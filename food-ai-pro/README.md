# Food AI Pro

A full-stack, zero-API 3D food volume & calorie AI application.

This application uses open-weight local AI models to estimate food volume in 3D using computer vision, calculate mass using volumetric density, and provide accurate macronutrients without relying on external or paid APIs.

## Architecture

- **Backend:** FastAPI, SQLite + FTS5, Ultralytics YOLOv11-seg, Depth-Anything-V2, Local VLM (Moondream2 / Qwen2.5-VL), Pyzbar + EasyOCR.
- **Mobile:** React Native (Expo), Zustand, AsyncStorage, Axios.
