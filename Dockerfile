FROM public.ecr.aws/lambda/python:3.11

# Lambda task root is already set by the base image
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements first
COPY requirements.txt .

# Install deps into Lambda task dir (must not install globally)
# Pin numpy/pandas to Lambda-compatible versions to avoid compilation errors
RUN pip install --no-cache-dir \
        numpy==1.26.4 \
        pandas==2.1.4 \
        -r requirements.txt \
        --target "${LAMBDA_TASK_ROOT}"

# Copy application code
COPY src/ ./src/

# Lambda entrypoint → FastAPI adapter (Mangum)
CMD ["src.main.handler"]
