FROM python:3.13-slim

# 安裝 Playwright 需要的系統套件
RUN apt-get update && apt-get install -y \
    libnss3 libatk1.0-0 libx11-xcb1 libdrm2 libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安裝 Playwright Chromium
RUN python -m playwright install chromium

# 複製程式碼
COPY . .

# 啟動程式
CMD ["python", "main.py"]
