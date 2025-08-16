# Production MCP System

A production-ready Model Context Protocol (MCP) server orchestration system that uses on-demand container management for optimal resource utilization.

## 🚀 Features

- **Production NVMe Drive Storage**: All data stored on high-performance NVMe drive
- **On-Demand Container Management**: Servers start only when needed, stop after inactivity
- **Stdio Communication**: All MCP servers use stdio for efficient communication
- **Resource Optimization**: Automatic shutdown after 5 minutes of inactivity
- **Centralized Management**: MCP Router manages all server communication
- **Monitoring & Logging**: Grafana dashboard and comprehensive logging
- **Production Security**: Non-root containers, read-only mounts, network isolation

## 📁 Directory Structure

```
/mnt/environments/prod/mcp-system/
├── logs/                    # All system logs
│   ├── router/             # Router logs
│   ├── resource-manager/   # Resource manager logs
│   └── containers/         # Container logs
├── volumes/                # Persistent volumes
│   ├── grafana/           # Grafana data
│   └── elasticsearch/     # Elasticsearch data
├── data/                  # Application data
│   ├── memory/            # Memory server data
│   └── repos/             # Git repository data
├── config/                # Configuration files
│   ├── router/            # Router configuration
│   └── grafana/           # Grafana configuration
├── images/                # Container images
└── repos/                 # Git repositories
```

## 🏗️ Architecture

### Core Services (Always Running)
- **MCP Router**: Central management and communication hub
- **Resource Manager**: Handles on-demand startup/shutdown
- **Grafana Monitor**: System monitoring and metrics

### On-Demand MCP Servers
- **filesystem**: File system operations
- **memory**: Memory-based data storage
- **fetch**: Web content fetching
- **everything**: Search functionality
- **sequentialthinking**: Sequential reasoning
- **time**: Time and date operations
- **git**: Git repository operations

## ⚙️ Configuration

### Environment Variables (`prod-config.env`)

```bash
# Production Drive Paths
PROD_ROOT="/mnt/environments/prod/mcp-system"
PROD_LOGS="${PROD_ROOT}/logs"
PROD_VOLUMES="${PROD_ROOT}/volumes"
PROD_DATA="${PROD_ROOT}/data"

# Resource Management
MAX_MEMORY_PER_CONTAINER="512M"
MAX_CPU_PER_CONTAINER="1.0"
AUTO_SHUTDOWN_TIMEOUT="300"  # 5 minutes
HEALTH_CHECK_INTERVAL="30"

# Stdio Communication
STDIO_ENABLED="true"
STDIO_BUFFER_SIZE="8192"
STDIO_TIMEOUT="30"
```

## 🚀 Deployment

### Prerequisites

1. **Production NVMe Drive**: Must be mounted at `/mnt/environments/prod`
2. **Podman**: Container runtime
3. **Node.js**: For router build
4. **Minimum 10GB**: Available space on production drive

### Quick Start

```bash
# 1. Deploy the production system
./deploy-prod.sh

# 2. Test the system
./test-prod.sh

# 3. Access the services
# Router Dashboard: http://localhost:8080
# Monitoring: http://localhost:3000 (admin/admin)
```

## 📊 Usage

### Starting a Server On-Demand

```bash
# Start filesystem server
curl -X POST http://localhost:8080/servers/filesystem/start

# Start memory server
curl -X POST http://localhost:8080/servers/memory/start

# Start git server
curl -X POST http://localhost:8080/servers/git/start
```

### Making MCP Requests

```bash
# List tools from filesystem server
curl -X POST http://localhost:8080/mcp/filesystem \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

### Stopping a Server

```bash
# Stop filesystem server
curl -X POST http://localhost:8080/servers/filesystem/stop
```

## 🔧 Management

### Checking System Status

```bash
# Check all containers
podman ps -a

# Check core services
podman ps --filter "name=mcp-router-prod"
podman ps --filter "name=mcp-monitor-prod"
podman ps --filter "name=mcp-resource-manager-prod"

# Check router health
curl http://localhost:8080/health
```

### Viewing Logs

```bash
# Router logs
tail -f /mnt/environments/prod/mcp-system/logs/router/router.log

# Resource manager logs
tail -f /mnt/environments/prod/mcp-system/logs/resource-manager/resource-manager.log

# Container logs
podman logs mcp-filesystem-prod
```

### Resource Monitoring

```bash
# Check resource usage
podman stats

# Check production drive usage
df -h /mnt/environments/prod/mcp-system

# Check container resource limits
podman inspect mcp-filesystem-prod | jq '.[0].HostConfig.Memory'
```

## 🔄 Auto-Shutdown Behavior

The system automatically manages container lifecycle:

1. **Startup**: Servers start when first requested
2. **Activity Tracking**: Router tracks all server activity
3. **Shutdown**: Servers stop after 5 minutes of inactivity
4. **Resource Cleanup**: Memory and CPU resources are freed

### Configuration

```bash
# Adjust auto-shutdown timeout (in seconds)
export AUTO_SHUTDOWN_TIMEOUT=600  # 10 minutes

