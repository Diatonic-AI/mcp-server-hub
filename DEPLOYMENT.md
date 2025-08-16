# MCP Server Hub Deployment Guide

This guide covers deployment scenarios for the MCP Server Hub across different environments.

## 🌍 Platform-Specific Deployment

### Windows Deployment

#### Prerequisites
```powershell
# Install Chocolatey (if not already installed)
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install dependencies
choco install nodejs python git googlechrome -y

# Verify installations
node --version
python --version  
git --version
```

#### Setup
```batch
git clone https://github.com/Diatonic-AI/mcp-server-hub.git
cd mcp-server-hub
start-mcp.bat setup
node credential-manager.js generate
```

#### Configuration
```batch
REM Edit credentials
copy %APPDATA%\mcp-credentials\.env.template .env
notepad .env

REM Validate setup
node credential-manager.js validate
start-mcp.bat run
```

### Linux/Ubuntu Deployment

#### Prerequisites
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js via NodeSource
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python and build tools
sudo apt install -y python3 python3-pip python3-venv build-essential git chromium-browser

# Verify installations  
node --version
python3 --version
chromium-browser --version
```

#### Setup
```bash
git clone https://github.com/Diatonic-AI/mcp-server-hub.git
cd mcp-server-hub
chmod +x start-mcp.sh
./start-mcp.sh setup
node credential-manager.js generate
```

#### Configuration
```bash
# Edit credentials
cp ~/.mcp-credentials/.env.template .env
nano .env

# Validate and start
node credential-manager.js validate
./start-mcp.sh run
```

### macOS Deployment

#### Prerequisites
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install node python git
brew install --cask google-chrome

# Verify installations
node --version
python3 --version
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version
```

#### Setup and Configuration
Same as Linux, but Chrome path will be auto-detected as `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`.

### WSL2 Deployment

#### Prerequisites
```bash
# Inside WSL2
sudo apt update && sudo apt upgrade -y

# Install Node.js, Python, and dependencies
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs python3 python3-pip python3-venv build-essential git

# Install Chrome in WSL2 (optional, for Puppeteer)
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable
```

#### Setup
```bash
git clone https://github.com/Diatonic-AI/mcp-server-hub.git
cd mcp-server-hub
./start-mcp.sh setup
```

The system will automatically detect WSL2 and use appropriate configurations.

## 🐳 Docker Deployment

### Local Docker Development

#### Prerequisites
- Docker Desktop (Windows/macOS) or Docker CE (Linux)
- Docker Compose v2+

#### Quick Start
```bash
git clone https://github.com/Diatonic-AI/mcp-server-hub.git
cd mcp-server-hub

# Generate secrets
node credential-manager.js secrets

# Create environment file
cp platform-configs/docker/.env.example platform-configs/docker/.env
# Edit with your credentials

# Start all services
docker-compose -f platform-configs/docker/docker-compose.yml up -d

# View logs
docker-compose -f platform-configs/docker/docker-compose.yml logs -f
```

#### Development with Auto-Rebuild
```bash
# For active development
docker-compose -f platform-configs/docker/docker-compose.yml up --build -d

# Watch logs in real-time
docker-compose -f platform-configs/docker/docker-compose.yml logs -f mcp-node mcp-python
```

### Production Docker Deployment

#### Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c platform-configs/docker/docker-compose.prod.yml mcp-hub

# Check status
docker service ls
docker stack ps mcp-hub
```

#### Kubernetes Deployment
```yaml
# kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: mcp-hub

---
# kubernetes/configmap.yaml  
apiVersion: v1
kind: ConfigMap
metadata:
  name: mcp-config
  namespace: mcp-hub
data:
  mcp-hub-config.json: |
    # Docker configuration content here

---
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-node-servers
  namespace: mcp-hub
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mcp-node
  template:
    metadata:
      labels:
        app: mcp-node
    spec:
      containers:
      - name: mcp-node
        image: mcp-hub/node:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: production
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: data
          mountPath: /app/data
      volumes:
      - name: config
        configMap:
          name: mcp-config
      - name: data
        persistentVolumeClaim:
          claimName: mcp-data-pvc
```

## ☁️ Cloud Deployment

### AWS ECS Deployment

#### Task Definition
```json
{
  "family": "mcp-hub",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "mcp-node",
      "image": "ACCOUNT.dkr.ecr.REGION.amazonaws.com/mcp-hub/node:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "NODE_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "GITHUB_PERSONAL_ACCESS_TOKEN", 
          "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:mcp-hub/github-token"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mcp-hub",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "mcp-node"
        }
      }
    }
  ]
}
```

#### Deployment Script
```bash
#!/bin/bash
# aws-deploy.sh

