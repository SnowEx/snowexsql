FROM public.ecr.aws/lambda/python:3.12

# Copy requirements and install dependencies
COPY deployment/docker/requirements-lambda.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r requirements-lambda.txt

# Copy the snowexsql package
COPY snowexsql/ ${LAMBDA_TASK_ROOT}/snowexsql/

# Set the CMD to your handler
CMD ["snowexsql.lambda_handler.lambda_handler"]