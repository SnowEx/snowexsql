#!/bin/bash

# AWS Lambda Deployment Script for SnowEx SQL
# This script builds and deploys the Docker container to AWS Lambda

set -e

# Configuration
AWS_ACCOUNT_ID="390402539674"
AWS_REGION="us-west-2"
ECR_REPOSITORY="snowexsql"
LAMBDA_FUNCTION_NAME="lambda-snowex-sql"
IMAGE_TAG="$(git rev-parse --short HEAD)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting SnowEx SQL Lambda deployment...${NC}"

# Check if AWS CLI is installed and configured
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Build the Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
DOCKER_BUILDKIT=0 docker build -f ../docker/Dockerfile -t ${ECR_REPOSITORY}:${IMAGE_TAG} ../..

# Get ECR login token
echo -e "${YELLOW}Logging into ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Tag the image for ECR
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:${IMAGE_TAG}"
echo -e "${YELLOW}Tagging image for ECR: ${ECR_URI}${NC}"
docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_URI}

# Push to ECR
echo -e "${YELLOW}Pushing image to ECR...${NC}"
docker push ${ECR_URI}

# Update Lambda function
echo -e "${YELLOW}Updating Lambda function...${NC}"
aws lambda update-function-code \
    --region ${AWS_REGION} \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --image-uri ${ECR_URI}

# Wait for the update to complete
echo -e "${YELLOW}Waiting for Lambda function update to complete...${NC}"
aws lambda wait function-updated \
    --region ${AWS_REGION} \
    --function-name ${LAMBDA_FUNCTION_NAME}

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}Lambda function '${LAMBDA_FUNCTION_NAME}' has been updated with the new image.${NC}"

# Optional: Test the function
read -p "Would you like to test the Lambda function? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Testing Lambda function...${NC}"
    aws lambda invoke \
        --region ${AWS_REGION} \
        --function-name ${LAMBDA_FUNCTION_NAME} \
        --payload '{"test": true}' \
        response.json
    
    echo -e "${GREEN}Test response:${NC}"
    cat response.json
    echo
    rm -f response.json
fi