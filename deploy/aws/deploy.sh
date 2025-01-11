#!/bin/bash
set -e

# Configuration
AWS_REGION="us-east-1"
ECR_REGISTRY="YOUR_AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
CLUSTER_NAME="chat-system-cluster"
SERVICE_NAME="chat-system-service"

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Build and push backend image
echo "Building and pushing backend image..."
docker build -t $ECR_REGISTRY/chat-backend:latest ./backend
docker push $ECR_REGISTRY/chat-backend:latest

# Build and push frontend image
echo "Building and pushing frontend image..."
docker build -t $ECR_REGISTRY/chat-frontend:latest ./frontend
docker push $ECR_REGISTRY/chat-frontend:latest

# Update ECS service
echo "Updating ECS service..."
aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service $SERVICE_NAME \
  --force-new-deployment \
  --region $AWS_REGION

# Wait for service to stabilize
echo "Waiting for service to stabilize..."
aws ecs wait services-stable \
  --cluster $CLUSTER_NAME \
  --services $SERVICE_NAME \
  --region $AWS_REGION

echo "Deployment completed successfully!"
