import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
from ..config import settings

class SegmentationEngine:
    def __init__(self):
        # We load YOLO with the specified segment model
        self.model = YOLO(settings.YOLO_MODEL_PATH)
        # Force model to target device
        self.model.to(settings.DEVICE)

    def process_image(self, image_bgr: np.ndarray):
        """
        Runs YOLO11n-seg on the image and extracts masks and bounding boxes.
        Falls back to OpenCV Hough Circles for the plate if not detected by YOLO.
        Returns:
            list of dicts containing:
            - mask: boolean numpy array of the mask
            - box: [x1, y1, x2, y2]
            - class_id: integer id from yolo
            - class_name: string label from yolo
        """
        results = self.model(image_bgr, verbose=False)
        result = results[0]

        detected_items = []
        has_plate = False

        if result.masks is not None:
            # result.masks.data is shape (N, H, W)
            # Resize masks to original image shape if necessary
            masks = result.masks.data.cpu().numpy()
            boxes = result.boxes.xyxy.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy().astype(int)
            names = result.names

            # Match mask size to original image
            orig_h, orig_w = image_bgr.shape[:2]

            for i in range(len(masks)):
                # Ultralytics masks might be downscaled, resize them back to image dimensions
                mask_resized = cv2.resize(masks[i], (orig_w, orig_h), interpolation=cv2.INTER_NEAREST)
                bool_mask = mask_resized > 0.5

                class_name = names[class_ids[i]]
                if class_name in ['bowl', 'plate', 'dining table']:
                    has_plate = True

                detected_items.append({
                    "mask": bool_mask,
                    "box": boxes[i].tolist(),
                    "class_id": int(class_ids[i]),
                    "class_name": class_name,
                    "is_reference": class_name in ['bowl', 'plate', 'dining table', 'fork', 'spoon', 'knife', 'cup']
                })

        if not has_plate:
            # Fallback: OpenCV Hough Circles to detect the plate
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            gray_blurred = cv2.medianBlur(gray, 5)

            # Parameters need tuning based on expected image size and lighting
            rows = gray_blurred.shape[0]
            circles = cv2.HoughCircles(
                gray_blurred,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=rows/8,
                param1=100,
                param2=30,
                minRadius=int(rows/10),
                maxRadius=int(rows/2)
            )

            if circles is not None:
                circles = np.uint16(np.around(circles))
                # Take the most prominent circle
                c = circles[0, 0]
                center_x, center_y, radius = c[0], c[1], c[2]

                # Create a mask for the plate
                plate_mask = np.zeros(image_bgr.shape[:2], dtype=np.uint8)
                cv2.circle(plate_mask, (center_x, center_y), radius, 1, thickness=-1)

                # Bounding box
                x1 = max(0, center_x - radius)
                y1 = max(0, center_y - radius)
                x2 = min(image_bgr.shape[1], center_x + radius)
                y2 = min(image_bgr.shape[0], center_y + radius)

                detected_items.append({
                    "mask": plate_mask.astype(bool),
                    "box": [float(x1), float(y1), float(x2), float(y2)],
                    "class_id": -1,
                    "class_name": "plate (fallback)",
                    "is_reference": True
                })

        return detected_items
