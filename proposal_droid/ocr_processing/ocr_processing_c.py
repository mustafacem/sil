import cv2
import numpy as np
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
#import pytesseract


import openai
import base64
import requests
import streamlit as st

from io import BytesIO


def extract_text_from_image(api_key, uploaded_file):
    """
    Translate image to base64 and then perform OCR on it.
    """
    # Function to encode the image
    def encode_image(file):
        return base64.b64encode(file.read()).decode('utf-8')

    # Convert PIL Image to BytesIO object if necessary
    if isinstance(uploaded_file, Image.Image):
        buffered = BytesIO()
        uploaded_file.save(buffered, format="JPEG")
        buffered.seek(0)
        base64_image = encode_image(buffered)
    else:
        base64_image = encode_image(uploaded_file)

    # Define headers and payload for the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "you are given a handwritten text image which you are tasked to convert to text, just provide the text nothing else no explanation"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    # Make the API request
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    # Extract and return the text from the response
    if response.status_code == 200:
        response_data = response.json()
        if "choices" in response_data:
            return response_data["choices"][0]["message"]["content"]
        else:
            return "Error: Unexpected response format."
    else:
        return f"Error: {response.status_code} - {response.text}"


def preprocess_handwritten_image(uploaded_file):
    """
    Preprocess the uploaded handwritten image file for OCR and return the preprocessed image.
    """
    # Load the image from the uploaded file
    image = Image.open(uploaded_file).convert('L')
    image_np = np.array(image)

    # Check if the image is loaded properly
    if image_np is None:
        st.error("Error: Unable to load image.")
        return None

    # Step 1: Noise reduction
    denoised_image = cv2.medianBlur(image_np, 1)

    # Step 2: Binarization
    _, binary_image = cv2.threshold(denoised_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Convert the binary image back to PIL Image format for OCR
    preprocessed_image = Image.fromarray(binary_image)

    return preprocessed_image


def load_model_and_predict(image_path):
    """
    ocr via MS handrwritting model
    """
    try:
        # Load the processor and model
        processor = TrOCRProcessor.from_pretrained("microsoft/trocr-large-handwritten")
        model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-large-handwritten")

        # Open the image
        image = Image.open(image_path).convert("RGB")  # Ensure the image has 3 channels (RGB)

        # Preprocess the image
        pixel_values = processor(images=image, return_tensors="pt").pixel_values

        # Generate text predictions
        generated_ids = model.generate(pixel_values)
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return generated_text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


