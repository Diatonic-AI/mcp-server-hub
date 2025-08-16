#!/bin/bash

# MCP Server Startup Script (Linux/macOS/WSL2)
set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[MCP]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[MCP]${NC} $1"
}

error() {
    echo -e "${RED}[MCP]${NC} $1"
}

# Check if we're in the right directory
if [[ ! -f "credential-manager.js" ]]; then
    error "Please run this script from the MCP project root directory"
    exit 1
fi

# Detect platform
PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
case "$PLATFORM" in
    linux*)
        if grep -q Microsoft /proc/version 2>/dev/null; then
            PLATFORM="wsl2"
        else
            PLATFORM="linux"
        fi
        ;;
    darwin*)
        PLATFORM="linux" # Use Linux config for macOS
        ;;
esac

log "Detected platform: $PLATFORM"

# Check for required tools
check_requirements() {
    local missing=()
    
    if ! command -v node >/dev/null 2>&1; then
        missing+=("Node.js")
    fi
    
    if ! command -v python3 >/dev/null 2>&1; then
        missing+=("Python 3")
    fi
    
    if ! command -v git >/dev/null 2>&1; then
        missing+=("Git")
    fi
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        error "Missing required tools: ${missing[*]}"
        error "Please install the missing tools and try again"
        exit 1
    fi
}

# Setup function
setup() {
    log "Setting up MCP environment..."
    
    # Generate credential template
    node credential-manager.js generate
    
    # Create Python virtual environment if it doesn't exist
    if [[ ! -d "mcp-python-env" ]]; then
        log "Creating Python virtual environment..."
        python3 -m venv mcp-python-env
        source mcp-python-env/bin/activate
        pip install --upgrade pip
        
        # Install Python MCP servers
        if [[ -f "setup-python-servers.sh" ]]; then
            chmod +x setup-python-servers.sh
            ./setup-python-servers.sh
        fi
    fi
    
    # Install Node.js dependencies
    if [[ -d "servers" ]] && [[ -f "servers/package.json" ]]; then
        log "Installing Node.js dependencies..."
        cd servers
        npm install
        npm run build-all 2>/dev/null || warn "Some builds may have failed"
        cd ..
    fi
    
    log "Setup complete! Please:"
    log "1. Edit .env with your credentials"
    log "2. Run: ./start-mcp.sh run"
}

# Start function
start_servers() {
    log "Starting MCP servers..."
    
    # Check credentials
    if ! node credential-manager.js validate; then
        error "Please configure credentials first: node credential-manager.js generate"
        exit 1
    fi
    
    # Determine config file
    local config_file
    if [[ "$1" == "docker" ]]; then
        config_file="platform-configs/docker/docker-compose.yml"
        if command -v docker-compose >/dev/null 2>&1; then
            log "Starting with Docker Compose..."
            docker-compose -f "$config_file" up -d
        else
            error "Docker Compose not found. Please install Docker and Docker Compose"
            exit 1
        fi
    else
        case "$PLATFORM" in
            "linux"|"wsl2")
                config_file="platform-configs/linux/mcp-hub-config-linux.json"
                ;;
            *)
                config_file="platform-configs/linux/mcp-hub-config-linux.json"
                ;;
        esac
        
        log "Using config: $config_file"
        log "MCP Hub will use configuration from: $config_file"
        log "Note: Start your MCP Hub client with this configuration file"
        log "Configuration file path: $(pwd)/$config_file"
    fi
}

# Stop function
stop_servers() {
    log "Stopping MCP servers..."
    
    if [[ -f "platform-configs/docker/docker-compose.yml" ]]; then
        if command -v docker-compose >/dev/null 2>&1; then
            docker-compose -f platform-configs/docker/docker-compose.yml down
        fi
    fi
    
    # Kill any running MCP processes
    pkill -f "mcp-server" || true
    pkill -f "mcp_server" || true
    
    log "All MCP servers stopped"
}

# Main script logic
case "${1:-}" in
    setup)
        check_requirements
        setup
        ;;
    run)
        check_requirements
        start_servers "${2:-native}"
        ;;
    docker)
        check_requirements
        start_servers "docker"
        ;;
    stop)
        stop_servers
        ;;
    status)
        node credential-manager.js status
        ;;
    *)
        echo "MCP Server Manager (Linux/macOS/WSL2)"
        echo "Usage: $0 {setup|run|docker|stop|status}"
        echo ""
        echo "Commands:"
        echo "  setup   - Initial setup of MCP environment"
        echo "  run     - Start MCP servers (native)"
        echo "  docker  - Start MCP servers using Docker"
        echo "  stop    - Stop all MCP servers"
        echo "  status  - Show current status"
        exit 1
        ;;
esac
