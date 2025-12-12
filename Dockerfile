FROM public.ecr.aws/lambda/python:3.11

WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements
COPY requirements.txt .

# Install prebuilt wheels only
RUN pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy app code
COPY src/ ./src/

# Lambda entrypoint
CMD ["src.lambda.handler"]
