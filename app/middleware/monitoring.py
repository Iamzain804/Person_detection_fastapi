import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import logger

class PerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Add the inference/process time to response headers
        response.headers["X-Inference-Time"] = f"{process_time:.4f}s"
        
        logger.info(f"Path: {request.url.path} | Time: {process_time:.4f}s | Status: {response.status_code}")
        
        return response
