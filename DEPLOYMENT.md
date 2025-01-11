# Multi-Agent Chat System Deployment Guide

This guide covers deployment of the multi-agent chat system using Docker containers on AWS ECS or Heroku.

## Local Development

1. Build and run locally:
```bash
docker-compose up --build
```

The system will be available at:
- Frontend: http://localhost
- Backend API: http://localhost/api
- WebSocket: ws://localhost/ws

## AWS ECS Deployment

### Prerequisites

1. AWS CLI installed and configured
2. Docker installed
3. ECR repositories created for frontend and backend
4. ECS cluster created
5. Task execution role with necessary permissions
6. Application Load Balancer configured
7. Redis instance (AWS ElastiCache) set up

### Deployment Steps

1. Update configuration:
   - Edit `deploy/aws/task-definition.json`:
     - Replace `${ECR_REGISTRY}` with your ECR registry
     - Update environment variables
   - Edit `deploy/aws/deploy.sh`:
     - Set correct AWS region
     - Update ECR registry
     - Set cluster and service names

2. Deploy:
```bash
chmod +x deploy/aws/deploy.sh
./deploy/aws/deploy.sh
```

### Infrastructure Setup

1. VPC and Networking:
```bash
aws cloudformation create-stack \
  --stack-name chat-system-network \
  --template-body file://deploy/aws/network.yml
```

2. ECS Cluster:
```bash
aws ecs create-cluster --cluster-name chat-system-cluster
```

3. Load Balancer:
```bash
aws elbv2 create-load-balancer \
  --name chat-system-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx
```

## Heroku Deployment

1. Create Heroku apps:
```bash
heroku create chat-system-backend
heroku create chat-system-frontend
```

2. Add Redis addon:
```bash
heroku addons:create heroku-redis:hobby-dev -a chat-system-backend
```

3. Configure environment variables:
```bash
heroku config:set \
  REDIS_URL=$(heroku config:get REDIS_URL) \
  CORS_ORIGINS=https://chat-system-frontend.herokuapp.com \
  -a chat-system-backend
```

4. Deploy containers:
```bash
# Backend
heroku container:push web -a chat-system-backend
heroku container:release web -a chat-system-backend

# Frontend
heroku container:push web -a chat-system-frontend
heroku container:release web -a chat-system-frontend
```

## Monitoring and Maintenance

### Health Checks

- Backend: `GET /health`
- Redis: Monitor through AWS ElastiCache or Heroku Redis metrics
- Frontend: Monitor through load balancer health checks

### Scaling

#### AWS ECS:
```bash
aws ecs update-service \
  --cluster chat-system-cluster \
  --service chat-system-service \
  --desired-count 3
```

#### Heroku:
```bash
heroku ps:scale web=3 -a chat-system-backend
```

### Logs

#### AWS:
```bash
aws logs get-log-events \
  --log-group-name /ecs/chat-system \
  --log-stream-name backend/xxx
```

#### Heroku:
```bash
heroku logs --tail -a chat-system-backend
```

## Security Considerations

1. Network Security:
   - Use private subnets for backend and Redis
   - Configure security groups to restrict access
   - Enable AWS WAF on the load balancer

2. Data Security:
   - Enable encryption at rest for Redis
   - Use AWS Secrets Manager for sensitive configuration
   - Enable SSL/TLS for all communications

3. Monitoring:
   - Set up CloudWatch alarms for metrics
   - Configure log aggregation
   - Enable AWS X-Ray for tracing

## Troubleshooting

1. Container Issues:
   - Check container logs
   - Verify health check endpoints
   - Review resource utilization

2. Network Issues:
   - Verify security group rules
   - Check route tables
   - Test connectivity between services

3. Application Issues:
   - Review application logs
   - Check environment variables
   - Verify Redis connection

## Backup and Recovery

1. Redis Backup:
   - Enable automatic backups in ElastiCache
   - Configure backup retention period
   - Test restore procedures

2. Application State:
   - Store critical data in persistent storage
   - Implement regular backup procedures
   - Document recovery steps
