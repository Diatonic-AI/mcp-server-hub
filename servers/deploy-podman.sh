#!/bin/bash

# MCP Servers Production Deployment Script for Podman Desktop
# This script deploys all MCP servers as production containers with stdio communication

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="mcp-servers"
NETWORK_NAME="mcp-network"
DATA_DIR="./data"
LOGS_DIR="./logs"
CONFIG_DIR="./config"

echo -e "${BLUE}🚀 MCP Servers Production Deployment for Podman Desktop${NC}"
echo "=================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if Podman is installed
check_podman() {
    if ! command -v podman &> /dev/null; then
        print_error "Podman is not installed. Please install Podman Desktop first."
        exit 1
    fi
    print_status "Podman is available"
}

# Create necessary directories
setup_directories() {
    mkdir -p $DATA_DIR
    mkdir -p $LOGS_DIR
    mkdir -p $CONFIG_DIR
    mkdir -p $DATA_DIR/memory
    mkdir -p $DATA_DIR/repos
    print_status "Created necessary directories"
}

# Create Podman network
setup_network() {
    if ! podman network exists $NETWORK_NAME; then
        podman network create $NETWORK_NAME
        print_status "Created Podman network: $NETWORK_NAME"
    else
        print_warning "Network $NETWORK_NAME already exists"
    fi
}

# Build TypeScript-based MCP servers
build_typescript_servers() {
    echo -e "\n${BLUE}Building TypeScript-based MCP servers...${NC}"
    
    local servers=("filesystem" "memory" "fetch" "everything" "sequentialthinking" "time")
    
    for server in "${servers[@]}"; do
        if [ -d "./servers/src/$server" ]; then
            echo "Building $server..."
            cd "./servers/src/$server"
            
            # Build the server
            podman build -t "mcp-$server:latest" .
            
            cd ../../..
            print_status "Built mcp-$server:latest"
        else
            print_warning "Server directory ./servers/src/$server not found"
        fi
    done
}

# Build Python-based MCP servers
build_python_servers() {
    echo -e "\n${BLUE}Building Python-based MCP servers...${NC}"
    
    local servers=("git")
    
    for server in "${servers[@]}"; do
        if [ -d "./servers/src/$server" ]; then
            echo "Building $server..."
            cd "./servers/src/$server"
            
            # Build the server
            podman build -t "mcp-$server:latest" .
            
            cd ../../..
            print_status "Built mcp-$server:latest"
        else
            print_warning "Server directory ./servers/src/$server not found"
        fi
    done
}

# Build MCP Router
build_router() {
    echo -e "\n${BLUE}Building MCP Router...${NC}"
    
    if [ -d "./router" ]; then
        cd "./router"
        
        # Install dependencies and build
        npm install
        npm run build
        
        # Build the container
        podman build -t "mcp-router:latest" .
        
        cd ..
        print_status "Built mcp-router:latest"
    else
        print_error "Router directory not found"
        exit 1
    fi
}

# Create Podman Compose file
create_podman_compose() {
    cat > podman-compose.yml << 'EOF'
version: '3.8'

services:
  # TypeScript-based MCP Servers
  mcp-filesystem:
    image: mcp-filesystem:latest
    container_name: mcp-filesystem
    volumes:
      - ./data:/data:ro
    environment:
      - NODE_ENV=production
    stdin_open: true
    tty: true
    restart: unless-stopped
    networks:
      - mcp-network

  mcp-memory:
    image: mcp-memory:latest
    container_name: mcp-memory
    volumes:
      - ./data/memory:/app/data
    environment:
      - NODE_ENV=production
    stdin_open: true
    tty: true
    restart: unless-stopped
    networks:
      - mcp-network

  mcp-fetch:
    image: mcp-fetch:latest
    container_name: mcp-fetch
    environment:
      - NODE_ENV=production
    stdin_open: true
    tty: true
    restart: unless-stopped
    networks:
      - mcp-network

  mcp-everything:
    image: mcp-everything:latest
    container_name: mcp-everything
    environment:
      - NODE_ENV=production
    stdin_open: true
    tty: true
    restart: unless-stopped
    networks:
      - mcp-network

  mcp-sequentialthinking:
    image: mcp-sequentialthinking:latest
    container_name: mcp-sequentialthinking
    environment:
      - NODE_ENV=production
    stdin_open: true
    tty: true
    restart: unless-stopped
    networks:
      - mcp-network

  mcp-time:
    image: mcp-time:latest
    container_name: mcp-time
    environment:
      - NODE_ENV=production
    stdin_open: true
    tty: true
    restart: unless-stopped
    networks:
      - mcp-network

  # Python-based MCP Servers
  mcp-git:
    image: mcp-git:latest
    container_name: mcp-git
    volumes:
      - ./data/repos:/repos:ro
    environment:
      - PYTHONPATH=/app
    stdin_open: true
    tty: true
    restart: unless-stopped
    networks:
      - mcp-network

  # MCP Router for centralized management
  mcp-router:
    image: mcp-router:latest
    container_name: mcp-router
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
      - MCP_SERVERS_CONFIG=/app/config/servers.json
    volumes:
      - ./router/config:/app/config
      - ./logs:/app/logs
    stdin_open: true
    tty: true
    restart: unless-stopped
    networks:
      - mcp-network

  # Monitoring
  mcp-monitor:
    image: grafana/grafana:latest
    container_name: mcp-monitor
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana
    restart: unless-stopped
    networks:
      - mcp-network

networks:
  mcp-network:
    external: true

volumes:
  grafana-storage:
EOF

    print_status "Created podman-compose.yml"
}

