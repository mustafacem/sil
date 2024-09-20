import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from urllib.parse import urlparse
import yt_dlp
import torchaudio
import torch
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
import os

def is_valid_url(url):
    """
    Validates if the provided string is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)

def fetch_html(url):
    """
    Sends a GET request to the given URL and returns the raw HTML content.
    Raises an exception if the request fails.
    """
    try:
        # Send the HTTP request
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)
        return response.text  # Return the HTML content
    except RequestException as e:
        # Handle network-related errors, invalid URL, etc.
        print(f"Error fetching URL: {e}")
        return None

def parse_html(html_content):
    """
    Parses the raw HTML content using BeautifulSoup and extracts text.
    This method removes script and style content and returns only visible text.
    """
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style elements (which don't contain useful text)
    for script_or_style in soup(['script', 'style']):
        script_or_style.extract()

    # Extract visible text
    text = soup.get_text(separator=' ', strip=True)

    # Return the clean text
    return text

def extract_text_from_url(url):
    """
    Main function that validates the URL, fetches its content,
    and extracts the visible text.
    """
    if not is_valid_url(url):
        return "Invalid URL provided."

    # Fetch the HTML content
    html_content = fetch_html(url)
    if html_content is None:
        return "Failed to retrieve content from the URL."

    # Parse and extract the text
    page_text = parse_html(html_content)
    return page_text


def transcribe_english_youtube(youtube_url, segment_length=30):
    """
    Downloads audio from a YouTube video using yt-dlp and transcribes it using the Whisper model.
    """
    # Download the audio from YouTube using yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(title)s.%(ext)s',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        audio_file_path = ydl.prepare_filename(info_dict).replace(".webm", ".mp3")  # Adjust if needed

    # Load the processor and model
    processor = AutoProcessor.from_pretrained("openai/whisper-medium")
    model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-medium")

    # Load and preprocess the audio file using the soundfile backend
    try:
        waveform, sample_rate = torchaudio.load(audio_file_path, backend='soundfile')
    except FileNotFoundError:
        print(f"Error: Audio file '{audio_file_path}' not found.")
        return None
    except RuntimeError as e:
        print(f"Runtime Error: {e}")
        return None

    # Convert to mono if necessary
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)

    # Resample if sample rate doesn't match model's expectation
    expected_sample_rate = processor.feature_extractor.sampling_rate
    if sample_rate != expected_sample_rate:
        waveform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=expected_sample_rate)(waveform)

    # Calculate the number of segments
    total_length = waveform.shape[1] / expected_sample_rate
    num_segments = int(total_length // segment_length) + 1

    transcriptions = []

    # Process each segment
    for i in range(num_segments):
        start_time = i * segment_length
        end_time = min((i + 1) * segment_length, total_length)

        start_sample = int(start_time * expected_sample_rate)
        end_sample = int(end_time * expected_sample_rate)

        segment_waveform = waveform[:, start_sample:end_sample]

        # Process the audio to get the input features
        inputs = processor(segment_waveform.squeeze(0), sampling_rate=expected_sample_rate, return_tensors="pt", language="en")

        # Generate the transcription
        with torch.no_grad():
            generated_ids = model.generate(inputs["input_features"], max_length=1000)

        # Decode the transcription
        transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)
        transcriptions.append(transcription[0])

    # Combine all segments
    full_transcription = " ".join(transcriptions)

    # Clean up the downloaded file
    os.remove(audio_file_path)

    return full_transcription


