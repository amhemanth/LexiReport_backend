# Deployment Guide

## Overview

This document provides detailed instructions for deploying the LexiReport application in various environments.

## Deployment Architecture

```mermaid
graph TD
    subgraph Production Environment
        A[Load Balancer] --> B[API Servers]
        B --> C[Database Cluster]
        B --> D[Cache Cluster]
        B --> E[File Storage]
        
        F[Monitoring] --> A
        F --> B
        F --> C
        F --> D
        F --> E
    end
```

## Prerequisites

### System Requirements

- **API Servers**
  - CPU: 4+ cores
  - RAM: 8GB+
  - Storage: 50GB+ SSD
  - OS: Ubuntu 20.04 LTS

- **Database Servers**
  - CPU: 4+ cores
  - RAM: 16GB+
  - Storage: 100GB+ SSD
  - OS: Ubuntu 20.04 LTS

- **Cache Servers**
  - CPU: 2+ cores
  - RAM: 4GB+
  - Storage: 20GB+ SSD
  - OS: Ubuntu 20.04 LTS

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.20+ (for production)
- Helm 3.0+ (for production)
- Git
- Python 3.8+
- Node.js 16+

## Environment Setup

### 1. Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/lexireport.git
cd lexireport

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
cd frontend
npm install
```

### 2. Configuration

Create `.env` files for both backend and frontend:

```env
# Backend .env
DATABASE_URL=postgresql://user:password@localhost:5432/lexireport
REDIS_URL=redis://localhost:6379
STORAGE_BUCKET=lexireport-files
API_KEY=your_api_key
JWT_SECRET=your_jwt_secret

# Frontend .env
API_URL=http://localhost:8000
WS_URL=ws://localhost:8000
```

## Deployment Methods

### 1. Docker Compose (Development/Staging)

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/lexireport
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=lexireport
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

Deploy with:
```bash
docker-compose up -d
```

### 2. Kubernetes (Production)

#### Helm Chart Structure

```mermaid
graph TD
    A[LexiReport Chart] --> B[API Deployment]
    A --> C[Database StatefulSet]
    A --> D[Redis StatefulSet]
    A --> E[Ingress]
    A --> F[ConfigMaps]
    A --> G[Secrets]
```

#### Deployment Steps

1. **Create Namespace**
```bash
kubectl create namespace lexireport
```

2. **Install Dependencies**
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgresql bitnami/postgresql -n lexireport
helm install redis bitnami/redis -n lexireport
```

3. **Deploy Application**
```bash
helm install lexireport ./helm/lexireport -n lexireport
```

### 3. Cloud Platform Deployment

#### AWS Deployment

```mermaid
graph TD
    A[Route 53] --> B[ALB]
    B --> C[ECS Cluster]
    C --> D[API Service]
    C --> E[Worker Service]
    D --> F[RDS]
    D --> G[ElastiCache]
    E --> F
    E --> G
```

1. **Create ECS Cluster**
```bash
aws ecs create-cluster --cluster-name lexireport
```

2. **Deploy Services**
```bash
aws ecs create-service --cluster lexireport --service-name api --task-definition lexireport-api
```

#### Azure Deployment

```mermaid
graph TD
    A[Azure DNS] --> B[Application Gateway]
    B --> C[AKS Cluster]
    C --> D[API Pods]
    C --> E[Worker Pods]
    D --> F[Azure Database]
    D --> G[Azure Cache]
    E --> F
    E --> G
```

1. **Create AKS Cluster**
```bash
az aks create --resource-group lexireport --name lexireport-cluster
```

2. **Deploy Application**
```bash
kubectl apply -f k8s/
```

## Monitoring Setup

### 1. Prometheus & Grafana

```mermaid
graph TD
    A[Prometheus] --> B[Metrics]
    B --> C[Grafana]
    C --> D[Dashboards]
    D --> E[Alerts]
```

1. **Install Prometheus**
```bash
helm install prometheus prometheus-community/kube-prometheus-stack
```

2. **Configure Grafana**
```bash
kubectl apply -f monitoring/grafana-dashboards.yaml
```

### 2. Logging

```mermaid
graph TD
    A[Application] --> B[Fluentd]
    B --> C[Elasticsearch]
    C --> D[Kibana]
```

1. **Install ELK Stack**
```bash
helm install elk elastic/eck-operator
```

2. **Configure Log Shipping**
```bash
kubectl apply -f logging/fluentd-config.yaml
```

## Security Configuration

### 1. SSL/TLS Setup