# Deploy all services
deploy_services() {
    echo -e "\n${BLUE}Deploying MCP services...${NC}"
    
    # Use podman-compose if available, otherwise use podman directly
    if command -v podman-compose &> /dev/null; then
        podman-compose up -d
        print_status "Deployed services using podman-compose"
    else
        print_warning "podman-compose not found, deploying manually"
        deploy_manual()
    fi
}

# Manual deployment using podman
deploy_manual() {
    # Start router first
    podman run -d \
        --name mcp-router \
        --network mcp-network \
        -p 8080:8080 \
        -v ./router/config:/app/config:ro \
        -v ./logs:/app/logs \
        -e NODE_ENV=production \
        mcp-router:latest

    # Start TypeScript servers
    local ts_servers=("filesystem" "memory" "fetch" "everything" "sequentialthinking" "time")
    for server in "${ts_servers[@]}"; do
        podman run -d \
            --name "mcp-$server" \
            --network mcp-network \
            -v "./data:/data:ro" \
            -e NODE_ENV=production \
            "mcp-$server:latest"
    done

    # Start Python servers
    podman run -d \
        --name mcp-git \
        --network mcp-network \
        -v "./data/repos:/repos:ro" \
        -e PYTHONPATH=/app \
        mcp-git:latest

    # Start monitoring
    podman run -d \
        --name mcp-monitor \
        --network mcp-network \
        -p 3000:3000 \
        -e GF_SECURITY_ADMIN_PASSWORD=admin \
        grafana/grafana:latest

    print_status "Deployed all services manually"
}

# Health check
health_check() {
    echo -e "\n${BLUE}Performing health checks...${NC}"
    
    # Check if containers are running
    local containers=("mcp-router" "mcp-filesystem" "mcp-memory" "mcp-fetch" "mcp-git" "mcp-monitor")
    
    for container in "${containers[@]}"; do
        if podman ps --format "table {{.Names}}" | grep -q "$container"; then
            print_status "$container is running"
        else
            print_error "$container is not running"
        fi
    done
    
    # Test router endpoint
    if curl -s http://localhost:8080/health > /dev/null; then
        print_status "Router health check passed"
    else
        print_error "Router health check failed"
    fi
}

# Show usage information
show_usage() {
    echo -e "\n${BLUE}Usage Information:${NC}"
    echo "=================="
    echo "Router Dashboard: http://localhost:8080"
    echo "Grafana Monitoring: http://localhost:3000 (admin/admin)"
    echo ""
    echo "Available endpoints:"
    echo "  GET  /health          - Health check"
    echo "  GET  /servers         - List all servers"
    echo "  POST /servers/{name}/start - Start a server"
    echo "  POST /servers/{name}/stop  - Stop a server"
    echo "  POST /mcp/{server}    - Forward MCP request"
    echo ""
    echo "To stop all services:"
    echo "  podman-compose down"
    echo ""
    echo "To view logs:"
    echo "  podman logs mcp-router"
    echo "  podman logs mcp-filesystem"
    echo "  podman logs mcp-memory"
}

# Main execution
main() {
    check_podman
    setup_directories
    setup_network
    build_typescript_servers
    build_python_servers
    build_router
    create_podman_compose
    deploy_services
    health_check
    show_usage
    
    echo -e "\n${GREEN}🎉 MCP Servers deployment completed successfully!${NC}"
    echo "You can now access the services at:"
    echo "  - Router: http://localhost:8080"
    echo "  - Monitoring: http://localhost:3000"
}

# Run main function
main "$@" 