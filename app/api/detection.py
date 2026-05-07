from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
from app.services.model_service import model_service
from app.core.security import get_api_key
from app.core.exceptions import CorruptedImageException
from app.utils.logger import logger
from app.core.database import get_db
from app.models.detection import DetectionRecord
from sqlalchemy.orm import Session
from PIL import Image
import io
import asyncio
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()

class Detection(BaseModel):
    label: str
    confidence: float
    box: List[float]

class DetectionResponse(BaseModel):
    count: int
    detections: List[Detection]
    inference_time: float

class HistoryRecord(BaseModel):
    id: int
    person_count: int
    max_confidence: float
    timestamp: datetime

    class Config:
        from_attributes = True

@router.post("/detect", response_model=DetectionResponse)
async def detect_persons(
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    logger.info(f"Received detection request for file: {file.filename}")
    
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
    except Exception as e:
        logger.error(f"Failed to open image: {str(e)}")
        raise CorruptedImageException()

    loop = asyncio.get_event_loop()
    
    try:
        results = await loop.run_in_executor(None, model_service.predict, image)
    except Exception as e:
        logger.error(f"Inference error: {str(e)}")
        raise Exception("Inference failed")

    detections = []
    max_conf = 0.0
    for result in results:
        boxes = result.boxes
        for box in boxes:
            conf = float(box.conf[0])
            if conf > max_conf:
                max_conf = conf
            
            detections.append(Detection(
                label="person",
                confidence=conf,
                box=[float(x) for x in box.xyxy[0]]
            ))

    # Save to Database
    try:
        new_record = DetectionRecord(
            person_count=len(detections),
            max_confidence=max_conf
        )
        db.add(new_record)
        db.commit()
    except Exception as e:
        logger.error(f"Database save error: {str(e)}")
        db.rollback()

    response = DetectionResponse(
        count=len(detections),
        detections=detections,
        inference_time=results[0].speed['inference'] / 1000.0
    )
    
    logger.info(f"Detection complete: {len(detections)} persons found. Saved to DB.")
    return response

@router.get("/history", response_model=List[HistoryRecord])
async def get_detection_history(
    limit: int = 10,
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """Fetches the latest detection records from the database."""
    records = db.query(DetectionRecord).order_by(DetectionRecord.timestamp.desc()).limit(limit).all()
    return records
