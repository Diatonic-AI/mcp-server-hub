# MCP Servers Directory

This directory contains all Model Context Protocol (MCP) servers configured for Docker-based stdio transport.

## Current Servers

### Obsidian MCP Server

**Status**: ✅ Installed and configured  
**Purpose**: Provides MCP access to Markdown notes in an Obsidian vault  
**Vault Path**: `/home/daclab-work001/Documents/steve-heaney-investments`

### PostgreSQL MCP Server

**Status**: ✅ Installed and configured  
**Purpose**: Provides MCP access to PostgreSQL databases with health monitoring, query analysis, and index tuning  
**Source**: https://github.com/crystaldba/postgres-mcp  
**Access Mode**: Restricted (read-only) by default

#### Quick Start

```bash
# Start the Obsidian MCP server
./manage-obsidian-mcp.sh start

# Check server status
./manage-obsidian-mcp.sh status

# View server logs
./manage-obsidian-mcp.sh logs

# Stop the server
./manage-obsidian-mcp.sh stop
```

#### Docker Configuration

The Obsidian MCP server can be run using Docker with the following configuration:

```bash
docker run -i --rm \
  -v "/home/daclab-work001/Documents/steve-heaney-investments:/vault:ro" \
  obsidian-mcp:latest /vault
```

#### Warp Terminal Integration

Add this configuration to your Warp MCP settings:

```json
{
  "obsidian-mcp": {
    "command": "docker",
    "args": [
      "run",
      "-i",
      "--rm",
      "-v",
      "/home/daclab-work001/Documents/steve-heaney-investments:/vault:ro",
      "obsidian-mcp:latest",
      "/vault"
    ],
    "env": {},
    "working_directory": null,
    "start_on_launch": true
  }
}
```

## Directory Structure

```
/home/daclab-work001/mcp-servers/
├── obsidian-mcp/              # Obsidian MCP server source code
│   ├── Dockerfile             # Docker build configuration
│   ├── package.json           # Node.js dependencies
│   ├── dist/                  # Compiled TypeScript
│   └── ...
├── docker-compose.yml         # Docker Compose configuration
├── .env                       # Environment variables
├── warp-mcp-config.json      # Warp Terminal MCP configuration
├── manage-obsidian-mcp.sh    # Management script
└── README.md                 # This file
```

## Management Commands

The `manage-obsidian-mcp.sh` script provides convenient commands:

- `start` - Start the Obsidian MCP server
- `stop` - Stop the Obsidian MCP server  
- `restart` - Restart the Obsidian MCP server
- `status` - Check if the server is running
- `logs` - Show server logs (follow mode)
- `shell` - Open a shell in the running container
- `test` - Test MCP server connection
- `rebuild` - Rebuild the Docker image

## Available Tools

The Obsidian MCP server provides the following tools:

- **search_notes** - Search through notes using text queries
- **read_note** - Read the content of a specific note
- **list_notes** - List all notes in the vault
- **get_note_metadata** - Get metadata for a specific note

## Troubleshooting

### Server Won't Start
1. Check if Docker is running: `docker ps`
2. Verify the vault path exists: `ls -la /home/daclab-work001/Documents/steve-heaney-investments`
3. Check Docker image exists: `docker images | grep obsidian-mcp`

### Connection Issues
1. Test the server directly: `./manage-obsidian-mcp.sh test`
2. Check server logs: `./manage-obsidian-mcp.sh logs`
3. Verify port availability and permissions

### Vault Access Issues
1. Ensure the vault directory has proper read permissions
2. Check that the mount path is correct in the Docker configuration
3. Verify the OBSIDIAN_VAULT_PATH environment variable

## Adding More MCP Servers

To add additional MCP servers to this directory:

1. Create a new subdirectory: `mkdir -p /home/daclab-work001/mcp-servers/new-server`
2. Add the server source code and Dockerfile
3. Update `docker-compose.yml` to include the new service
4. Add configuration to `warp-mcp-config.json`
5. Create or update management scripts as needed

## Environment Variables

Current environment variables in `.env`:

- `OBSIDIAN_VAULT_PATH=/vault` - Path to the Obsidian vault inside the container

## Security Notes

- The Obsidian vault is mounted read-only (`ro`) for security
- No sensitive credentials are stored in plain text
- All MCP servers run in isolated Docker containers
- Network access is restricted to the mcp-network bridge

## Support

For issues with specific MCP servers:
- Obsidian MCP: https://github.com/smithery-ai/mcp-obsidian

For general MCP questions:
- MCP Documentation: https://modelcontextprotocol.io/
