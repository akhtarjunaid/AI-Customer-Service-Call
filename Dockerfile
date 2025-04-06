FROM public.ecr.aws/lambda/python:3.12.7

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your source code into the container
COPY src/ ${LAMBDA_TASK_ROOT}/src/

# Set the working directory so Python can find your modules
ENV PYTHONPATH="${LAMBDA_TASK_ROOT}/src"

# Set the Lambda handler path: file.function
CMD ["src.lambda_function.lambda_handler"]