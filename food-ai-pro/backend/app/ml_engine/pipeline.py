import cv2
import numpy as np
from PIL import Image

from .segmentation import SegmentationEngine
from .depth_volume import DepthVolumeEngine
from .vlm_classifier import VLMClassifierEngine
from ..database.db import fuzzy_search_food

class Pipeline:
    def __init__(self):
        # We initialize all models lazily or upfront. Upfront is better for API performance.
        self.seg_engine = SegmentationEngine()
        self.depth_engine = DepthVolumeEngine()
        self.vlm_engine = VLMClassifierEngine()

    def process_meal_image(self, image_bgr: np.ndarray, plate_diameter_cm: float):
        """
        Orchestrates the entire vision to nutrition pipeline.
        """
        # 1. Segmentation
        items = self.seg_engine.process_image(image_bgr)

        # 2. Depth Map
        # Depth engine expects PIL Image
        img_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(img_rgb)
        depth_map = self.depth_engine.compute_depth_map(pil_image)

        # 3. Volume Calculation
        items = self.depth_engine.calculate_volumes(items, depth_map, plate_diameter_cm)

        # 4. Classification & Nutrition Mapping
        results = []
        for item in items:
            if item.get('is_reference', False):
                continue

            # Crop image for VLM
            x1, y1, x2, y2 = [int(v) for v in item['box']]
            # Add padding
            pad = 20
            h, w = img_rgb.shape[:2]
            x1 = max(0, x1 - pad)
            y1 = max(0, y1 - pad)
            x2 = min(w, x2 + pad)
            y2 = min(h, y2 + pad)

            crop = img_rgb[y1:y2, x1:x2]
            crop_pil = Image.fromarray(crop)

            # VLM Classification
            vlm_res = self.vlm_engine.classify_food(crop_pil)

            # DB Matching
            query = f"{vlm_res['food_type']}"
            db_matches = fuzzy_search_food(query, limit=1)

            if db_matches:
                food_db = db_matches[0]

                # Calculate macros based on volume
                volume_cm3 = item['volume_cm3']
                density = food_db['density_g_cm3']
                weight_g = volume_cm3 * density

                multiplier = weight_g / 100.0

                # Hidden calories adjustments based on VLM
                added_kcal = 0
                added_fat = 0
                if vlm_res['visible_sauces']:
                    added_kcal += 90  # roughly 1 tbsp oil/sauce
                    added_fat += 10

                if vlm_res['cooking_method'] == 'fried' and food_db['cooking_method'] != 'fried':
                    # If VLM says fried but DB base item isn't
                    added_kcal += 120
                    added_fat += 13

                result_item = {
                    "box": item['box'],
                    "polygon_mask": self._mask_to_polygon(item['mask']),
                    "food_name": food_db['name_pt'],
                    "food_slug": food_db['slug'],
                    "volume_cm3": round(volume_cm3, 2),
                    "weight_g": round(weight_g, 2),
                    "macros": {
                        "kcal": round((food_db['kcal_100g'] * multiplier) + added_kcal, 1),
                        "protein": round(food_db['protein_100g'] * multiplier, 1),
                        "carbs": round(food_db['carbs_100g'] * multiplier, 1),
                        "fat": round((food_db['fat_100g'] * multiplier) + added_fat, 1)
                    }
                }
                results.append(result_item)
            else:
                # Unknown fallback
                results.append({
                    "box": item['box'],
                    "polygon_mask": self._mask_to_polygon(item['mask']),
                    "food_name": vlm_res['food_type'],
                    "food_slug": "unknown",
                    "volume_cm3": round(item['volume_cm3'], 2),
                    "weight_g": 0,
                    "macros": {"kcal": 0, "protein": 0, "carbs": 0, "fat": 0}
                })

        return results

    def _mask_to_polygon(self, mask: np.ndarray) -> list:
        # Convert boolean mask to list of (x,y) points for the UI
        mask_uint8 = (mask * 255).astype(np.uint8)
        contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return []

        # Take largest contour
        largest = max(contours, key=cv2.contourArea)
        # Simplify contour
        epsilon = 0.005 * cv2.arcLength(largest, True)
        approx = cv2.approxPolyDP(largest, epsilon, True)

        return [{"x": float(pt[0][0]), "y": float(pt[0][1])} for pt in approx]

pipeline_instance = Pipeline()
