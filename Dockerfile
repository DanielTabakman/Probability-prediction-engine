FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# System deps (minimal) + runuser for non-root entrypoint
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1001 ppe \
    && useradd --uid 1001 --gid ppe --create-home --shell /usr/sbin/nologin ppe

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
RUN chmod +x /app/scripts/docker_streamlit_entrypoint.sh \
    && chown -R ppe:ppe /app

# Streamlit default port on many platforms is provided via PORT.
ENV PORT=8501
EXPOSE 8501

ENTRYPOINT ["/app/scripts/docker_streamlit_entrypoint.sh"]
CMD ["sh", "-c", "streamlit run src/viz/app.py --server.port ${PORT} --server.address 0.0.0.0"]