# Adjust health check interval (in seconds)
export HEALTH_CHECK_INTERVAL=60   # 1 minute
```

## 📈 Monitoring

### Grafana Dashboard

Access Grafana at `http://localhost:3000`:
- **Username**: admin
- **Password**: admin

### Metrics Available

- Container resource usage (CPU, Memory)
- Server request frequency
- Auto-shutdown events
- Production drive I/O performance
- Network communication statistics

### Custom Dashboards

Create custom dashboards for:
- MCP server performance
- Resource utilization trends
- Error rates and response times
- Production drive performance metrics

## 🔒 Security

### Container Security

- **Non-root users**: All containers run as non-root
- **Read-only mounts**: Configurations mounted read-only
- **Network isolation**: Custom bridge network
- **Resource limits**: Memory and CPU limits per container

### Production Drive Security

```bash
# Check permissions
ls -la /mnt/environments/prod/mcp-system/

# Verify ownership
sudo chown -R daclab-work001:daclab-work001 /mnt/environments/prod/mcp-system/
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Production Drive Not Accessible

```bash
# Check if drive is mounted
df -h /mnt/environments/prod

# Remount if needed
sudo mount /dev/mapper/ubuntu--vg-prod--lv /mnt/environments/prod
```

#### 2. Container Won't Start

```bash
# Check container logs
podman logs mcp-filesystem-prod

# Check resource availability
podman system df

# Restart resource manager
podman restart mcp-resource-manager-prod
```

#### 3. Router Not Responding

```bash
# Check router status
podman ps --filter "name=mcp-router-prod"

# Check router logs
podman logs mcp-router-prod

# Restart router
podman restart mcp-router-prod
```

#### 4. Auto-Shutdown Not Working

```bash
# Check resource manager logs
tail -f /mnt/environments/prod/mcp-system/logs/resource-manager/resource-manager.log

# Check router activity tracking
curl http://localhost:8080/servers
```

### Performance Issues

#### 1. Slow Startup

```bash
# Check production drive performance
dd if=/dev/zero of=/mnt/environments/prod/mcp-system/test bs=1M count=100

# Check container image size
podman images
```

#### 2. High Memory Usage

```bash
# Check memory usage
podman stats --no-stream

# Adjust memory limits in prod-config.env
MAX_MEMORY_PER_CONTAINER="256M"
```

## 🔄 Maintenance

### Regular Maintenance Tasks

#### Daily
- Check system logs for errors
- Monitor resource usage
- Verify auto-shutdown is working

#### Weekly
- Review Grafana dashboards
- Clean up old logs
- Update container images

#### Monthly
- Review production drive space
- Update system configurations
- Performance optimization

### Backup Procedures

```bash
# Backup configurations
tar -czf mcp-config-backup-$(date +%Y%m%d).tar.gz /mnt/environments/prod/mcp-system/config/

# Backup data
tar -czf mcp-data-backup-$(date +%Y%m%d).tar.gz /mnt/environments/prod/mcp-system/data/

# Backup logs
tar -czf mcp-logs-backup-$(date +%Y%m%d).tar.gz /mnt/environments/prod/mcp-system/logs/
```

## 📋 API Reference

### Router Endpoints

#### Health Check
```bash
GET /health
Response: {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}
```

#### List Servers
```bash
GET /servers
Response: [{"name": "filesystem", "status": "running", "lastActivity": "2024-01-01T00:00:00Z"}]
```

#### Start Server
```bash
POST /servers/{name}/start
Response: {"success": true, "message": "Server started"}
```

#### Stop Server
```bash
POST /servers/{name}/stop
Response: {"success": true, "message": "Server stopped"}
```

#### MCP Request
```bash
POST /mcp/{server}
Content-Type: application/json
Body: {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
```

## 🎯 Performance Optimization

### Production Drive Optimization

```bash
# Check drive performance
hdparm -tT /dev/nvme2n1

# Optimize filesystem
sudo tune2fs -O has_journal /dev/mapper/ubuntu--vg-prod--lv
```

### Container Optimization

```bash
# Use multi-stage builds
# Enable compression
# Optimize base images
# Set appropriate resource limits
```

### Network Optimization

```bash
# Use custom bridge network
# Optimize DNS resolution
# Configure appropriate MTU
```

## 📞 Support

For issues or questions:

1. Check the logs in `/mnt/environments/prod/mcp-system/logs/`
2. Review the troubleshooting section
3. Check Grafana dashboards for metrics
4. Verify production drive health

## 📄 License

This production MCP system is designed for high-performance, resource-efficient deployment of Model Context Protocol servers with on-demand container management. 