FROM python:3.11-slim

# Install system dependencies for Playwright, WeasyPrint and general use
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    php-cli \
    curl \
    libmagic1 \
    file \
    # Playwright dependencies
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    # WeasyPrint dependencies
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (Chromium only for SEO Spider)
# Set PLAYWRIGHT_BROWSERS_PATH to /ms-playwright to match docker-compose
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN mkdir -p /ms-playwright && \
    playwright install chromium

# Copy application code
COPY . .

# Create workspace, backup and report directories
RUN mkdir -p /app/workspace /app/backups /app/workspace/reports /app/workspace/screenshots

# Create entrypoint script to ensure playwright browsers are available
RUN echo '#!/bin/sh\n\
mkdir -p /ms-playwright\n\
if [ ! -d "/ms-playwright/chromium-1091" ]; then\n\
    echo "Installing Playwright browsers..."\n\
    playwright install chromium\n\
fi\n\
exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

# Expose port
EXPOSE 8000

# Use entrypoint to ensure playwright is available
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

