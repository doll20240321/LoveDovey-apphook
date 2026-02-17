FROM python:3.13-slim
RUN apt-get update && apt-get install -y \
    libnss3 libatk1.0-0 libx11-xcb1 libdrm2 libgbm1
RUN pip install -r requirements.txt
RUN playwright install chromium
CMD ["python", "main.py"]
