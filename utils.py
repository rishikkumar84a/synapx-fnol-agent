import pytesseract
from PIL import Image
import os

def load_image(image_path):
    """Loads an image from a path."""
    try:
        return Image.open(image_path)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

def run_ocr(images):
    """
    Runs OCR on a list of PIL Image objects and returns the combined text.
    Handles multiple pages by concatenating text with page markers.
    """
    full_text = ""
    for i, img in enumerate(images):
        try:
            # Assuming standard tesseract installation. 
            # In some envs, pytesseract.pytesseract.tesseract_cmd needs to be set.
            text = pytesseract.image_to_string(img)
            full_text += f"\n--- PAGE {i+1} ---\n"
            full_text += text
        except Exception as e:
            print(f"Error running OCR on page {i+1}: {e}")
    return full_text
