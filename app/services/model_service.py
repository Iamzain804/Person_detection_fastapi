import threading
import torch
from ultralytics import YOLO
from app.core.config import get_settings
from app.utils.logger import logger
import time

# --- Senior Architect Global Patch ---
# This monkey-patches torch.load to default weights_only=False
# This is the most robust way to fix the PyTorch 2.6+ breaking change for YOLO
original_torch_load = torch.load

def patched_torch_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return original_torch_load(*args, **kwargs)

torch.load = patched_torch_load
# -------------------------------------

settings = get_settings()

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
            logger.info(f"Loading YOLO model from {settings.MODEL_PATH}...")
            start_time = time.time()
            
            # Now this will use our patched torch.load internally
            self._model = YOLO(settings.MODEL_PATH)
            
            end_time = time.time()
            logger.info(f"Model loaded successfully in {end_time - start_time:.2f} seconds.")
        return self._model

    def predict(self, image):
        # We also disable verbose to keep logs clean
        results = self._model.predict(image, classes=[0], verbose=False)
        return results

model_service = ModelService()
