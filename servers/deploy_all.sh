#!/bin/bash

set -e

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

echo "========================================"
echo "MCP Servers Full Deployment"
echo "========================================"

# Purge all Podman containers, images, and volumes
echo -e "\n${BLUE}Purging all existing containers, images, and volumes...${NC}"
echo "Stopping and removing all containers..."
podman stop --all 2>/dev/null || echo "No containers to stop."
podman rm --all -f 2>/dev/null || echo "No containers to remove."

echo "Removing all images..."
podman rmi --all -f 2>/dev/null || echo "No images to remove."

echo "Cleaning up volumes..."
podman volume prune -f || echo "No volumes to prune."

echo "Cleaning up networks..."
podman network prune -f || echo "No networks to prune."

print_status "System purged successfully"

# Build all MCP server images
echo -e "\n${BLUE}Building MCP server images...${NC}"

# Build TypeScript-based servers from servers/src
TS_SERVERS=("filesystem" "memory" "fetch" "everything" "sequentialthinking" "time")
for server in "${TS_SERVERS[@]}"; do
    if [ -d "./servers/src/$server" ]; then
        echo "Building $server..."
        cd "./servers/src/$server"
        podman build -t "mcp-$server:latest" .
        cd ../../..
        print_status "Built mcp-$server:latest"
    else
        print_warning "Server directory ./servers/src/$server not found"
    fi
done

# Build Python-based servers
PY_SERVERS=("git")
for server in "${PY_SERVERS[@]}"; do
    if [ -d "./servers/src/$server" ]; then
        echo "Building $server..."
        cd "./servers/src/$server"
        podman build -t "mcp-$server:latest" .
        cd ../../..
        print_status "Built mcp-$server:latest"
    else
        print_warning "Server directory ./servers/src/$server not found"
    fi
done

# Build Router
if [ -d "./router" ]; then
    echo "Building router..."
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
    echo "Building resource-manager..."
    cd "./resource-manager"
    podman build -t "mcp-resource-manager:latest" .
    cd ..
    print_status "Built mcp-resource-manager:latest"
else
    print_error "Resource manager directory not found"
    exit 1
fi

# Create production directories
echo -e "\n${BLUE}Setting up production directories...${NC}"
PROD_ROOT="/tmp/mcp-prod"
mkdir -p "$PROD_ROOT"/{logs,volumes,data,repos,config}
mkdir -p "$PROD_ROOT"/data/{memory,repos}
mkdir -p "$PROD_ROOT"/volumes/{grafana}
mkdir -p "$PROD_ROOT"/config/{grafana,router}
mkdir -p "$PROD_ROOT"/logs/{router,resource-manager,containers}
print_status "Production directories created"

# Create production network
echo -e "\n${BLUE}Setting up production network...${NC}"
NETWORK_NAME="mcp-network"
if ! podman network exists "$NETWORK_NAME" 2>/dev/null; then
    podman network create "$NETWORK_NAME"
    print_status "Created production network: $NETWORK_NAME"
else
    print_warning "Network $NETWORK_NAME already exists"
fi

# Deploy all containers
echo -e "\n${BLUE}Deploying containers...${NC}"

# Start Router (port 8080)
podman run -d \
    --name mcp-router-prod \
    --network "$NETWORK_NAME" \
    -p 8080:8080 \
    -v "$PROD_ROOT/logs/router:/app/logs" \
    -e NODE_ENV=production \
    mcp-router:latest
print_status "Router deployed on port 8080"

# Start Grafana Monitor (port 3001)
podman run -d \
    --name mcp-monitor-prod \
    --network "$NETWORK_NAME" \
    -p 3001:3000 \
    -v "$PROD_ROOT/volumes/grafana:/var/lib/grafana" \
    -e GF_SECURITY_ADMIN_PASSWORD=admin \
    grafana/grafana:latest
print_status "Monitor deployed on port 3001"

# Start Resource Manager
podman run -d \
    --name mcp-resource-manager-prod \
    --network "$NETWORK_NAME" \
    -v "$PROD_ROOT/logs/resource-manager:/app/logs" \
    mcp-resource-manager:latest
print_status "Resource Manager deployed"

# Start MCP Server containers
# Filesystem Server
podman run -d \
    --name mcp-filesystem-prod \
    --network "$NETWORK_NAME" \
    -v "$PROD_ROOT/data:/data" \
    -e NODE_ENV=production \
    mcp-filesystem:latest
print_status "Filesystem server deployed"

# Memory Server
podman run -d \
    --name mcp-memory-prod \
    --network "$NETWORK_NAME" \
    -v "$PROD_ROOT/data/memory:/data" \
    -e NODE_ENV=production \
    mcp-memory:latest
print_status "Memory server deployed"

# Fetch Server
podman run -d \
    --name mcp-fetch-prod \
    --network "$NETWORK_NAME" \
    -e NODE_ENV=production \
    mcp-fetch:latest
print_status "Fetch server deployed"

# Time Server with timezone
podman run -d \
    --name mcp-time-prod \
    --network "$NETWORK_NAME" \
    -e LOCAL_TIMEZONE=America/Chicago \
    -e NODE_ENV=production \
    mcp-time:latest
print_status "Time server deployed"

# Git Server
podman run -d \
    --name mcp-git-prod \
    --network "$NETWORK_NAME" \
    -v "$PROD_ROOT/repos:/repos" \
    -e PYTHONPATH=/app \
    mcp-git:latest
print_status "Git server deployed"

# Everything Server
podman run -d \
    --name mcp-everything-prod \
    --network "$NETWORK_NAME" \
    -e NODE_ENV=production \
    mcp-everything:latest
print_status "Everything server deployed"

# Sequential Thinking Server
podman run -d \
    --name mcp-sequentialthinking-prod \
    --network "$NETWORK_NAME" \
    -e NODE_ENV=production \
    mcp-sequentialthinking:latest
print_status "Sequential thinking server deployed"

# Wait for services to be ready
echo -e "\n${BLUE}Waiting for services to be ready...${NC}"
sleep 10

# Health check
echo -e "\n${BLUE}Performing health checks...${NC}"

# Check all containers are running
containers=("mcp-router-prod" "mcp-monitor-prod" "mcp-resource-manager-prod" "mcp-filesystem-prod" "mcp-memory-prod" "mcp-fetch-prod" "mcp-time-prod" "mcp-git-prod" "mcp-everything-prod" "mcp-sequentialthinking-prod")
all_healthy=true

for container in "${containers[@]}"; do
    if podman ps --format "table {{.Names}}" | grep -q "$container"; then
        print_status "$container is running"
    else
        print_error "$container is not running"
        all_healthy=false
    fi
done

if [ "$all_healthy" = true ]; then
    print_status "All services are healthy"
else
    print_error "Some services are not healthy"
fi

# Show access information
echo -e "\n${BLUE}Deployment Complete!${NC}"
echo "============================="
echo "Router Dashboard: http://localhost:8080"
echo "Monitoring: http://localhost:3001 (admin/admin)"
echo ""
echo "Running containers:"
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "Logs directory: $PROD_ROOT/logs/"
echo "Data directory: $PROD_ROOT/data/"

print_status "Full MCP deployment completed successfully!"

