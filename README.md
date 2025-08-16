# MCP (Model Context Protocol) Directory

This directory contains all MCP-related servers, configurations, and documentation in a consolidated structure.

## Directory Structure

```
mcp/
├── servers/                    # MCP servers and related components
│   ├── src/                   # Individual MCP servers
│   │   ├── filesystem/        # Node.js filesystem server
│   │   ├── memory/           # Node.js memory server
│   │   ├── everything/       # Node.js everything server
│   │   ├── sequentialthinking/ # Node.js sequential thinking server
│   │   ├── fetch/            # Python fetch server
│   │   ├── time/             # Python time server
│   │   └── git/              # Python git server
│   ├── router/               # MCP router component
│   ├── resource-manager/     # Resource management component
│   ├── build-all.sh         # Build script for all servers
│   ├── deploy-prod.sh       # Production deployment script
│   └── package.json         # Main package configuration
├── configs/                  # MCP configuration files
│   └── config.json          # Main MCP configuration
├── docs/                    # MCP documentation
│   └── extract_mcp_servers/ # Pattern documentation
└── README.md               # This file
```

## Quick Start

### Building MCP Servers
```bash
cd /home/daclab-work001/DEV/mcp/servers
./build-all.sh
```

### Production Deployment
```bash
cd /home/daclab-work001/DEV/mcp/servers
./deploy-prod.sh
```

## Server Types

### Node.js Servers
- **filesystem**: File system operations
- **memory**: Memory management and storage
- **everything**: Comprehensive MCP server
- **sequentialthinking**: Sequential reasoning support
- **obsidian-mcp**: Obsidian vault integration
- **read-website-fast**: Fast web content extraction and markdown conversion

### Python Servers  
- **fetch**: HTTP/web content fetching
- **time**: Time-related operations
- **git**: Git repository operations
- **postgres-mcp**: PostgreSQL database integration with health monitoring

## Configuration

Configuration files are located in the `configs/` directory:
- `config.json`: Main MCP configuration for local/remote servers
- `docker-compose-additional.yml`: Docker Compose for Obsidian and PostgreSQL servers
- `warp-mcp-config-additional.json`: Warp Terminal MCP configuration
- `additional.env`: Environment variables for additional servers

## Components

### Router
The MCP router handles request routing between clients and servers, providing:
- Load balancing
- Health monitoring
- Automatic server lifecycle management

### Resource Manager
Manages server resources including:
- Container lifecycle management
- Resource optimization
- Monitoring and alerting

## Migration Notes

This directory consolidates MCP components that were previously scattered across:
- `/home/daclab-work001/DEV/terraform/mcp/` (removed)
- `/home/daclab-work001/DEV/configs/.config/mcp/` (copied here)
- `/home/daclab-work001/mcp-servers/` (removed completely)
- `/home/daclab-work001/mcp-read-website-fast/` (moved here)
- Documentation from various project locations

All path references in scripts have been updated to reflect the new structure.

### Total MCP Servers: 11
- **7 Core servers** (filesystem, memory, everything, sequentialthinking, fetch, time, git)
- **4 Specialized servers** (obsidian-mcp, postgres-mcp, read-website-fast)

## Additional Servers Management

For the specialized servers (Obsidian, PostgreSQL), use the management scripts:
```bash
# Obsidian MCP Server
./manage-obsidian-mcp.sh start
./manage-obsidian-mcp.sh status

# PostgreSQL MCP Server  
./manage-postgres-mcp.sh start
./manage-postgres-mcp.sh status
```

## Development

Each server can be built individually by navigating to its directory and running:
```bash
# For Node.js servers
npm install
npm run build

# For Python servers
pip install -e .
```

Docker/Podman images are created with the naming convention: `mcp-{server-name}:latest`
