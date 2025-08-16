#!/bin/bash

# Obsidian MCP Server Management Script
# Usage: ./manage-obsidian-mcp.sh [start|stop|restart|status|logs|shell]

set -e

CONTAINER_NAME="obsidian-mcp-server"
IMAGE_NAME="obsidian-mcp:latest"
VAULT_PATH="/home/daclab-work001/Documents/steve-heaney-investments"

case "$1" in
    start)
        echo "Starting Obsidian MCP server..."
        docker-compose -f ../configs/docker-compose-additional.yml up -d obsidian-mcp
        echo "Obsidian MCP server started successfully!"
        ;;
    
    stop)
        echo "Stopping Obsidian MCP server..."
        docker-compose -f ../configs/docker-compose-additional.yml down
        echo "Obsidian MCP server stopped."
        ;;
    
    restart)
        echo "Restarting Obsidian MCP server..."
        docker-compose -f ../configs/docker-compose-additional.yml restart obsidian-mcp
        echo "Obsidian MCP server restarted."
        ;;
    
    status)
        echo "Checking Obsidian MCP server status..."
        if docker ps | grep -q $CONTAINER_NAME; then
            echo "✓ Obsidian MCP server is running"
            docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        else
            echo "✗ Obsidian MCP server is not running"
        fi
        ;;
    
    logs)
        echo "Showing Obsidian MCP server logs..."
        docker-compose -f ../configs/docker-compose-additional.yml logs -f obsidian-mcp
        ;;
    
    shell)
        echo "Opening shell in Obsidian MCP server..."
        docker exec -it $CONTAINER_NAME /bin/bash
        ;;
    
    test)
        echo "Testing Obsidian MCP server connection..."
        docker run --rm -i \
            -v "$VAULT_PATH:/vault:ro" \
            $IMAGE_NAME /vault <<< '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}'
        ;;
    
    rebuild)
        echo "Rebuilding Obsidian MCP Docker image..."
        cd src/obsidian-mcp
        docker build -t $IMAGE_NAME .
        cd ../..
        echo "Obsidian MCP image rebuilt successfully!"
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|shell|test|rebuild}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the Obsidian MCP server"
        echo "  stop     - Stop the Obsidian MCP server"
        echo "  restart  - Restart the Obsidian MCP server"
        echo "  status   - Check if the server is running"
        echo "  logs     - Show server logs (follow mode)"
        echo "  shell    - Open a shell in the running container"
        echo "  test     - Test MCP server connection"
        echo "  rebuild  - Rebuild the Docker image"
        exit 1
        ;;
esac
