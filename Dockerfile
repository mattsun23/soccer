# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code - Updated 2026-01-20 to use sunheart.tech domain
COPY main.py .

# Expose port (Railway will set PORT env variable)
EXPOSE 8000

# Run the application with explicit port binding
# Use shell form to ensure PORT variable is expanded
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]