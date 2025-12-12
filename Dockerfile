FROM public.ecr.aws/lambda/python:3.11

# Set the working directory inside Lambda
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements
COPY requirements.txt .

# Install dependencies into Lambda’s task root
RUN pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy application source
COPY src/ ./src/

# Lambda uses a handler, not Uvicorn
# Mangum converts FastAPI → Lambda-compatible
CMD ["src.main.handler"]
