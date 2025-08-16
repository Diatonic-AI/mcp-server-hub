# MCP Servers Production Deployment Guide

## Overview

This guide provides a complete production-ready deployment solution for Model Context Protocol (MCP) servers using Podman Desktop. The setup includes all reference MCP servers from the official repository, configured for stdio communication in production containers.

## 🎯 What We've Built

### 1. **Complete Containerized MCP Infrastructure**
- **7 Reference MCP Servers**: filesystem, memory, git, fetch, everything, sequentialthinking, time
- **MCP Router**: Centralized management and proxy for all servers
- **Monitoring Stack**: Grafana for visualization and metrics
- **Production-Ready**: Optimized for stdio communication and container orchestration

### 2. **Key Features**
- ✅ **Stdio Communication**: All servers use stdio for production-grade communication
- ✅ **Podman Desktop Integration**: Native support for Podman Desktop
- ✅ **Centralized Management**: Single router for all MCP servers
- ✅ **Monitoring & Logging**: Built-in monitoring with Grafana
- ✅ **Security**: Isolated network, read-only mounts, proper permissions
- ✅ **Scalability**: Horizontal and vertical scaling support
- ✅ **Health Checks**: Comprehensive health monitoring
- ✅ **One-Command Deployment**: Automated deployment script

## 📁 Project Structure

```
core-mcp/
├── servers/                    # Cloned MCP servers repository
│   ├── src/
│   │   ├── filesystem/        # Filesystem MCP server
│   │   ├── memory/           # Memory MCP server
│   │   ├── git/              # Git MCP server
│   │   ├── fetch/            # Fetch MCP server
│   │   ├── everything/       # Everything MCP server
│   │   ├── sequentialthinking/ # Sequential thinking MCP server
│   │   └── time/             # Time MCP server
├── router/                    # MCP Router for centralized management
│   ├── src/
│   │   └── index.ts          # Router application
│   ├── config/
│   │   └── servers.json      # Server configurations
│   ├── Dockerfile            # Router container
│   └── package.json          # Router dependencies
├── docker-compose.yml         # Docker Compose configuration
├── deploy-podman.sh          # Automated deployment script
├── test-mcp.sh              # Test and validation script
├── README.md                 # Main documentation
└── DEPLOYMENT_GUIDE.md       # This guide
```

## 🚀 Quick Deployment

### Prerequisites
1. **Podman Desktop**: Install from [podman-desktop.io](https://podman-desktop.io/)
2. **Node.js**: For building the router
3. **Git**: For cloning repositories

### One-Command Deployment
```bash
# Clone and setup
git clone <repository-url>
cd core-mcp

# Deploy everything
./deploy-podman.sh

# Test the deployment
./test-mcp.sh
```

## 🔧 Architecture Details

### Container Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Client    │    │   MCP Router    │    │   MCP Servers   │
│   (Claude,      │◄──►│   (Port 8080)   │◄──►│   (Containers)  │
│   Cursor, etc.) │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Monitoring    │
                       │   (Grafana)     │
                       └─────────────────┘
```

### Network Configuration
- **Network**: `mcp-network` (isolated bridge network)
- **Router Port**: 8080 (HTTP API)
- **Monitoring Port**: 3000 (Grafana)
- **Internal Communication**: stdio via router

### Volume Mounts
- **Data**: `./data` → `/data` (shared data)
- **Repositories**: `./data/repos` → `/repos` (git repos)
- **Logs**: `./logs` → `/app/logs` (application logs)
- **Config**: `./router/config` → `/app/config` (router config)

## 📊 Monitoring & Management

### Router Dashboard
- **URL**: http://localhost:8080
- **Endpoints**:
  - `GET /health` - Health check
  - `GET /servers` - List all servers
  - `POST /servers/{name}/start` - Start server
  - `POST /servers/{name}/stop` - Stop server
  - `POST /mcp/{server}` - Forward MCP request

### Grafana Monitoring
- **URL**: http://localhost:3000
- **Credentials**: admin/admin
- **Metrics**: Container resources, MCP request latency, error rates

### Logs
```bash
# View router logs
podman logs mcp-router

# View specific server logs
podman logs mcp-filesystem
podman logs mcp-memory

# Follow logs in real-time
podman logs -f mcp-router
```

## 🔒 Security Features

### Network Security
- ✅ Isolated `mcp-network`
- ✅ Only router exposes HTTP port
- ✅ Internal communication via stdio
- ✅ No direct external access to servers

### Container Security
- ✅ Non-root users in containers
- ✅ Read-only mounts for sensitive data
- ✅ Minimal container images
- ✅ Proper signal handling with dumb-init

### Data Security
- ✅ Environment variables for secrets
- ✅ No secrets in container images
- ✅ Proper file permissions
- ✅ Container user isolation

## 📈 Scaling & Performance

### Horizontal Scaling
```bash
# Scale specific servers
podman-compose up -d --scale mcp-filesystem=3

# Router automatically load balances requests
```

### Vertical Scaling
```bash
# Increase container resources
podman run --cpus=2 --memory=2g mcp-memory:latest
```

### Performance Optimization
- ✅ Multi-stage builds for smaller images
- ✅ Alpine Linux base images
- ✅ Production-only dependencies
- ✅ Optimized stdio communication

## 🛠️ Development & Customization

### Adding New Servers
1. **Add server configuration** in `router/config/servers.json`
2. **Add to deployment script** in `deploy-podman.sh`
3. **Rebuild and deploy**

### Custom Server Development
1. **Create server directory** in `servers/src/`
2. **Add Dockerfile** for containerization
3. **Add to router configuration**
4. **Test with deployment script**

### Configuration Management
- **Server Configs**: `router/config/servers.json`
- **Environment Variables**: Set in deployment script
- **Volume Mounts**: Configured in docker-compose.yml
- **Network Settings**: Isolated mcp-network

## 🔄 Maintenance & Updates

### Regular Maintenance
```bash
# Update all containers
podman-compose pull
podman-compose up -d --force-recreate

# Clean up unused resources
podman system prune -a

# Backup data
tar -czf mcp-backup-$(date +%Y%m%d).tar.gz ./data ./logs
```

### Monitoring & Alerts
- **Health Checks**: Automatic container health monitoring
- **Resource Monitoring**: CPU, memory, network usage
- **Error Tracking**: Comprehensive logging and error reporting
- **Performance Metrics**: Request latency and throughput

## 🧪 Testing & Validation

### Automated Testing
```bash
# Run comprehensive tests
./test-mcp.sh
```

### Test Coverage
- ✅ Container status verification
- ✅ Router health checks
- ✅ MCP stdio communication
- ✅ File operations testing
- ✅ Memory operations testing
- ✅ Performance benchmarking
- ✅ Monitoring validation

## 📚 Integration Examples

### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "router": {
      "command": "curl",
      "args": ["-X", "POST", "http://localhost:8080/mcp/filesystem"]
    }
  }
}
```

### Cursor Configuration
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "curl",
      "args": ["-X", "POST", "http://localhost:8080/mcp/filesystem"]
    },
    "memory": {
      "command": "curl",
      "args": ["-X", "POST", "http://localhost:8080/mcp/memory"]
    }
  }
}
```

## 🎯 Production Checklist

### Before Deployment
- [ ] Podman Desktop installed and running
- [ ] Node.js available for router build
- [ ] Git repositories cloned
- [ ] Network ports available (8080, 3000)
- [ ] Sufficient disk space for containers

### After Deployment
- [ ] All containers running (`podman ps`)
- [ ] Router responding (`curl http://localhost:8080/health`)
- [ ] Monitoring accessible (`curl http://localhost:3000`)
- [ ] MCP communication working (run `./test-mcp.sh`)
- [ ] Logs accessible and clean
- [ ] Performance acceptable

