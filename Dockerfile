FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ANONYMIZED_TELEMETRY=False
ENV TRANSFORMERS_NO_TF=1
ENV USE_TF=0
ENV USE_TORCH=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-docker.txt .

RUN pip install --upgrade pip setuptools wheel


RUN pip install --index-url https://download.pytorch.org/whl/cpu torch==2.5.1

RUN pip install -r requirements-docker.txt

COPY . .

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

CMD ["python", "twilio_phone_server.py"]