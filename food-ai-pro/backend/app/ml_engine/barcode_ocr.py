import cv2
import numpy as np
from pyzbar.pyzbar import decode
import easyocr
import re

class BarcodeOCREngine:
    def __init__(self):
        # We load EasyOCR for text extraction fallback
        self.reader = easyocr.Reader(['en', 'pt'], gpu=False)

    def scan_barcode(self, image_bgr: np.ndarray) -> str:
        """
        Scans an image for a barcode and returns the EAN-13 string.
        Returns None if no barcode is found.
        """
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        barcodes = decode(gray)

        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            # Check if it looks like an EAN-13 or similar product code
            if len(barcode_data) >= 8 and barcode_data.isdigit():
                return barcode_data

        return None

    def scan_nutrition_label(self, image_bgr: np.ndarray) -> dict:
        """
        Fallback OCR for reading nutritional labels directly.
        Returns a dict of parsed macros if found.
        """
        result = self.reader.readtext(image_bgr)
        text_lines = [res[1].lower() for res in result]
        full_text = " ".join(text_lines)

        # Extremely basic regex-based extraction for demonstration
        # Real-world needs much more robust parsing
        macros = {
            "kcal_100g": 0.0,
            "protein_100g": 0.0,
            "carbs_100g": 0.0,
            "fat_100g": 0.0
        }

        kcal_match = re.search(r'(\d+[\.,]?\d*)\s*(kcal|calories)', full_text)
        if kcal_match:
            macros["kcal_100g"] = float(kcal_match.group(1).replace(',', '.'))

        protein_match = re.search(r'protein[a-z]*\s*(\d+[\.,]?\d*)\s*g', full_text)
        if protein_match:
            macros["protein_100g"] = float(protein_match.group(1).replace(',', '.'))

        carbs_match = re.search(r'carb[a-z]*\s*(\d+[\.,]?\d*)\s*g', full_text)
        if carbs_match:
            macros["carbs_100g"] = float(carbs_match.group(1).replace(',', '.'))

        fat_match = re.search(r'(fat|gordura)[a-z]*\s*(\d+[\.,]?\d*)\s*g', full_text)
        if fat_match:
            macros["fat_100g"] = float(fat_match.group(2).replace(',', '.'))

        return macros
