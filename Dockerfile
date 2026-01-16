# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY .env .

# Expose port (Railway will set PORT env variable)
EXPOSE 8000

# Run the application
# Railway sets PORT env variable, default to 8000
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}