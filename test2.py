from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import requests
import torch

import pytesseract

from chat_gpt.chat_gpt_c import *


def clear_transformers_cache():
    from pathlib import Path
    import shutil

    cache_dir = Path.home() / ".cache" / "huggingface" / "transformers"
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
        print("Transformers cache cleared.")
    else:
        print("Transformers cache is already clear.")

# Clear the cache


def load_model_and_predict(image_path):
    """
    OCR via MS handwritten model
    """
    try:
        # Load the processor and model
        print("Loading the processor and model...")
        processor = TrOCRProcessor.from_pretrained("Riksarkivet/trocr-base-handwritten-swe")
        model = VisionEncoderDecoderModel.from_pretrained("Riksarkivet/trocr-base-handwritten-swe")

        # Check if CUDA is available and use it if possible
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        print(f"Using device: {device}")

        # Open the image
        print("Opening the image...")
        image = Image.open(image_path).convert("RGB")  # Ensure the image has 3 channels (RGB)

        # Preprocess the image
        print("Preprocessing the image...")
        pixel_values = processor(images=image, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(device)

        # Generate text predictions
        print("Generating text predictions...")
        generated_ids = model.generate(pixel_values, max_length=50)  # Adjust max_length as needed
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        print("Prediction completed.")
        return generated_text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def tes_ext(path):
    """
    Perform OCR on an image at the given path using Tesseract with custom configuration.

    Args:
    path (str): Path to the image file.

    Returns:
    str: The transcribed text from the image.
    """
    custom_config = r'--oem 3 --psm 6'
    image = Image.open(path)
    raw_text_4 = pytesseract.image_to_string(image, config=custom_config)
    return raw_text_4



# Example usage with image URL
image_url = 'converted_image.png'
predicted_text = tes_ext(image_url)
#predicted_text = decoder(predicted_text,)
print(predicted_text)
