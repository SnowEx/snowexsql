# Deployment

This directory contains all the infrastructure and deployment configurations for
running snowexsql on AWS Lambda.

## Structure

- **`docker/`** - Docker container configuration for Lambda
  - `Dockerfile` - Lambda-compatible container definition
  - `.dockerignore` - Optimization for container builds
  - `requirements-lambda.txt` - Lightweight dependencies

- **`aws/`** - AWS IAM policies and configurations
  - `ecr_policy.json` - ECR repository permissions for Lambda
  - `secrets_policy.json` - Secrets Manager access policy

- **`scripts/`** - Deployment automation scripts
  - `deploy.sh` - Main deployment script (container-based)
  - `test_lambda.sh` - Automated testing script

## Quick Start

1. Run `scripts/deploy.sh` to deploy the Lambda function
2. Test with `scripts/test_lambda.sh`

## Prerequisites

- AWS CLI configured
- Docker installed and running  
- Existing ECR repository named `snowexsql`
- Lambda function with container image support