# Build Stage
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

# Install system dependencies for OpenCV and YOLO
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create logs directory and set permissions for SQLite
RUN mkdir -p /app/logs && chmod -R 777 /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Ensure the database file can be created/written
RUN touch /app/sql_app.db && chmod 777 /app/sql_app.db

# Hugging Face Spaces port is 7860
EXPOSE 7860

# Command to run the application
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:7860", "app.main:app"]
