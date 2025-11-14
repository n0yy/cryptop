# Deployment Guide

## Production Deployment

### Prerequisites

- Docker & Docker Compose
- Domain name with SSL certificate
- Cloud provider account (AWS, GCP, Azure, or DigitalOcean)
- Environment variables configured

## Deployment Options

### Option 1: Docker Compose (Simple)

#### 1. Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y
```

#### 2. Clone Repository

```bash
git clone <repository-url>
cd crypto-monitoring-system/backend
```

#### 3. Configure Environment

```bash
cp .env.example .env
nano .env
```

Set production values:
```env
DEBUG=False
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@postgres:5432/crypto_db
SECRET_KEY=<generate-strong-secret>
JWT_SECRET_KEY=<generate-strong-secret>
```

#### 4. Deploy

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Option 2: Kubernetes (Scalable)

#### 1. Create Kubernetes Manifests

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crypto-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: crypto-api
  template:
    metadata:
      labels:
        app: crypto-api
    spec:
      containers:
      - name: api
        image: crypto-monitoring:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: crypto-secrets
              key: database-url
```

#### 2. Deploy to Kubernetes

```bash
kubectl apply -f k8s/
kubectl get pods
kubectl get services
```

### Option 3: Cloud Platform (AWS)

#### Using AWS ECS

```bash
# Build and push image
docker build -t crypto-monitoring .
docker tag crypto-monitoring:latest <ecr-repo-url>:latest
docker push <ecr-repo-url>:latest

# Deploy with ECS CLI
ecs-cli compose --file docker-compose.prod.yml up
```

## Database Setup

### PostgreSQL with TimescaleDB

```bash
# Connect to database
psql $DATABASE_URL

# Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

# Create hypertable for price history
SELECT create_hypertable('price_history', 'timestamp');

# Run migrations
alembic upgrade head
```

## SSL/TLS Configuration

### Using Nginx as Reverse Proxy

```nginx
# /etc/nginx/sites-available/crypto-api
server {
    listen 80;
    server_name api.cryptomonitoring.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.cryptomonitoring.com;

    ssl_certificate /etc/letsencrypt/live/api.cryptomonitoring.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.cryptomonitoring.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Obtain SSL Certificate

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.cryptomonitoring.com

# Auto-renewal
sudo certbot renew --dry-run
```

## Monitoring Setup

### Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'crypto-api'
    static_configs:
      - targets: ['localhost:8000']
```

### Grafana Dashboard

```bash
docker run -d \
  -p 3000:3000 \
  --name=grafana \
  -e "GF_SECURITY_ADMIN_PASSWORD=admin" \
  grafana/grafana
```

## Backup Strategy

### Database Backups

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

### Automated Backups

```bash
# Add to crontab
0 2 * * * /path/to/backup.sh
```

## Scaling Strategies

### Horizontal Scaling

```bash
# Scale API servers
docker-compose up -d --scale api=3

# Scale Celery workers
docker-compose up -d --scale celery_worker=5
```

### Load Balancing

```nginx
upstream api_backend {
    least_conn;
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    location / {
        proxy_pass http://api_backend;
    }
}
```

## Health Checks

### Application Health

```bash
# Check API health
curl https://api.cryptomonitoring.com/health

# Check database connection
curl https://api.cryptomonitoring.com/health/db

# Check Redis connection
curl https://api.cryptomonitoring.com/health/redis
```

### Monitoring Endpoints

- API: `https://api.cryptomonitoring.com/health`
- Flower: `https://flower.cryptomonitoring.com`
- Prometheus: `https://prometheus.cryptomonitoring.com`
- Grafana: `https://grafana.cryptomonitoring.com`

## Security Checklist

- [ ] Change default passwords
- [ ] Configure firewall rules
- [ ] Enable SSL/TLS
- [ ] Set up rate limiting
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets
- [ ] Enable database encryption
- [ ] Set up VPN for database access
- [ ] Configure backup encryption
- [ ] Enable audit logging
- [ ] Set up intrusion detection
- [ ] Regular security updates

## Performance Tuning

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_alerts_user_status ON alerts(user_id, status);
CREATE INDEX idx_positions_portfolio ON positions(portfolio_id);

-- Analyze tables
ANALYZE alerts;
ANALYZE portfolios;
ANALYZE positions;
```

### Redis Configuration

```conf
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

### Application Settings

```env
# Production settings
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=20
REDIS_CACHE_TTL=3600
WS_MAX_CONNECTIONS=10000
```

## Troubleshooting

### Common Issues

**High Memory Usage**
```bash
# Check container stats
docker stats

# Restart services
docker-compose restart
```

**Database Connection Pool Exhausted**
```bash
# Increase pool size in .env
DATABASE_POOL_SIZE=100
DATABASE_MAX_OVERFLOW=50
```

**Celery Tasks Stuck**
```bash
# Purge all tasks
celery -A app.tasks.celery_app purge

# Restart workers
docker-compose restart celery_worker
```

## Rollback Procedure

```bash
# Rollback to previous version
docker-compose down
git checkout <previous-tag>
docker-compose up -d

# Rollback database migration
alembic downgrade -1
```

## Maintenance Windows

Schedule regular maintenance:
- Weekly: Security updates
- Monthly: Database optimization
- Quarterly: Full system audit

## Support & Monitoring

- Set up alerts for critical metrics
- Configure on-call rotation
- Document incident response procedures
- Regular backup testing
