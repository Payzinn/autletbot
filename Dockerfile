FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY .env .

COPY app ./app

RUN mkdir -p /app/qrcodes

CMD ["python3", "-u", "main.py"]