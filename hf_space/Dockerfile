# Use lightweight Python 3.9 image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HOME=/home/user
ENV PATH="/home/user/.local/bin:${PATH}"

# Install system dependencies for OpenCV and YOLO
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user with UID 1000
RUN useradd -m -u 1000 user

# Set work directory
WORKDIR $HOME/app

# Copy requirements and install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application
COPY --chown=user . .

# Ensure correct permissions for the app directory
RUN chmod -R 777 $HOME/app

# Switch to non-root user
USER user

# Hugging Face Spaces expect the app to listen on port 7860
EXPOSE 7860

# Run the application with Gunicorn and UvicornWorker
# Workers set to 4 as requested for optimal performance on HF free tier
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:7860", "--workers", "4", "--timeout", "120", "main:app"]
