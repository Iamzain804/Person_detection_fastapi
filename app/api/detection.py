from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
from app.services.model_service import model_service
from app.core.security import get_api_key
from app.core.exceptions import CorruptedImageException
from app.utils.logger import logger
from PIL import Image
import io
import asyncio
from pydantic import BaseModel
from typing import List

router = APIRouter()

class Detection(BaseModel):
    label: str
    confidence: float
    box: List[float]

class DetectionResponse(BaseModel):
    count: int
    detections: List[Detection]
    inference_time: float

@router.post("/detect", response_model=DetectionResponse)
async def detect_persons(
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
):
    logger.info(f"Received detection request for file: {file.filename}")
    
    try:
        # Read file content
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
    except Exception as e:
        logger.error(f"Failed to open image: {str(e)}")
        raise CorruptedImageException()

    # Offload the synchronous YOLO prediction to a separate thread
    # to avoid blocking the event loop for 1000+ requests.
    loop = asyncio.get_event_loop()
    
    try:
        # YOLOv8 predict expects a PIL image or numpy array
        results = await loop.run_in_executor(None, model_service.predict, image)
    except Exception as e:
        logger.error(f"Inference error: {str(e)}")
        raise Exception("Inference failed")

    detections = []
    # results is a list because we might pass multiple images, but here it's one
    for result in results:
        boxes = result.boxes
        for box in boxes:
            # box.xyxy[0] returns [x1, y1, x2, y2]
            detections.append(Detection(
                label="person",
                confidence=float(box.conf[0]),
                box=[float(x) for x in box.xyxy[0]]
            ))

    response = DetectionResponse(
        count=len(detections),
        detections=detections,
        inference_time=results[0].speed['inference'] / 1000.0  # Convert ms to s
    )
    
    logger.info(f"Detection complete: {len(detections)} persons found.")
    return response
