#!/bin/bash

# MCP Servers Build Script
# This script builds all MCP server images individually with proper tagging

set -e

echo "========================================"
echo "Starting MCP Servers Build Process"
echo "========================================"

# Define the servers and their types
declare -A SERVERS=(
    ["filesystem"]="node"
    ["memory"]="node"
    ["everything"]="node"
    ["sequentialthinking"]="node"
    ["fetch"]="python"
    ["time"]="python"
    ["git"]="python"
    ["obsidian-mcp"]="node"
    ["postgres-mcp"]="python"
    ["read-website-fast"]="node"
)

# Base directory
BASE_DIR="/home/daclab-work001/DEV/mcp/servers"
SERVERS_DIR="$BASE_DIR/src"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to build Node.js servers
build_node_server() {
    local server_name=$1
    local server_path="$SERVERS_DIR/$server_name"
    
    print_status "Building Node.js server: $server_name"
    
    if [ ! -d "$server_path" ]; then
        print_error "Server directory not found: $server_path"
        return 1
    fi
    
    cd "$server_path"
    
    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        print_error "package.json not found in $server_path"
        return 1
    fi
    
    # Install dependencies and build
    print_status "Installing dependencies for $server_name..."
    npm install
    
    print_status "Building TypeScript for $server_name..."
    npm run build
    
    # Build Docker image
    print_status "Building Docker image: mcp-$server_name:latest"
    podman build -t "mcp-$server_name:latest" .
    
    if [ $? -eq 0 ]; then
        print_status "✓ Successfully built mcp-$server_name:latest"
    else
        print_error "✗ Failed to build mcp-$server_name:latest"
        return 1
    fi
}

# Function to build Python servers
build_python_server() {
    local server_name=$1
    local server_path="$SERVERS_DIR/$server_name"
    
    print_status "Building Python server: $server_name"
    
    if [ ! -d "$server_path" ]; then
        print_error "Server directory not found: $server_path"
        return 1
    fi
    
    cd "$server_path"
    
    # Check if pyproject.toml exists
    if [ ! -f "pyproject.toml" ]; then
        print_error "pyproject.toml not found in $server_path"
        return 1
    fi
    
    # Build Docker image
    print_status "Building Docker image: mcp-$server_name:latest"
    podman build -t "mcp-$server_name:latest" .
    
    if [ $? -eq 0 ]; then
        print_status "✓ Successfully built mcp-$server_name:latest"
    else
        print_error "✗ Failed to build mcp-$server_name:latest"
        return 1
    fi
}

# Main build process
main() {
    print_status "Starting individual server builds..."
    
    local failed_builds=()
    
    for server in "${!SERVERS[@]}"; do
        server_type="${SERVERS[$server]}"
        
        echo ""
        echo "----------------------------------------"
        print_status "Processing $server ($server_type)"
        echo "----------------------------------------"
        
        case $server_type in
            "node")
                if ! build_node_server "$server"; then
                    failed_builds+=("$server")
                fi
                ;;
            "python")
                if ! build_python_server "$server"; then
                    failed_builds+=("$server")
                fi
                ;;
            *)
                print_error "Unknown server type: $server_type for $server"
                failed_builds+=("$server")
                ;;
        esac
    done
    
    echo ""
    echo "========================================"
    print_status "Build Summary"
    echo "========================================"
    
    if [ ${#failed_builds[@]} -eq 0 ]; then
        print_status "✓ All servers built successfully!"
        
        echo ""
        print_status "Built Images:"
        podman images | grep "mcp-"
        
        echo ""
        print_status "You can now run the deployment script: ./deploy-prod.sh"
    else
        print_error "✗ Some builds failed:"
        for failed in "${failed_builds[@]}"; do
            print_error "  - $failed"
        done
        exit 1
    fi
}

# Run the main function
main "$@"
