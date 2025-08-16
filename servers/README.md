# MCP Servers Production Deployment with Podman Desktop

This repository contains a complete production-ready deployment setup for Model Context Protocol (MCP) servers using Podman Desktop. The setup includes all reference MCP servers from the official repository, configured for stdio communication in production containers.

## 🚀 Quick Start

### Prerequisites

1. **Podman Desktop** - Install from [podman-desktop.io](https://podman-desktop.io/)
2. **Node.js** (for building the router)
3. **Git** (for cloning repositories)

### One-Command Deployment

```bash
# Make the deployment script executable
chmod +x deploy-podman.sh

# Run the deployment
./deploy-podman.sh
```

This will:
- Build all MCP server containers
- Create a Podman network
- Deploy all services with proper stdio communication
- Set up monitoring and logging
- Perform health checks

## 📋 Included MCP Servers

### Reference Servers (Official)
- **Filesystem** - Secure file operations with configurable access controls
- **Memory** - Knowledge graph-based persistent memory system
- **Git** - Tools to read, search, and manipulate Git repositories
- **Fetch** - Web content fetching and conversion for efficient LLM usage
- **Everything** - Reference/test server with prompts, resources, and tools
- **Sequential Thinking** - Dynamic problem-solving through thought sequences
- **Time** - Time and timezone conversion capabilities

### Infrastructure Components
- **MCP Router** - Centralized management and proxy for all servers
- **Grafana** - Monitoring and visualization dashboard
- **Elasticsearch** - Log aggregation and search

## 🏗️ Architecture

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

## 🔧 Configuration

### MCP Router Configuration

The router configuration is located in `router/config/servers.json`:

```json
{
  "servers": {
    "filesystem": {
      "name": "filesystem",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/data"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  },
  "router": {
    "port": 8080,
    "host": "0.0.0.0",
    "logLevel": "info",
    "autoStart": true
  }
}
```

### Volume Mounts

- **Data Directory**: `./data` - Shared data for filesystem and memory servers
- **Repositories**: `./data/repos` - Git repositories for the git server
- **Logs**: `./logs` - Application logs
- **Configuration**: `./router/config` - Router configuration

## 🌐 API Endpoints

### Router API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/servers` | List all servers |
| POST | `/servers/{name}/start` | Start a server |
| POST | `/servers/{name}/stop` | Stop a server |
| POST | `/mcp/{server}` | Forward MCP request |

### Example Usage

```bash
# Health check
curl http://localhost:8080/health

# List servers
curl http://localhost:8080/servers

# Start filesystem server
curl -X POST http://localhost:8080/servers/filesystem/start

# Send MCP request
curl -X POST http://localhost:8080/mcp/filesystem \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/list",
    "params": {}
  }'
```

## 📊 Monitoring

### Grafana Dashboard
- **URL**: http://localhost:3000
- **Username**: admin
- **Password**: admin

### Metrics Available
- Container resource usage (CPU, Memory, Network)
- MCP request latency and throughput
- Server health status
- Error rates and logs

## 🔍 Troubleshooting

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

## 🛠️ Development

### Adding New Servers

1. **Create server configuration** in `router/config/servers.json`:
   ```json
   {
     "name": "new-server",
     "command": "npx",
     "args": ["-y", "@modelcontextprotocol/server-new"],
     "env": {
       "NODE_ENV": "production"
     }
   }
   ```

2. **Add to deployment script** in `deploy-podman.sh`:
   ```bash
   local servers=("filesystem" "memory" "new-server")
   ```

3. **Rebuild and deploy**:
   ```bash
   ./deploy-podman.sh
   ```

### Custom Server Development

1. **Create server directory**:
   ```bash
   mkdir -p servers/src/my-server
   cd servers/src/my-server
   ```

2. **Add Dockerfile**:
   ```dockerfile
   FROM node:22.12-alpine
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci --only=production
   COPY . .
   CMD ["node", "dist/index.js"]
   ```

3. **Add to deployment** and rebuild.

## 🔒 Security Considerations

### Production Security

1. **Network Security**
   - All containers run on isolated `mcp-network`
   - Only router exposes HTTP port (8080)
   - Internal communication via stdio

2. **File System Security**
   - Read-only mounts for sensitive data
   - Proper file permissions
   - Container user isolation

3. **Environment Variables**
   - No secrets in container images
   - Use environment files for sensitive data
   - Rotate credentials regularly

### Security Best Practices

```bash
# Use secrets for sensitive data
podman secret create db-password ./secrets/db-password.txt

# Run containers with minimal privileges
podman run --security-opt no-new-privileges mcp-filesystem:latest

# Regular security updates
podman system prune -a
```

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale specific servers
podman-compose up -d --scale mcp-filesystem=3

# Load balancing with router
# Router automatically distributes requests across instances
```

### Vertical Scaling

```bash
# Increase container resources
podman run --cpus=2 --memory=2g mcp-memory:latest
```

## 🔄 Updates and Maintenance

### Updating Servers

```bash
# Pull latest images
podman-compose pull

# Update and restart
podman-compose up -d --force-recreate
```

### Backup and Restore

```bash
# Backup data
tar -czf mcp-backup-$(date +%Y%m%d).tar.gz ./data ./logs

# Restore data
tar -xzf mcp-backup-20240101.tar.gz
```

## 📚 Additional Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Podman Desktop Documentation](https://docs.podman-desktop.io/)
- [Official MCP Servers Repository](https://github.com/modelcontextprotocol/servers)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with the deployment script
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Note**: This deployment is optimized for production use with Podman Desktop. For development environments, consider using the individual server commands directly as documented in the official MCP servers repository. 