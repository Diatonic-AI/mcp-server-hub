#!/bin/bash

# PostgreSQL MCP Server Management Script
# Usage: ./manage-postgres-mcp.sh [start|stop|restart|status|logs|shell|test|rebuild]

set -e

CONTAINER_NAME="postgres-mcp-server"
IMAGE_NAME="postgres-mcp:latest"

case "$1" in
    start)
        echo "Starting PostgreSQL MCP server..."
        docker-compose up -d postgres-mcp
        echo "PostgreSQL MCP server started successfully!"
        ;;
    
    stop)
        echo "Stopping PostgreSQL MCP server..."
        docker-compose stop postgres-mcp
        echo "PostgreSQL MCP server stopped."
        ;;
    
    restart)
        echo "Restarting PostgreSQL MCP server..."
        docker-compose restart postgres-mcp
        echo "PostgreSQL MCP server restarted."
        ;;
    
    status)
        echo "Checking PostgreSQL MCP server status..."
        if docker ps | grep -q $CONTAINER_NAME; then
            echo "✓ PostgreSQL MCP server is running"
            docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        else
            echo "✗ PostgreSQL MCP server is not running"
        fi
        ;;
    
    logs)
        echo "Showing PostgreSQL MCP server logs..."
        docker-compose logs -f postgres-mcp
        ;;
    
    shell)
        echo "Opening shell in PostgreSQL MCP server..."
        docker exec -it $CONTAINER_NAME /bin/bash
        ;;
    
    test)
        echo "Testing PostgreSQL MCP server connection..."
        if [ -z "$POSTGRES_DATABASE_URI" ]; then
            echo "ERROR: POSTGRES_DATABASE_URI environment variable not set"
            echo "Please set it in .env file or export it:"
            echo "export POSTGRES_DATABASE_URI='postgresql://username:password@localhost:5432/dbname'"
            exit 1
        fi
        
        docker run --rm -i \
            -e "DATABASE_URI=$POSTGRES_DATABASE_URI" \
            $IMAGE_NAME --access-mode=restricted <<< '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}'
        ;;
    
    test-sse)
        echo "Testing PostgreSQL MCP server with SSE transport..."
        if [ -z "$POSTGRES_DATABASE_URI" ]; then
            echo "ERROR: POSTGRES_DATABASE_URI environment variable not set"
            exit 1
        fi
        
        echo "Starting PostgreSQL MCP server in SSE mode on port 8001..."
        docker run --rm -d -p 8001:8000 \
            -e "DATABASE_URI=$POSTGRES_DATABASE_URI" \
            --name postgres-mcp-sse-test \
            $IMAGE_NAME --access-mode=restricted --transport=sse
        
        sleep 3
        echo "Testing SSE endpoint..."
        curl -s http://localhost:8001/sse || echo "SSE endpoint test completed"
        
        echo "Stopping test container..."
        docker stop postgres-mcp-sse-test
        ;;
    
    rebuild)
        echo "Rebuilding PostgreSQL MCP Docker image..."
        cd postgres-mcp
        docker build -t $IMAGE_NAME .
        cd ..
        echo "PostgreSQL MCP image rebuilt successfully!"
        ;;
    
    tools)
        echo "Available PostgreSQL MCP tools:"
        echo "  • get_schema - Get database schema information"
        echo "  • analyze_schema - Analyze schema for performance insights"
        echo "  • get_database_health - Check database health metrics"
        echo "  • list_tables - List all tables with details"
        echo "  • describe_table - Get detailed table information"
        echo "  • execute_sql - Execute SQL statements (restricted mode = read-only)"
        echo "  • explain_query - Get query execution plans"
        echo "  • get_top_queries - Get slowest queries from pg_stat_statements"
        echo "  • analyze_workload_indexes - Analyze and recommend indexes"
        echo "  • get_connection_info - Get database connection information"
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|shell|test|test-sse|rebuild|tools}"
        echo ""
        echo "Commands:"
        echo "  start     - Start the PostgreSQL MCP server"
        echo "  stop      - Stop the PostgreSQL MCP server"
        echo "  restart   - Restart the PostgreSQL MCP server"
        echo "  status    - Check if the server is running"
        echo "  logs      - Show server logs (follow mode)"
        echo "  shell     - Open a shell in the running container"
        echo "  test      - Test MCP server connection (stdio mode)"
        echo "  test-sse  - Test MCP server in SSE mode"
        echo "  rebuild   - Rebuild the Docker image"
        echo "  tools     - List available MCP tools"
        echo ""
        echo "Environment Variables:"
        echo "  POSTGRES_DATABASE_URI - PostgreSQL connection string"
        echo "    Example: postgresql://user:pass@host:5432/dbname"
        exit 1
        ;;
esac
