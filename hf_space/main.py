import os
import io
import time
import asyncio
import logging
import threading
import torch
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Security, HTTPException, Request, status, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from PIL import Image
from ultralytics import YOLO
from starlette.middleware.base import BaseHTTPMiddleware

# --- Senior Architect Global Patch for PyTorch 2.6+ ---
original_torch_load = torch.load
def patched_torch_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return original_torch_load(*args, **kwargs)
torch.load = patched_torch_load
# -----------------------------------------------------

# --- Configuration & Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("hf_person_detection")

HF_API_KEY = os.getenv("HF_API_KEY", "default-secret-key")
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# --- Pydantic Models ---
class Detection(BaseModel):
    label: str
    confidence: float
    box: List[float]

class DetectionResponse(BaseModel):
    count: int
    detections: List[Detection]
    inference_time_ms: float

# --- Custom Exceptions ---
class AppError(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code

# --- Singleton Model Service ---
class ModelService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ModelService, cls).__new__(cls)
                cls._instance._model = None
        return cls._instance

    def load_model(self):
        if self._model is None:
            logger.info("Loading YOLOv8 model...")
            self._model = YOLO("yolov8n.pt")
            logger.info("Model loaded successfully.")
        return self._model

    def predict(self, image):
        return self._model.predict(image, classes=[0], verbose=False)

model_service = ModelService()

# --- Middleware ---
class InferenceTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time_ms = (time.time() - start_time) * 1000
        response.headers["X-Inference-Time-Ms"] = f"{process_time_ms:.2f}"
        logger.info(f"Path: {request.url.path} | Duration: {process_time_ms:.2f}ms")
        return response

# --- FastAPI App ---
app = FastAPI(title="Synavos Person Detection API")
app.add_middleware(InferenceTimeMiddleware)

# --- Auth Dependency ---
async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == HF_API_KEY:
        return api_key_header
    raise AppError("Unauthorized Access: Invalid API Key", status.HTTP_401_UNAUTHORIZED)

# --- Global Exception Handlers ---
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "status": "failed"}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Internal Error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "An unexpected error occurred", "status": "failed"}
    )

# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    model_service.load_model()

# --- Endpoints ---
@app.get("/")
async def root():
    return {"message": "Person Detection API is running on Hugging Face Spaces"}

@app.post("/detect", response_model=DetectionResponse)
async def detect(
    file: UploadFile = File(...),
    api_key: str = Security(get_api_key)
):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
    except Exception:
        raise AppError("Invalid Image: Could not decode upload", status.HTTP_400_BAD_REQUEST)

    loop = asyncio.get_event_loop()
    try:
        results = await loop.run_in_executor(None, model_service.predict, image)
    except asyncio.TimeoutError:
        raise AppError("Inference Timeout: Model took too long", status.HTTP_504_GATEWAY_TIMEOUT)
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        raise AppError("Inference Error: Processing failed", status.HTTP_500_INTERNAL_SERVER_ERROR)

    detections = []
    for result in results:
        for box in result.boxes:
            detections.append(Detection(
                label="person",
                confidence=float(box.conf[0]),
                box=[float(x) for x in box.xyxy[0]]
            ))

    return DetectionResponse(
        count=len(detections),
        detections=detections,
        inference_time_ms=results[0].speed['inference']
    )
