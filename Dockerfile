# Dockerfile for Auto YouTube AI Video Pipeline
# Builds a portable, cross-platform image for the pipeline

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/output /app/logs /app/cache /app/config /app/scripts && \
    mkdir -p /app/assets/dejavu-fonts-ttf-2.37/ttf && \
    chmod -R 755 /app

# Copy bundled fonts for cross-platform compatibility
COPY assets/dejavu-fonts-ttf-2.37/ttf/DejaVuSans.ttf /app/assets/dejavu-fonts-ttf-2.37/ttf/
COPY assets/dejavu-fonts-ttf-2.37/ttf/DejaVuSans-Bold.ttf /app/assets/dejavu-fonts-ttf-2.37/ttf/

# Copy the pipeline code
COPY scripts/ ./scripts/
COPY config/ ./config/
COPY assets/ ./assets/

# Expose port for debugging (optional)
EXPOSE 8080

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "scripts/pipeline.py", "--scheduler"]