FROM python:3.11-alpine

# Install required packages including build dependencies
RUN apk add --no-cache \
    curl \
    jq \
    dumb-init \
    gcc \
    musl-dev \
    python3-dev \
    linux-headers

# Create non-root user
RUN addgroup -g 1001 -S appuser && \
    adduser -S appuser -u 1001

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

USER appuser

# Use dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]

# Start the resource manager
CMD ["python", "src/main.py"] 