from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.detection import router as detection_router
from app.middleware.monitoring import PerformanceMiddleware
from app.services.model_service import model_service
from app.core.exceptions import PersonDetectionException
from app.core.config import get_settings
from app.utils.logger import logger

settings = get_settings()

app = FastAPI(title=settings.PROJECT_NAME)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development ke liye sab allow kar rahe hain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add performance middleware
app.add_middleware(PerformanceMiddleware)

# Exception Handler
@app.exception_handler(PersonDetectionException)
async def custom_exception_handler(request: Request, exc: PersonDetectionException):
    logger.warning(f"Custom Exception: {exc.message} at {request.url.path}")
    return JSONResponse(
        status_code=exc.code,
        content={"error": exc.message, "status": "failed"}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "An internal server error occurred", "status": "failed"}
    )

# Startup Event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Person Detection API...")
    # Pre-load the model to the Singleton
    model_service.load_model()
    logger.info("API is ready to serve requests.")

# Include Routes
app.include_router(detection_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to Person Detection API", "status": "running"}
