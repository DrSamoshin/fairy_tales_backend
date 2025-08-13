FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    curl libpq-dev gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR /app
COPY . /app
EXPOSE 8080
CMD ["uv", "run", "python", "run.py"]
