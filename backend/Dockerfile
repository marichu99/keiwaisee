FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    wget \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxss1 \
    libgtk-3-0 \
    libasound2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxrandr2 \
    libgbm-dev \
    libpango-1.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libxkbcommon0 \
    xdg-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    wget curl gnupg build-essential \
    libasound2 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 \
    libnspr4 libnss3 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxrandr2 libgbm1 libgtk-3-0 \
    libxshmfence1 libxss1 libxext6 libxfixes3 \
    libdrm2 libgl1 libxkbcommon0 xdg-utils \
    libglib2.0-0 libpango-1.0-0 libpangocairo-1.0-0 \
    xvfb libnss3 libxss1 libasound2 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libdbus-1-3 libx11-xcb1 \
    libgstreamer1.0-0 libgstreamer-plugins-base1.0-0 \
    libwebpdemux2 libenchant-2-2 libvpx7 libopus0 \
    libevent-2.1-7 libxslt1.1 libwoff1 \
    libsecret-1-0 libharfbuzz-icu0 libmanette-0.2-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


# Set workdir
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install

# Copy the rest of the app
COPY . .

# Expose port
EXPOSE 5000

# Run app
CMD ["python", "app.py"]
