import os
import torch
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Device configuration
    DEVICE: str = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")

    # Model paths
    YOLO_MODEL_PATH: str = "yolo11n-seg.pt"
    DEPTH_MODEL_ID: str = "depth-anything/Depth-Anything-V2-Small-hf"
    VLM_MODEL_ID: str = "vikhyatk/moondream2"

    # Default plate calibration (diameter in cm)
    DEFAULT_PLATE_DIAMETER_CM: float = 26.0

    class Config:
        env_file = ".env"

settings = Settings()
