import torch
import numpy as np
import cv2
from transformers import pipeline
from PIL import Image
from ..config import settings

class DepthVolumeEngine:
    def __init__(self):
        # We load the Depth-Anything-V2-Small model
        self.depth_estimator = pipeline(
            task="depth-estimation",
            model=settings.DEPTH_MODEL_ID,
            device=settings.DEVICE
        )

    def compute_depth_map(self, image: Image.Image) -> np.ndarray:
        """
        Generates a normalized inverse depth map from [0, 1].
        """
        prediction = self.depth_estimator(image)
        # prediction['depth'] is a PIL Image
        depth_map = np.array(prediction['depth'], dtype=np.float32)

        # Normalize to [0, 1]
        depth_min, depth_max = depth_map.min(), depth_map.max()
        if depth_max > depth_min:
            depth_map = (depth_map - depth_min) / (depth_max - depth_min)
        else:
            depth_map = np.zeros_like(depth_map)

        return depth_map

    def calculate_volumes(self, items, depth_map: np.ndarray, plate_diameter_cm: float = settings.DEFAULT_PLATE_DIAMETER_CM):
        """
        Calculates the real volume in cm^3 for each food item.
        """
        # Find the plate mask to use for calibration
        plate_mask = None
        plate_box = None
        for item in items:
            if item.get('class_name', '').startswith('plate') or item.get('class_name') == 'bowl':
                plate_mask = item['mask']
                plate_box = item['box']
                break

        h, w = depth_map.shape
        img_area = h * w

        # Check for single large item (close-up)
        close_up_detected = False
        if plate_mask is None or plate_box is None:
            if len(items) == 1 and not items[0].get('is_reference', False):
                item_mask = items[0]['mask']
                item_area = np.count_nonzero(item_mask)
                if item_area / img_area > 0.4: # Item fills > 40% of image
                    close_up_detected = True

        if close_up_detected:
            # We don't have a plate, and it's a close up. We will signal this to pipeline.py.
            px_per_cm = min(h, w) / 26.0 # Dummy value, will be overridden
            z_base = np.percentile(depth_map, 15)
            for item in items:
                item['is_close_up'] = True
        elif plate_mask is None or plate_box is None:
            # Fallback if no plate detected: assume center crop scale
            px_per_cm = min(h, w) / plate_diameter_cm
            z_base = np.percentile(depth_map, 15)
        else:
            # Scale calibration using plate width in pixels
            x1, y1, x2, y2 = plate_box
            w_px = max(x2 - x1, y2 - y1)  # use max dimension as diameter
            px_per_cm = w_px / plate_diameter_cm

            # Plane Fitting: estimate base elevation using inner boundary of plate mask
            # For simplicity, taking the 15th percentile of depth values within the plate mask
            plate_depths = depth_map[plate_mask]
            if len(plate_depths) > 0:
                z_base = np.percentile(plate_depths, 15)
            else:
                z_base = np.percentile(depth_map, 15)

        # cm per pixel
        cm_per_px = 1.0 / px_per_cm

        # Volume Integration
        for item in items:
            if item.get('is_reference', False):
                item['volume_cm3'] = 0.0
                continue

            mask = item['mask']

            # Get depths for the food mask
            food_depths = depth_map[mask]

            if len(food_depths) == 0:
                item['volume_cm3'] = 0.0
                continue

            # Depth difference relative to base.
            # Note: Depth models often output inverse depth (closer is higher value or vice versa).
            # Assuming depth_map has higher values for closer objects (typical for relative depth models normalized to [0,1]):
            # The physical height above the plate is proportional to (depth - z_base).
            # This requires scaling to real-world units.
            # We assume a linear mapping where a change in depth value maps to cm.
            # Calibration factor: a heuristic mapping, since monocular relative depth is unscaled.
            # We'll use cm_per_px as a rough scaling factor for Z as well (assuming roughly isometric voxels).

            delta_z = np.maximum(food_depths - z_base, 0)

            # Convert depth delta to physical height in cm (heuristic scale factor 50.0 for normalized map)
            heights_cm = delta_z * (cm_per_px * 50.0)

            # Area of one pixel in cm^2
            area_cm2 = cm_per_px * cm_per_px

            # Volume is the integral of heights over the mask area
            volume = np.sum(heights_cm * area_cm2)

            item['volume_cm3'] = float(volume)

        return items
