#!/bin/bash

# Update Lambda function configuration (timeout, memory, etc.)
# Run this after deploy.sh if you need to adjust Lambda settings

set -e

# Configuration
AWS_REGION="us-west-2"
LAMBDA_FUNCTION_NAME="lambda-snowex-sql"
TIMEOUT=90  # seconds (max is 900 for Lambda)
MEMORY=1024  # MB (default is 512, max is 10240)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Updating Lambda configuration...${NC}"
echo -e "${YELLOW}Function: ${LAMBDA_FUNCTION_NAME}${NC}"
echo -e "${YELLOW}Timeout: ${TIMEOUT}s${NC}"
echo -e "${YELLOW}Memory: ${MEMORY}MB${NC}"

# Update Lambda configuration
aws lambda update-function-configuration \
    --region ${AWS_REGION} \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --timeout ${TIMEOUT} \
    --memory-size ${MEMORY}

echo -e "${GREEN}Configuration updated successfully!${NC}"

# Wait a moment for the update to propagate
sleep 2

# Show current configuration
echo -e "${YELLOW}Current configuration:${NC}"
aws lambda get-function-configuration \
    --region ${AWS_REGION} \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --query '{Timeout:Timeout,Memory:MemorySize,Runtime:Runtime,LastModified:LastModified}' \
    --output table

echo -e "${GREEN}Done!${NC}"