### Security Verification
- [ ] No secrets in container images
- [ ] Read-only mounts for sensitive data
- [ ] Network isolation working
- [ ] Non-root users in containers
- [ ] Proper file permissions

## 🆘 Troubleshooting

### Common Issues

1. **Container Build Failures**
   ```bash
   # Check build logs
   podman logs mcp-router
   
   # Rebuild specific container
   podman build -t mcp-filesystem:latest ./servers/src/filesystem
   ```

2. **Network Issues**
   ```bash
   # Check network
   podman network ls
   podman network inspect mcp-network
   ```

3. **Permission Issues**
   ```bash
   # Fix directory permissions
   sudo chown -R $USER:$USER ./data ./logs
   ```

4. **Router Not Responding**
   ```bash
   # Check router logs
   podman logs mcp-router
   
   # Restart router
   podman restart mcp-router
   ```

### Debug Commands
```bash
# Check container status
podman ps -a

# View container logs
podman logs <container-name>

# Execute commands in container
podman exec -it <container-name> /bin/sh

# Check network connectivity
podman network inspect mcp-network

# Monitor resource usage
podman stats
```

## 🎉 Success Metrics

### Deployment Success
- ✅ All containers running and healthy
- ✅ Router responding to health checks
- ✅ MCP stdio communication working
- ✅ Monitoring dashboard accessible
- ✅ File and memory operations functional
- ✅ Performance within acceptable limits

### Production Readiness
- ✅ Security best practices implemented
- ✅ Monitoring and alerting configured
- ✅ Backup and recovery procedures in place
- ✅ Documentation complete and accurate
- ✅ Testing procedures validated

## 📞 Support & Resources

### Documentation
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Podman Desktop](https://docs.podman-desktop.io/)
- [Official MCP Servers](https://github.com/modelcontextprotocol/servers)

### Community
- [MCP Discord](https://discord.gg/jHEGxQu2a5)
- [GitHub Discussions](https://github.com/orgs/modelcontextprotocol/discussions)
- [Reddit Community](https://www.reddit.com/r/modelcontextprotocol/)

---

**🎯 Mission Accomplished**: You now have a complete, production-ready MCP servers deployment using Podman Desktop with stdio communication, centralized management, monitoring, and comprehensive testing. The setup is optimized for production use and includes all the necessary components for a robust MCP infrastructure. 