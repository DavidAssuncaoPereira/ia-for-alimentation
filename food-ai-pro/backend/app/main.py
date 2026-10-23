import io
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .schemas import (
    AnalysisResponse, AnalyzedFoodItem, Macros,
    RecalculateRequest, BarcodeScanResponse, FoodSearchResponseItem
)
from .database.seed_nutrition import seed
from .database.db import get_food_by_slug, fuzzy_search_food, get_connection
from .ml_engine.pipeline import pipeline_instance
from .ml_engine.barcode_ocr import BarcodeOCREngine
from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Seed the database if it doesn't exist or is empty
    seed()
    yield
    # Shutdown logic if any

app = FastAPI(title="Food AI Pro", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

barcode_engine = BarcodeOCREngine()

@app.post("/api/v1/analyze-meal", response_model=AnalysisResponse)
async def analyze_meal(
    image: UploadFile = File(...),
    plate_diameter_cm: float = Form(settings.DEFAULT_PLATE_DIAMETER_CM),
    user_notes: str = Form(None)
):
    try:
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img_bgr is None:
            raise HTTPException(status_code=400, detail="Invalid image format.")

        results = pipeline_instance.process_meal_image(img_bgr, plate_diameter_cm)

        total_macros = Macros(kcal=0, protein=0, carbs=0, fat=0)
        response_items = []

        for item in results:
            macros = Macros(**item['macros'])
            total_macros.kcal += macros.kcal
            total_macros.protein += macros.protein
            total_macros.carbs += macros.carbs
            total_macros.fat += macros.fat

            response_items.append(AnalyzedFoodItem(
                box=item['box'],
                polygon_mask=item['polygon_mask'],
                food_name=item['food_name'],
                food_slug=item['food_slug'],
                volume_cm3=item['volume_cm3'],
                weight_g=item['weight_g'],
                macros=macros
            ))

        return AnalysisResponse(items=response_items, totals=total_macros)

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/recalculate", response_model=AnalysisResponse)
async def recalculate_meal(request: RecalculateRequest):
    total_macros = Macros(kcal=0, protein=0, carbs=0, fat=0)
    response_items = []

    for item in request.items:
        food_db = get_food_by_slug(item.food_slug)
        if not food_db:
            continue

        multiplier = item.weight_g / 100.0

        macros = Macros(
            kcal=(food_db['kcal_100g'] * multiplier) + item.added_kcal,
            protein=food_db['protein_100g'] * multiplier,
            carbs=food_db['carbs_100g'] * multiplier,
            fat=(food_db['fat_100g'] * multiplier) + item.added_fat
        )

        total_macros.kcal += macros.kcal
        total_macros.protein += macros.protein
        total_macros.carbs += macros.carbs
        total_macros.fat += macros.fat

        response_items.append(AnalyzedFoodItem(
            box=[],  # Empty for recalculation
            polygon_mask=[],
            food_name=food_db['name_pt'],
            food_slug=food_db['slug'],
            volume_cm3=item.weight_g / food_db['density_g_cm3'],
            weight_g=item.weight_g,
            macros=macros
        ))

    return AnalysisResponse(items=response_items, totals=total_macros)

@app.post("/api/v1/scan-barcode", response_model=BarcodeScanResponse)
async def scan_barcode(
    ean13: str = Form(None),
    image: UploadFile = File(None)
):
    detected_ean = ean13

    if not detected_ean and image:
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_bgr is not None:
            detected_ean = barcode_engine.scan_barcode(img_bgr)

    if not detected_ean:
        raise HTTPException(status_code=400, detail="Barcode not found.")

    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM barcodes WHERE ean13 = ?', (detected_ean,))
    row = c.fetchone()
    conn.close()

    if row:
        return BarcodeScanResponse(
            ean13=row['ean13'],
            name=row['name'],
            serving_size_g=row['serving_size_g'],
            macros=Macros(
                kcal=row['kcal_100g'],
                protein=row['protein_100g'],
                carbs=row['carbs_100g'],
                fat=row['fat_100g']
            )
        )
    else:
        # Mocking an external lookup as fallback since external APIs are forbidden
        # In a real offline app, the user would be prompted to enter manually.
        raise HTTPException(status_code=404, detail="Barcode not found in local database. Please enter manually.")

@app.get("/api/v1/foods/search", response_model=list[FoodSearchResponseItem])
async def search_foods(q: str):
    if not q or len(q) < 2:
        return []

    results = fuzzy_search_food(q, limit=10)
    return [FoodSearchResponseItem(**res) for res in results]
