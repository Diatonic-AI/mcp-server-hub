#!/bin/bash

# MCP Servers Production Deployment Script
# This script deploys MCP servers using individual container commands for production

set -e

echo "========================================"
echo "MCP Servers Production Deployment"
echo "========================================"

# Base directory
BASE_DIR="/home/daclab-work001/DEV/mcp/servers"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check prerequisites
check_prerequisites() {
    echo -e "\n${BLUE}Checking prerequisites...${NC}"
    
    # Check if production drive is mounted
    if [ ! -d "$PROD_ROOT" ]; then
        print_error "Production drive not mounted at $PROD_ROOT"
        exit 1
    fi
    print_status "Production drive accessible"
    
    # Check available space
    local available_space=$(df "$PROD_ROOT" | awk 'NR==2 {print $4}')
    local available_gb=$((available_space / 1024 / 1024))
    if [ $available_gb -lt 10 ]; then
        print_error "Insufficient space on production drive (${available_gb}GB available, need at least 10GB)"
        exit 1
    fi
    print_status "Sufficient space available (${available_gb}GB)"
    
    # Check Podman
    if ! command -v podman &> /dev/null; then
        print_error "Podman is not installed"
        exit 1
    fi
    print_status "Podman is available"
    
    # Check Node.js (for router build)
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed (required for router build)"
        exit 1
    fi
    print_status "Node.js is available"
}

