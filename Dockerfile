FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    zlib1g-dev \
    libsqlite3-dev \
    libreadline-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip wheel setuptools

COPY requirements.txt .

RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.11-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libcairo2 \
    libgirepository-1.0-1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

COPY . .

ENV PATH="/usr/local/bin:$PATH"

USER appuser

EXPOSE 8003

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
