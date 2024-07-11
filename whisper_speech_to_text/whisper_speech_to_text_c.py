import torch
import torchaudio
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq


def transcribe_czech_audio(audio_file_path, segment_length=30):
    """
    Finetuned model for transcribing Czech audio
    """
    # Load the processor and the model
    processor = AutoProcessor.from_pretrained("Cem13/whisper-large-v3-czech")
    model = AutoModelForSpeechSeq2Seq.from_pretrained("Cem13/whisper-large-v3-czech")

    # Load and preprocess the audio file
    try:
        waveform, sample_rate = torchaudio.load(audio_file_path)
        print(f"Loaded audio file: {audio_file_path}")
    except FileNotFoundError:
        print(f"Error: Audio file '{audio_file_path}' not found.")
        return None

    # Convert to mono if necessary
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)
        print("Converted audio to mono")

    # Resample if sample rate doesn't match model's expectation
    expected_sample_rate = processor.feature_extractor.sampling_rate
    if sample_rate != expected_sample_rate:
        waveform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=expected_sample_rate)(waveform)
        print(f"Resampled audio from {sample_rate}Hz to {expected_sample_rate}Hz")

    # Calculate the number of segments
    total_length = waveform.shape[1] / expected_sample_rate
    num_segments = int(total_length // segment_length) + 1
    print(f"Total length of audio: {total_length:.2f}s, Number of segments: {num_segments}")

    transcriptions = []

    # Process each segment
    for i in range(num_segments):
        start_time = i * segment_length
        end_time = min((i + 1) * segment_length, total_length)

        start_sample = int(start_time * expected_sample_rate)
        end_sample = int(end_time * expected_sample_rate)

        segment_waveform = waveform[:, start_sample:end_sample]

        # Process the audio to get the input features
        inputs = processor(segment_waveform.squeeze(0), sampling_rate=expected_sample_rate, return_tensors="pt")

        # Generate the transcription
        with torch.no_grad():
            generated_ids = model.generate(inputs["input_features"], max_length=1000)  # Adjust max_length if needed

        # Decode the transcription
        transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)
        transcriptions.append(transcription[0])
        print(f"Segment {i + 1}/{num_segments} transcribed")

        # Clear memory
        del inputs, segment_waveform, generated_ids
        torch.cuda.empty_cache()

    # Combine all segments
    full_transcription = " ".join(transcriptions)
    print("Full transcription completed")
    if "Titulky vytvořil JohnyX." in full_transcription:
        full_transcription = full_transcription.replace(" Titulky vytvořil JohnyX.", '', 1)
    return full_transcription


def transcribe_english_audio(audio_file_path,segment_length=30):
    """
    nonfinetuned base model for transcribing english audio
    """

    # Load the processor and the model (ensure these names are correct)
    processor = AutoProcessor.from_pretrained("openai/whisper-large-v3")
    model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-large-v3")
    # Load and preprocess the audio file
    try:
        waveform, sample_rate = torchaudio.load(audio_file_path)
    except FileNotFoundError:
        print(f"Error: Audio file '{audio_file_path}' not found.")
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
        inputs = processor(segment_waveform.squeeze(0), sampling_rate=expected_sample_rate, return_tensors="pt")

        # Generate the transcription
        with torch.no_grad():
            generated_ids = model.generate(inputs["input_features"], max_length=1000)  # Adjust max_length if needed

        # Decode the transcription
        transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)
        transcriptions.append(transcription[0])

    # Combine all segments
    full_transcription = " ".join(transcriptions)

    
    
    return full_transcription




# Example usage:
# full_text = transcribe_czech_audio("path/to/audio.wav", "path/to/output.txt")
