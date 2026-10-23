import sys
import os
import cv2
import numpy as np

# Add backend directory to sys.path to allow imports when running as a script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.seed_nutrition import seed
from app.ml_engine.pipeline import pipeline_instance

def generate_synthetic_plate():
    """Generates a synthetic plate image with a food item for testing."""
    img = np.ones((600, 800, 3), dtype=np.uint8) * 200  # Gray background

    # Draw a plate (white circle)
    cv2.circle(img, (400, 300), 200, (255, 255, 255), -1)

    # Draw a "food item" (e.g., a brown blob representing cooked meat)
    cv2.circle(img, (400, 300), 80, (42, 42, 165), -1)

    return img

def test_pipeline():
    print("Seeding database if necessary...")
    seed()

    print("Generating synthetic image...")
    img = generate_synthetic_plate()

    print("Running pipeline...")
    # This will initialize models which might take a bit of time and require internet to download weights the first time.
    results = pipeline_instance.process_meal_image(img, plate_diameter_cm=26.0)

    print("Results:")
    for item in results:
        print(f"Food: {item['food_name']} ({item['food_slug']})")
        print(f"Volume: {item['volume_cm3']} cm^3")
        print(f"Weight: {item['weight_g']} g")
        print(f"Macros: {item['macros']}")
        print("-" * 20)

        # Basic assertions
        assert item['volume_cm3'] > 0, f"Volume should be positive, got {item['volume_cm3']}"
        assert item['weight_g'] > 0, f"Weight should be positive, got {item['weight_g']}"
        assert 'kcal' in item['macros'], "Macros should contain kcal"

    print("Pipeline test completed successfully.")

if __name__ == "__main__":
    test_pipeline()
