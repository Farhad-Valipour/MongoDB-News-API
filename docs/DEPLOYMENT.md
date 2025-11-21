# Deployment Guide

Complete guide for deploying MongoDB News API to production.

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Cloud Deployment](#cloud-deployment)
3. [Environment Configuration](#environment-configuration)
4. [Monitoring & Logging](#monitoring--logging)
5. [Backup & Recovery](#backup--recovery)
6. [Scaling](#scaling)
7. [Security](#security)

---

## Docker Deployment

### Quick Start with Docker Compose

```bash
# Clone repository
git clone https://github.com/yourusername/mongodb-news-api.git
cd mongodb-news-api

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGODB_USERNAME}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_PASSWORD}
    volumes:
      - /data/mongodb:/data/db
    networks:
      - news-api-network

  api:
    image: yourusername/mongodb-news-api:latest
    restart: always
    environment:
      MONGODB_URI: mongodb://mongodb:27017
      API_KEYS: ${API_KEYS}
      DEBUG: false
      LOG_LEVEL: INFO
    ports:
      - "8000:8000"
    depends_on:
      - mongodb
    networks:
      - news-api-network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    networks:
      - news-api-network

networks:
  news-api-network:
    driver: bridge
```

Deploy:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Cloud Deployment

### AWS Deployment

#### Using ECS (Elastic Container Service)

1. **Build and push Docker image**
```bash
# Authenticate to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag
docker build -t mongodb-news-api .
docker tag mongodb-news-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/mongodb-news-api:latest

# Push
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/mongodb-news-api:latest
```

2. **Create ECS Task Definition**
```json
{
  "family": "mongodb-news-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/mongodb-news-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "MONGODB_URI", "value": "mongodb://your-atlas-uri"},
        {"name": "LOG_LEVEL", "value": "INFO"}
      ],
      "secrets": [
        {
          "name": "API_KEYS",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:api-keys"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mongodb-news-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "api"
        }
      }
    }
  ]
}
```

3. **Create ECS Service**
```bash
aws ecs create-service \
  --cluster production \
  --service-name mongodb-news-api \
  --task-definition mongodb-news-api \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

#### Using EC2

```bash
# Connect to EC2
ssh -i key.pem ubuntu@ec2-ip

# Install Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Clone and deploy
git clone https://github.com/yourusername/mongodb-news-api.git
cd mongodb-news-api
docker-compose -f docker-compose.prod.yml up -d
```

### Google Cloud Platform (GCP)

#### Using Cloud Run

```bash
# Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/mongodb-news-api

# Deploy to Cloud Run
gcloud run deploy mongodb-news-api \
  --image gcr.io/PROJECT_ID/mongodb-news-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MONGODB_URI=mongodb+srv://... \
  --set-secrets API_KEYS=api-keys:latest
```

### Azure

#### Using Container Instances

```bash
# Create resource group
az group create --name news-api-rg --location eastus

# Create container
az container create \
  --resource-group news-api-rg \
  --name mongodb-news-api \
  --image yourusername/mongodb-news-api:latest \
  --dns-name-label mongodb-news-api \
  --ports 8000 \
  --environment-variables \
    MONGODB_URI=mongodb://... \
    LOG_LEVEL=INFO \
  --secure-environment-variables \
    API_KEYS=key1,key2
```

### Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create mongodb-news-api

# Add MongoDB add-on
heroku addons:create mongolab:sandbox

# Set config vars
heroku config:set API_KEYS=your-keys

# Deploy
git push heroku main
```

---

## Environment Configuration

### Production Environment Variables

```env
# Application
APP_NAME=MongoDB News API
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

# MongoDB (Use MongoDB Atlas for production)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB_NAME=novoxpert
MONGODB_COLLECTION_NAME=news
MONGODB_MIN_POOL_SIZE=10
MONGODB_MAX_POOL_SIZE=50

# Security
API_KEYS=prod-key-1,prod-key-2,prod-key-3
# Generate strong keys: python -c "import secrets; print(secrets.token_urlsafe(32))"

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting
RATE_LIMIT_PER_HOUR=1000
```

### MongoDB Atlas Setup

1. **Create Cluster**
   - Go to [MongoDB Atlas](https://cloud.mongodb.com/)
   - Create a new cluster
   - Choose your cloud provider and region

2. **Configure Network Access**
   - Add IP whitelist (0.0.0.0/0 for development)
   - Use VPC peering for production

3. **Create Database User**
   - Create user with read/write permissions
   - Use strong password

4. **Get Connection String**
   ```
   mongodb+srv://username:password@cluster.mongodb.net/novoxpert?retryWrites=true&w=majority
   ```

---

## Monitoring & Logging

### Application Logs

```bash
# Docker logs
docker-compose logs -f api

# Tail logs
tail -f logs/app.log

# With filtering
grep ERROR logs/app.log
```

### Health Checks

```bash
# API health
curl http://your-domain.com/api/v1/health

# Docker health
docker inspect --format='{{.State.Health.Status}}' mongodb-news-api
```

### Monitoring Tools

#### Prometheus + Grafana

1. Add to `docker-compose.yml`:
```yaml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

2. Create `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'fastapi'
    static_configs:
      - targets: ['api:8000']
```

#### Datadog

```yaml
services:
  datadog:
    image: datadog/agent:latest
    environment:
      - DD_API_KEY=${DD_API_KEY}
      - DD_SITE=datadoghq.com
      - DD_LOGS_ENABLED=true
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /proc/:/host/proc/:ro
      - /sys/fs/cgroup:/host/sys/fs/cgroup:ro
```

---

## Backup & Recovery

### MongoDB Backup

#### Manual Backup

```bash
# Full backup
mongodump --uri="mongodb://localhost:27017" --db=novoxpert --out=/backup/$(date +%Y%m%d)

# Compress backup
tar -czf backup-$(date +%Y%m%d).tar.gz /backup/$(date +%Y%m%d)
```

#### Automated Backup Script

Create `backup.sh`:
```bash
#!/bin/bash

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
MONGODB_URI="mongodb://localhost:27017"
DB_NAME="novoxpert"

# Create backup
mongodump --uri="$MONGODB_URI" --db="$DB_NAME" --out="$BACKUP_DIR/$DATE"

# Compress
tar -czf "$BACKUP_DIR/$DATE.tar.gz" "$BACKUP_DIR/$DATE"
rm -rf "$BACKUP_DIR/$DATE"

# Keep only last 7 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

Add to crontab:
```bash
# Daily backup at 2 AM
0 2 * * * /path/to/backup.sh
```

### Recovery

```bash
# Extract backup
tar -xzf backup-20251121.tar.gz

# Restore
mongorestore --uri="mongodb://localhost:27017" --db=novoxpert backup-20251121/novoxpert/
```

---

## Scaling

### Horizontal Scaling

#### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml news-api

# Scale service
docker service scale news-api_api=5
```

#### Kubernetes

Create `deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb-news-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mongodb-news-api
  template:
    metadata:
      labels:
        app: mongodb-news-api
    spec:
      containers:
      - name: api
        image: mongodb-news-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: MONGODB_URI
          valueFrom:
            secretKeyRef:
              name: mongodb-secret
              key: uri
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: mongodb-news-api-service
spec:
  selector:
    app: mongodb-news-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f deployment.yaml
```

### Load Balancing

#### Nginx Configuration

Create `nginx.conf`:
```nginx
upstream api_backend {
    least_conn;
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Security

### SSL/TLS Configuration

#### Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Firewall Configuration

```bash
# Ubuntu UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### API Key Rotation

```bash
# Generate new keys
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update environment
export API_KEYS=new-key-1,new-key-2,old-key-1

# Gracefully remove old keys after transition period
```

---

## Performance Tuning

### MongoDB Indexes

```javascript
// Create indexes for better query performance
db.news.createIndex({ "releasedAt": -1 })
db.news.createIndex({ "source": 1, "releasedAt": -1 })
db.news.createIndex({ "assets.slug": 1, "releasedAt": -1 })
db.news.createIndex({ "slug": 1 }, { unique: true })
```

### Uvicorn Workers

```bash
# Multiple workers for production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Troubleshooting

### Common Issues

**API not responding:**
```bash
# Check if service is running
docker-compose ps

# Check logs
docker-compose logs api

# Restart service
docker-compose restart api
```

**Database connection error:**
```bash
# Test MongoDB connection
mongosh --uri="your-mongodb-uri"

# Check network
ping mongodb-host
```

**High memory usage:**
```bash
# Monitor resources
docker stats

# Adjust memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 512M
```

---

## Checklist for Production

- [ ] SSL/TLS configured
- [ ] Strong API keys generated
- [ ] CORS origins restricted
- [ ] Rate limiting enabled
- [ ] MongoDB authentication enabled
- [ ] Automated backups configured
- [ ] Monitoring setup
- [ ] Log aggregation setup
- [ ] Health checks configured
- [ ] Error tracking enabled
- [ ] Documentation updated
- [ ] Load testing completed

---

**Need help?** Open an issue on [GitHub](https://github.com/yourusername/mongodb-news-api/issues)