# Build and push images
docker build -t mcp-hub/node -f Dockerfile.node .
docker build -t mcp-hub/python -f Dockerfile.python .

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

docker tag mcp-hub/node:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/mcp-hub/node:latest
docker tag mcp-hub/python:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/mcp-hub/python:latest

docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/mcp-hub/node:latest
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/mcp-hub/python:latest

# Update ECS service
aws ecs update-service --cluster mcp-hub --service mcp-node-service --force-new-deployment
```

### Google Cloud Run Deployment

```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/PROJECT-ID/mcp-node .
gcloud run deploy mcp-hub --image gcr.io/PROJECT-ID/mcp-node --platform managed --region us-central1

# Set environment variables
gcloud run services update mcp-hub --set-env-vars NODE_ENV=production --region us-central1
```

### Azure Container Instances

```bash
# Create resource group
az group create --name mcp-hub-rg --location eastus

# Create container registry
az acr create --resource-group mcp-hub-rg --name mcpHubRegistry --sku Basic

# Build and push
az acr build --registry mcpHubRegistry --image mcp-node .

# Deploy container instance
az container create \
  --resource-group mcp-hub-rg \
  --name mcp-hub \
  --image mcpHubRegistry.azurecr.io/mcp-node:latest \
  --cpu 1 \
  --memory 2 \
  --registry-login-server mcpHubRegistry.azurecr.io \
  --registry-username mcpHubRegistry \
  --registry-password $(az acr credential show --name mcpHubRegistry --query "passwords[0].value" --output tsv)
```

## 🔧 Configuration Management

### Environment-Specific Configurations

#### Development
```bash
# Local development with hot reload
NODE_ENV=development ./start-mcp.sh run
```

#### Staging
```bash
# Docker with external databases
docker-compose -f platform-configs/docker/docker-compose.yml -f platform-configs/docker/docker-compose.staging.yml up -d
```

#### Production  
```bash
# Full production stack with monitoring
docker-compose -f platform-configs/docker/docker-compose.yml -f platform-configs/docker/docker-compose.prod.yml up -d
```

### Secret Management

#### Local Development
```bash
# Use credential manager
node credential-manager.js generate
```

#### Docker
```bash
# Generate secure secrets
node credential-manager.js secrets

# Secrets stored in platform-configs/docker/secrets/
```

#### Cloud (AWS Secrets Manager)
```bash
# Store secrets in AWS
aws secretsmanager create-secret --name "mcp-hub/github-token" --secret-string "ghp_your_token_here"
aws secretsmanager create-secret --name "mcp-hub/google-maps-key" --secret-string "AIza_your_key_here"
```

## 📊 Monitoring and Observability

### Health Checks

#### Docker Health Checks
```dockerfile
# Already included in Dockerfiles
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node --version || exit 1
```

#### External Monitoring
```bash
# Prometheus metrics endpoint (if configured)
curl http://localhost:3000/metrics

# Health check endpoints
curl http://localhost:3000/health
```

### Logging

#### Centralized Logging (ELK Stack)
```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.2
    environment:
      - discovery.type=single-node
    
  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.2
    
  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.2
    ports:
      - "5601:5601"
```

#### Application Logging
```javascript
// Structured logging configuration
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' })
  ]
});
```

## 🚨 Troubleshooting

### Common Issues

#### Permission Errors
```bash
# Linux/macOS
chmod +x start-mcp.sh
chmod 600 .env

# Windows (run as Administrator if needed)
icacls .env /grant:r %USERNAME%:(R,W)
```

#### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :3000  # Linux
netstat -an | findstr :3000  # Windows

# Change ports in docker-compose.yml
ports:
  - "3001:3000"  # External:Internal
```

#### Database Connection Issues
```bash
# Check database connectivity
docker-compose exec postgres pg_isready
docker-compose exec redis redis-cli ping

# View database logs
docker-compose logs postgres redis
```

### Performance Tuning

#### Node.js Optimization
```bash
# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=4096"
```

#### Docker Resource Limits
```yaml
# In docker-compose.yml
services:
  mcp-node:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## 🔄 Maintenance

### Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose build --no-cache

# Update Python dependencies
source mcp-python-env/bin/activate
pip install --upgrade -r requirements.txt
```

### Backup
```bash
# Backup Docker volumes
docker run --rm -v mcp-data:/data -v $(pwd):/backup alpine tar czf /backup/mcp-backup.tar.gz /data

# Restore
docker run --rm -v mcp-data:/data -v $(pwd):/backup alpine tar xzf /backup/mcp-backup.tar.gz
```

---

For more deployment scenarios and advanced configurations, see the [GitHub Wiki](https://github.com/Diatonic-AI/mcp-server-hub/wiki).
