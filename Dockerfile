# Build stage
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Lambda stage
FROM public.ecr.aws/lambda/python:3.11
COPY --from=builder /install /var/task
COPY src/ ./src/
CMD ["src.main.handler"]
