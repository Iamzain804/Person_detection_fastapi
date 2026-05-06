# Person Detection API (Production-Grade)

A high-performance, scalable API for person detection using FastAPI and YOLOv8.

## Key Features
- **Singleton Model Loading**: Efficient memory usage by loading YOLOv8 once.
- **Async Processing**: Handles high concurrency using `run_in_executor` for CPU-bound tasks.
- **Advanced Logging**: Rotating file logs for tracking and debugging.
- **Performance Monitoring**: Returns `X-Inference-Time` in response headers.
- **Production-Ready**: Configured for Gunicorn with Uvicorn workers.

## Project Structure
```text
person_detection_api/
├── app/
│   ├── main.py                # FastAPI Application
│   ├── core/                  # Config, Security, Exceptions
│   ├── api/                   # Endpoint definitions
│   ├── services/              # Model Singleton & Logic
│   ├── middleware/            # Monitoring Middleware
│   └── utils/                 # Logging & Helpers
├── logs/                      # Log Storage
├── gunicorn_conf.py           # Deployment Config
└── requirements.txt           # Dependencies
```

## Setup & Running

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file or modify the existing one:
- `API_KEY`: Security key for authentication.
- `MODEL_PATH`: Path to YOLOv8 weights (e.g., `yolov8n.pt`).

### 3. Run Locally (Development)
```bash
uvicorn app.main:app --reload
```

### 4. Run in Production
```bash
gunicorn -c gunicorn_conf.py app.main:app
```

## API Usage
### Detect Persons
**Endpoint**: `POST /api/v1/detect`  
**Headers**: `X-API-Key: your-super-secret-api-key`  
**Body**: `multipart/form-data` with `file` field.

**Response**:
```json
{
  "count": 2,
  "detections": [
    {
      "label": "person",
      "confidence": 0.95,
      "box": [10, 20, 100, 200]
    }
  ],
  "inference_time": 0.045
}
```
