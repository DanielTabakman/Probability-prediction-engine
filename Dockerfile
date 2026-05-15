FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Streamlit default port on many platforms is provided via PORT.
ENV PORT=8501
EXPOSE 8501

CMD ["sh", "-c", "streamlit run src/viz/app.py --server.port ${PORT} --server.address 0.0.0.0"]