```mermaid
graph TD
    A[Domain] --> B[Certificate]
    B --> C[Load Balancer]
    C --> D[Application]
```

1. **Generate Certificate**
```bash
certbot certonly --nginx -d api.lexireport.com
```

2. **Configure SSL**
```bash
kubectl create secret tls lexireport-tls --cert=cert.pem --key=key.pem
```

### 2. Network Security

```mermaid
graph TD
    A[VPC] --> B[Security Groups]
    B --> C[API Servers]
    B --> D[Database]
    B --> E[Cache]
```

1. **Configure Security Groups**
```bash
aws ec2 create-security-group --group-name lexireport-api
```

2. **Set Up Firewall Rules**
```bash
kubectl apply -f security/network-policies.yaml
```

## Backup and Recovery

### 1. Database Backup

```mermaid
graph TD
    A[Database] --> B[Backup Job]
    B --> C[S3 Bucket]
    C --> D[Restore Process]
```

1. **Configure Backup**
```bash
kubectl apply -f backup/database-backup.yaml
```

2. **Test Recovery**
```bash
./scripts/test-recovery.sh
```

### 2. File Storage Backup

1. **Configure S3 Replication**
```bash
aws s3api put-bucket-replication --bucket lexireport-files --replication-configuration file://backup/replication.json
```

2. **Set Up Versioning**
```bash
aws s3api put-bucket-versioning --bucket lexireport-files --versioning-configuration Status=Enabled
```

## Scaling Configuration

### 1. Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: lexireport-api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: lexireport-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 2. Database Scaling

1. **Configure Read Replicas**
```bash
kubectl apply -f scaling/database-replicas.yaml
```

2. **Set Up Connection Pooling**
```bash
kubectl apply -f scaling/pgpool.yaml
```

## Maintenance Procedures

### 1. Database Maintenance

```mermaid
graph TD
    A[Maintenance Window] --> B[Backup]
    B --> C[Vacuum]
    C --> D[Index Rebuild]
    D --> E[Verify]
```

1. **Schedule Maintenance**
```bash
kubectl apply -f maintenance/db-maintenance.yaml
```

2. **Monitor Progress**
```bash
kubectl logs -f job/db-maintenance
```

### 2. Application Updates

1. **Deploy Update**
```bash
helm upgrade lexireport ./helm/lexireport
```

2. **Verify Deployment**
```bash
kubectl rollout status deployment/lexireport-api
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check network policies
   - Verify credentials
   - Check database logs

2. **API Performance Issues**
   - Check resource usage
   - Review application logs
   - Monitor database performance

3. **Cache Issues**
   - Check Redis connection
   - Monitor memory usage
   - Review cache hit rates

### Debug Procedures

1. **API Debugging**
```bash
kubectl logs -f deployment/lexireport-api
```

2. **Database Debugging**
```bash
kubectl exec -it postgresql-0 -- psql -U postgres
```

3. **Cache Debugging**
```bash
kubectl exec -it redis-0 -- redis-cli
```

## Disaster Recovery

### 1. Recovery Procedures

```mermaid
graph TD
    A[Disaster] --> B[Assess Impact]
    B --> C[Restore Backup]
    C --> D[Verify Data]
    D --> E[Resume Service]
```

1. **Database Recovery**
```bash
./scripts/recover-database.sh
```

2. **Application Recovery**
```bash
./scripts/recover-application.sh
```

### 2. Failover Testing

1. **Test Database Failover**
```bash
./scripts/test-db-failover.sh
```

2. **Test Application Failover**
```bash
./scripts/test-app-failover.sh
```

## Performance Optimization

### 1. API Optimization

```mermaid
graph TD
    A[API] --> B[Caching]
    A --> C[Connection Pooling]
    A --> D[Load Balancing]
```

1. **Configure Caching**
```bash
kubectl apply -f optimization/cache-config.yaml
```

2. **Optimize Database**
```bash
kubectl apply -f optimization/db-optimization.yaml
```

### 2. Frontend Optimization

1. **Configure CDN**
```bash
kubectl apply -f optimization/cdn-config.yaml
```

2. **Enable Compression**
```bash
kubectl apply -f optimization/compression.yaml
```

## Security Best Practices

1. **Regular Updates**
   - Keep dependencies updated
   - Apply security patches
   - Monitor vulnerabilities

2. **Access Control**
   - Use RBAC
   - Implement least privilege
   - Regular access review

3. **Monitoring**
   - Security event logging
   - Intrusion detection
   - Regular audits 