# Setup production directory structure
setup_production_dirs() {
    echo -e "\n${BLUE}Setting up production directory structure...${NC}"
    
    # Create main directories
    mkdir -p "$PROD_ROOT"/{logs,volumes,data,repos,config,images}
    mkdir -p "$PROD_ROOT"/data/{memory,repos}
    mkdir -p "$PROD_ROOT"/volumes/{grafana,elasticsearch}
    mkdir -p "$PROD_ROOT"/config/{grafana,router}
    mkdir -p "$PROD_ROOT"/logs/{router,resource-manager,containers}
    
    # Set proper permissions
    chmod 755 "$PROD_ROOT"
    chmod 755 "$PROD_ROOT"/*
    
    print_status "Production directory structure created"
}

# Create production network
setup_network() {
    echo -e "\n${BLUE}Setting up production network...${NC}"
    
    if ! podman network exists "$NETWORK_NAME"; then
        podman network create "$NETWORK_NAME"
        print_status "Created production network: $NETWORK_NAME"
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

# Build Router and Resource Manager
build_management_components() {
    echo -e "\n${BLUE}Building management components...${NC}"
    
    # Build Router
    if [ -d "./router" ]; then
        cd "./router"
        npm install
        npm run build
        podman build -t "mcp-router:latest" .
        cd ..
        print_status "Built mcp-router:latest"
    else
        print_error "Router directory not found"
        exit 1
    fi
    
    # Build Resource Manager
    if [ -d "./resource-manager" ]; then
        cd "./resource-manager"
        podman build -t "mcp-resource-manager:latest" .
        cd ..
        print_status "Built mcp-resource-manager:latest"
    else
        print_error "Resource manager directory not found"
        exit 1
    fi
}

# Copy configuration files
setup_configurations() {
    echo -e "\n${BLUE}Setting up configurations...${NC}"
    
    # Copy router configuration
    cp ./router/config/servers.json "$PROD_ROOT/config/router/"
    
    # Create Grafana configuration
    mkdir -p "$PROD_ROOT/config/grafana/provisioning"
    cat > "$PROD_ROOT/config/grafana/provisioning/datasources.yml" << 'EOF'
apiVersion: 1

datasources:
  - name: MCP Metrics
    type: prometheus
    access: proxy
    url: http://localhost:9090
    isDefault: true
EOF

    cat > "$PROD_ROOT/config/grafana/provisioning/dashboards.yml" << 'EOF'
apiVersion: 1

providers:
  - name: 'MCP Dashboards'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF

    print_status "Configurations copied to production"
}

# Deploy always-running services
deploy_core_services() {
    echo -e "\n${BLUE}Deploying core services (always running)...${NC}"
    
    # Start Router
    podman run -d \
        --name mcp-router-prod \
        --network "$NETWORK_NAME" \
        -p "$ROUTER_PORT:$ROUTER_PORT" \
        -v "$PROD_ROOT/config/router:/app/config:ro" \
        -v "$PROD_ROOT/logs/router:/app/logs" \
        -e NODE_ENV=production \
        -e MCP_SERVERS_CONFIG=/app/config/servers.json \
        -e AUTO_SHUTDOWN_TIMEOUT="$AUTO_SHUTDOWN_TIMEOUT" \
        -e HEALTH_CHECK_INTERVAL="$HEALTH_CHECK_INTERVAL" \
        mcp-router:latest
    
    print_status "Router started"
    
    # Start Monitor
    podman run -d \
        --name mcp-monitor-prod \
        --network "$NETWORK_NAME" \
        -p "$MONITOR_PORT:$MONITOR_PORT" \
        -v "$PROD_ROOT/volumes/grafana:/var/lib/grafana" \
        -v "$PROD_ROOT/config/grafana/provisioning:/etc/grafana/provisioning:ro" \
        -e GF_SECURITY_ADMIN_PASSWORD=admin \
        -e GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource \
        grafana/grafana:latest
    
    print_status "Monitor started"
    
    # Start Resource Manager
    podman run -d \
        --name mcp-resource-manager-prod \
        --network "$NETWORK_NAME" \
        -v /var/run/podman/podman.sock:/var/run/podman/podman.sock \
        -v "$PROD_ROOT/logs/resource-manager:/app/logs" \
        -e PROD_ROOT="$PROD_ROOT" \
        -e AUTO_SHUTDOWN_TIMEOUT="$AUTO_SHUTDOWN_TIMEOUT" \
        -e HEALTH_CHECK_INTERVAL="$HEALTH_CHECK_INTERVAL" \
        mcp-resource-manager:latest
    
    print_status "Resource Manager started"
}

# Create on-demand containers (not started)
create_ondemand_containers() {
    echo -e "\n${BLUE}Creating on-demand containers...${NC}"
    
    # TypeScript servers
    local ts_servers=("filesystem" "memory" "fetch" "everything" "sequentialthinking" "time")
    for server in "${ts_servers[@]}"; do
        podman create \
            --name "mcp-$server-prod" \
            --network "$NETWORK_NAME" \
            -v "$PROD_ROOT/data:/data:ro" \
            -e NODE_ENV=production \
            -e STDIO_ENABLED=true \
            "mcp-$server:latest"
        
        print_status "Created mcp-$server-prod (on-demand)"
    done
    
    # Python servers
    podman create \
        --name mcp-git-prod \
        --network "$NETWORK_NAME" \
        -v "$PROD_ROOT/repos:/repos:ro" \
        -e PYTHONPATH=/app \
        -e STDIO_ENABLED=true \
        mcp-git:latest
    
    print_status "Created mcp-git-prod (on-demand)"
}

# Wait for services to be ready
wait_for_services() {
    echo -e "\n${BLUE}Waiting for services to be ready...${NC}"
    
    # Wait for router
    echo "Waiting for router..."
    for i in {1..60}; do
        if curl -s "http://localhost:$ROUTER_PORT/health" > /dev/null 2>&1; then
            print_status "Router is ready"
            break
        fi
        if [ $i -eq 60 ]; then
            print_error "Router failed to start"
            exit 1
        fi
        sleep 1
    done
    
    # Wait for monitor
    echo "Waiting for monitor..."
    for i in {1..60}; do
        if curl -s "http://localhost:$MONITOR_PORT" > /dev/null 2>&1; then
            print_status "Monitor is ready"
            break
        fi
        if [ $i -eq 60 ]; then
            print_warning "Monitor failed to start"
        fi
        sleep 1
    done
}

# Health check
health_check() {
    echo -e "\n${BLUE}Performing health checks...${NC}"
    
    # Check core services
    local core_services=("mcp-router-prod" "mcp-monitor-prod" "mcp-resource-manager-prod")
    local all_healthy=true
    
    for service in "${core_services[@]}"; do
        if podman ps --format "table {{.Names}}" | grep -q "$service"; then
            print_status "$service is running"
        else
            print_error "$service is not running"
            all_healthy=false
        fi
    done
    
    # Test router endpoint
    if curl -s "http://localhost:$ROUTER_PORT/health" | grep -q "healthy"; then
        print_status "Router health check passed"
    else
        print_error "Router health check failed"
        all_healthy=false
    fi
    
    if [ "$all_healthy" = true ]; then
        print_status "All core services are healthy"
    else
        print_error "Some services are not healthy"
        return 1
    fi
}

# Show usage information
show_usage() {
    echo -e "\n${BLUE}Production MCP System Usage:${NC}"
    echo "================================"
    echo "Router Dashboard: http://localhost:$ROUTER_PORT"
    echo "Monitoring: http://localhost:$MONITOR_PORT (admin/admin)"
    echo ""
    echo "On-Demand Server Management:"
    echo "  Start server: curl -X POST http://localhost:$ROUTER_PORT/servers/{name}/start"
    echo "  Stop server:  curl -X POST http://localhost:$ROUTER_PORT/servers/{name}/stop"
    echo ""
    echo "Resource Management:"
    echo "  - Servers start automatically when requested"
    echo "  - Servers stop after ${AUTO_SHUTDOWN_TIMEOUT}s of inactivity"
    echo "  - Resource usage is monitored and optimized"
    echo ""
    echo "Logs: $PROD_ROOT/logs/"
    echo "Data: $PROD_ROOT/data/"
    echo "Config: $PROD_ROOT/config/"
}

# Main execution
main() {
    check_prerequisites
    setup_production_dirs
    setup_network
    build_typescript_servers
    build_python_servers
    build_management_components
    setup_configurations
    deploy_core_services
    create_ondemand_containers
    wait_for_services
    health_check
    show_usage
    
    echo -e "\n${GREEN}🎉 Production MCP System deployment completed successfully!${NC}"
    echo ""
    echo "System is now running with:"
    echo "  - On-demand resource management"
    echo "  - Production drive storage"
    echo "  - Stdio communication for all servers"
    echo "  - Automatic shutdown for inactive servers"
}

# Run main function
main "$@" 