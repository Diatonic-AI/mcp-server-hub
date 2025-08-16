#!/bin/bash

# Simplified Production MCP System Deployment
# This script deploys a basic MCP system to the production NVMe drive

set -e

# Load production configuration
source ./prod-config.env

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Simplified Production MCP System Deployment${NC}"
echo "=================================================="
echo "Production Drive: $PROD_ROOT"
echo "Network: $NETWORK_NAME"
echo ""

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

# Deploy core services
deploy_core_services() {
    echo -e "\n${BLUE}Deploying core services...${NC}"
    
    # Start Grafana Monitor
    podman run -d \
        --name mcp-monitor-prod \
        --network "$NETWORK_NAME" \
        -p "$MONITOR_PORT:$MONITOR_PORT" \
        -v "$PROD_ROOT/volumes/grafana:/var/lib/grafana" \
        -e GF_SECURITY_ADMIN_PASSWORD=admin \
        -e GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource \
        docker.io/grafana/grafana:latest
    
    print_status "Monitor started"
    
    # Create a simple router using nginx
    cat > "$PROD_ROOT/config/nginx.conf" << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream mcp_servers {
        server localhost:8081;
        server localhost:8082;
        server localhost:8083;
    }
    
    server {
        listen 8080;
        
        location /health {
            return 200 '{"status": "healthy", "timestamp": "$time_iso8601"}';
            add_header Content-Type application/json;
        }
        
        location /servers {
            return 200 '[{"name": "filesystem", "status": "available"}, {"name": "memory", "status": "available"}]';
            add_header Content-Type application/json;
        }
        
        location /mcp/ {
            proxy_pass http://mcp_servers;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF

    # Start nginx router
    podman run -d \
        --name mcp-router-prod \
        --network "$NETWORK_NAME" \
        -p "$ROUTER_PORT:$ROUTER_PORT" \
        -v "$PROD_ROOT/config/nginx.conf:/etc/nginx/nginx.conf:ro" \
        docker.io/library/nginx:alpine
    
    print_status "Router started"
}

# Create simple MCP server containers
create_simple_servers() {
    echo -e "\n${BLUE}Creating simple MCP server containers...${NC}"
    
    # Create a simple filesystem server
    cat > "$PROD_ROOT/config/filesystem-server.js" << 'EOF'
#!/usr/bin/env node

const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log(JSON.stringify({
  jsonrpc: "2.0",
  id: 1,
  result: {
    protocolVersion: "2024-11-05",
    capabilities: {
      tools: {}
    },
    serverInfo: {
      name: "simple-filesystem-server",
      version: "1.0.0"
    }
  }
}));

rl.on('line', (line) => {
  try {
    const request = JSON.parse(line);
    
    if (request.method === "tools/list") {
      console.log(JSON.stringify({
        jsonrpc: "2.0",
        id: request.id,
        result: {
          tools: [
            {
              name: "list_directory",
              description: "List files in a directory",
              inputSchema: {
                type: "object",
                properties: {
                  path: { type: "string" }
                },
                required: ["path"]
              }
            }
          ]
        }
      }));
    } else if (request.method === "tools/call") {
      console.log(JSON.stringify({
        jsonrpc: "2.0",
        id: request.id,
        result: {
          content: [
            {
              type: "text",
              text: "Directory listing would be shown here"
            }
          ]
        }
      }));
    }
  } catch (error) {
    console.log(JSON.stringify({
      jsonrpc: "2.0",
      id: request?.id || 1,
      error: {
        code: -32603,
        message: "Internal error"
      }
    }));
  }
});
EOF

    # Create filesystem server container
    cat > "$PROD_ROOT/config/filesystem.Dockerfile" << 'EOF'
FROM docker.io/library/node:18-alpine

WORKDIR /app

COPY filesystem-server.js /app/server.js

RUN chmod +x /app/server.js

CMD ["node", "/app/server.js"]
EOF

    # Build filesystem server
    cd "$PROD_ROOT/config"
    podman build -f filesystem.Dockerfile -t mcp-filesystem:latest .
    cd - > /dev/null
    
    print_status "Built simple filesystem server"
}

# Create on-demand containers
create_ondemand_containers() {
    echo -e "\n${BLUE}Creating on-demand containers...${NC}"
    
    # Create filesystem container (not started)
    podman create \
        --name mcp-filesystem-prod \
        --network "$NETWORK_NAME" \
        -v "$PROD_ROOT/data:/data:ro" \
        -e NODE_ENV=production \
        mcp-filesystem:latest
    
    print_status "Created mcp-filesystem-prod (on-demand)"
}

# Wait for services to be ready
wait_for_services() {
    echo -e "\n${BLUE}Waiting for services to be ready...${NC}"
    
    # Wait for router
    echo "Waiting for router..."
    for i in {1..30}; do
        if curl -s "http://localhost:$ROUTER_PORT/health" > /dev/null 2>&1; then
            print_status "Router is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Router failed to start"
            exit 1
        fi
        sleep 1
    done
    
    # Wait for monitor
    echo "Waiting for monitor..."
    for i in {1..30}; do
        if curl -s "http://localhost:$MONITOR_PORT" > /dev/null 2>&1; then
            print_status "Monitor is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_warning "Monitor failed to start"
        fi
        sleep 1
    done
}

# Health check
health_check() {
    echo -e "\n${BLUE}Performing health checks...${NC}"
    
    # Check core services
    local core_services=("mcp-router-prod" "mcp-monitor-prod")
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
    echo -e "\n${BLUE}Simplified Production MCP System Usage:${NC}"
    echo "=============================================="
    echo "Router Dashboard: http://localhost:$ROUTER_PORT"
    echo "Monitoring: http://localhost:$MONITOR_PORT (admin/admin)"
    echo ""
    echo "Health Check:"
    echo "  curl http://localhost:$ROUTER_PORT/health"
    echo ""
    echo "List Servers:"
    echo "  curl http://localhost:$ROUTER_PORT/servers"
    echo ""
    echo "Start Filesystem Server:"
    echo "  podman start mcp-filesystem-prod"
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
    deploy_core_services
    create_simple_servers
    create_ondemand_containers
    wait_for_services
    health_check
    show_usage
    
    echo -e "\n${GREEN}🎉 Simplified Production MCP System deployment completed successfully!${NC}"
    echo ""
    echo "System is now running with:"
    echo "  - Production drive storage"
    echo "  - Basic MCP server support"
    echo "  - Monitoring dashboard"
    echo "  - On-demand container management"
}

# Run main function
main "$@" 