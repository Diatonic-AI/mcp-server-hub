#!/bin/bash

echo "Testing MCP Servers with stdio commands..."
echo "=========================================="

# Test function for MCP servers
test_mcp_server() {
    local server_name=$1
    local image_name=$2
    local extra_args=$3
    
    echo "Testing $server_name..."
    
    # Create a temporary file with the commands
    cat > /tmp/mcp_test.json << EOF
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}
{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
EOF

    # Run the server with a timeout
    timeout 10s podman run -i --rm $extra_args $image_name < /tmp/mcp_test.json
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "✓ $server_name responded successfully"
    elif [ $exit_code -eq 124 ]; then
        echo "⚠ $server_name timed out (may be waiting for more input)"
    else
        echo "✗ $server_name failed with exit code $exit_code"
    fi
    echo ""
    
    # Clean up
    rm -f /tmp/mcp_test.json
}

# Test all servers
test_mcp_server "Filesystem Server" "mcp-filesystem:latest" "-v /tmp:/data"
test_mcp_server "Memory Server" "mcp-memory:latest"
test_mcp_server "Fetch Server" "mcp-fetch:latest" 
test_mcp_server "Time Server" "mcp-time:latest"
test_mcp_server "Git Server" "mcp-git:latest" "-v /tmp:/repos"
test_mcp_server "Everything Server" "mcp-everything:latest"
test_mcp_server "Sequential Thinking Server" "mcp-sequentialthinking:latest"

echo "Testing completed!"
