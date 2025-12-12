# Build stage
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel

# Install packages into /install in a Lambda-compatible layout
RUN pip install --no-cache-dir -r requirements.txt --target /install

# Lambda stage
FROM public.ecr.aws/lambda/python:3.11
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy installed packages
COPY --from=builder /install/ ${LAMBDA_TASK_ROOT}/

# Copy application code
COPY src/ ./src/
COPY src/lambda.py ./

# Lambda entrypoint
CMD ["lambda.handler"]
