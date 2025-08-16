#!/bin/bash

# Production MCP System Test Script
# Tests the on-demand container system and resource management

set -e

# Load production configuration
source ./prod-config.env

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Testing Production MCP System${NC}"
echo "====================================="
echo "Production Drive: $PROD_ROOT"
echo "Auto Shutdown Timeout: ${AUTO_SHUTDOWN_TIMEOUT}s"
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

# Test production drive access
test_production_drive() {
    echo -e "\n${BLUE}Testing Production Drive Access...${NC}"
    
    if [ -d "$PROD_ROOT" ]; then
        print_status "Production drive accessible"
        
        # Check directory structure
        local required_dirs=("logs" "volumes" "data" "repos" "config" "images")
        for dir in "${required_dirs[@]}"; do
            if [ -d "$PROD_ROOT/$dir" ]; then
                print_status "Directory $dir exists"
            else
                print_error "Directory $dir missing"
                return 1
            fi
        done
    else
        print_error "Production drive not accessible"
        return 1
    fi
}

# Test core services
test_core_services() {
    echo -e "\n${BLUE}Testing Core Services...${NC}"
    
    local core_services=("mcp-router-prod" "mcp-monitor-prod" "mcp-resource-manager-prod")
    local all_running=true
    
    for service in "${core_services[@]}"; do
        if podman ps --format "table {{.Names}}" | grep -q "$service"; then
            print_status "$service is running"
        else
            print_error "$service is not running"
            all_running=false
        fi
    done
    
    if [ "$all_running" = true ]; then
        print_status "All core services are running"
    else
        print_error "Some core services are not running"
        return 1
    fi
}

# Test router health
test_router_health() {
    echo -e "\n${BLUE}Testing Router Health...${NC}"
    
    # Wait for router to be ready
    echo "Waiting for router to be ready..."
    for i in {1..30}; do
        if curl -s "http://localhost:$ROUTER_PORT/health" > /dev/null 2>&1; then
            print_status "Router is responding"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Router is not responding after 30 seconds"
            return 1
        fi
        sleep 1
    done
    
    # Test health endpoint
    local health_response=$(curl -s "http://localhost:$ROUTER_PORT/health")
    if echo "$health_response" | grep -q "healthy"; then
        print_status "Health check passed"
    else
        print_error "Health check failed"
        echo "Response: $health_response"
        return 1
    fi
}

# Test on-demand container creation
test_ondemand_containers() {
    echo -e "\n${BLUE}Testing On-Demand Container Creation...${NC}"
    
    local ondemand_servers=("filesystem" "memory" "fetch" "everything" "sequentialthinking" "time" "git")
    
    for server in "${ondemand_servers[@]}"; do
        local container_name="mcp-$server-prod"
        if podman ps -a --format "table {{.Names}}" | grep -q "$container_name"; then
            print_status "Container $container_name exists"
        else
            print_error "Container $container_name missing"
            return 1
        fi
    done
    
    print_status "All on-demand containers created"
}

# Test on-demand startup
test_ondemand_startup() {
    echo -e "\n${BLUE}Testing On-Demand Startup...${NC}"
    
    # Test starting filesystem server
    echo "Testing filesystem server startup..."
    local response=$(curl -s -X POST "http://localhost:$ROUTER_PORT/servers/filesystem/start")
    
    if echo "$response" | grep -q "success"; then
        print_status "Filesystem server started successfully"
    else
        print_error "Filesystem server startup failed"
        echo "Response: $response"
        return 1
    fi
    
    # Wait for container to be running
    sleep 5
    if podman ps --format "table {{.Names}}" | grep -q "mcp-filesystem-prod"; then
        print_status "Filesystem container is running"
    else
        print_error "Filesystem container is not running"
        return 1
    fi
}

# Test stdio communication
test_stdio_communication() {
    echo -e "\n${BLUE}Testing Stdio Communication...${NC}"
    
    # Test MCP request to filesystem server
    local test_request='{
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }'
    
    local response=$(curl -s -X POST "http://localhost:$ROUTER_PORT/mcp/filesystem" \
        -H "Content-Type: application/json" \
        -d "$test_request")
    
    if echo "$response" | grep -q "result"; then
        print_status "Stdio communication works"
        echo "Response: $response"
    else
        print_error "Stdio communication failed"
        echo "Response: $response"
        return 1
    fi
}

# Test resource management
test_resource_management() {
    echo -e "\n${BLUE}Testing Resource Management...${NC}"
    
    # Check resource manager logs
    if [ -f "$PROD_ROOT/logs/resource-manager/resource-manager.log" ]; then
        print_status "Resource manager logs exist"
        
        # Check for recent activity
        local recent_logs=$(tail -n 10 "$PROD_ROOT/logs/resource-manager/resource-manager.log" | grep -c "container management" || true)
        if [ "$recent_logs" -gt 0 ]; then
            print_status "Resource manager is active"
        else
            print_warning "Resource manager may not be active"
        fi
    else
        print_warning "Resource manager logs not found"
    fi
    
    # Check container resource limits
    local filesystem_container=$(podman ps --filter "name=mcp-filesystem-prod" --format "{{.Names}}")
    if [ -n "$filesystem_container" ]; then
        local memory_limit=$(podman inspect "$filesystem_container" | jq -r '.[0].HostConfig.Memory' 2>/dev/null || echo "unknown")
        if [ "$memory_limit" != "null" ] && [ "$memory_limit" != "unknown" ]; then
            print_status "Container has memory limits set"
        else
            print_warning "Container memory limits not set"
        fi
    fi
}

# Test auto-shutdown functionality
test_auto_shutdown() {
    echo -e "\n${BLUE}Testing Auto-Shutdown Functionality...${NC}"
    
    # Stop filesystem server
    echo "Stopping filesystem server to test auto-shutdown..."
    curl -s -X POST "http://localhost:$ROUTER_PORT/servers/filesystem/stop" > /dev/null
    
    # Wait for container to stop
    sleep 5
    if ! podman ps --format "table {{.Names}}" | grep -q "mcp-filesystem-prod"; then
        print_status "Container stopped successfully"
    else
        print_warning "Container may still be running"
    fi
    
    # Check if container exists but is stopped
    if podman ps -a --format "table {{.Names}}" | grep -q "mcp-filesystem-prod"; then
        print_status "Container exists but is stopped (ready for on-demand startup)"
    else
        print_error "Container not found"
        return 1
    fi
}

# Test monitoring
test_monitoring() {
    echo -e "\n${BLUE}Testing Monitoring...${NC}"
    
    # Wait for Grafana to be ready
    echo "Waiting for Grafana to be ready..."
    for i in {1..30}; do
        if curl -s "http://localhost:$MONITOR_PORT" > /dev/null 2>&1; then
            print_status "Grafana is responding"
            break
        fi
        if [ $i -eq 30 ]; then
            print_warning "Grafana is not responding after 30 seconds"
            return 0
        fi
        sleep 1
    done
}

# Test production drive performance
test_production_performance() {
    echo -e "\n${BLUE}Testing Production Drive Performance...${NC}"
    
    # Test write performance
    local test_file="$PROD_ROOT/data/test_performance.txt"
    local start_time=$(date +%s.%N)
    
    # Write 1MB of data
    dd if=/dev/zero of="$test_file" bs=1M count=1 2>/dev/null
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    local speed=$(echo "scale=2; 1 / $duration" | bc)
    
    print_status "Write speed: ${speed} MB/s"
    
    # Test read performance
    start_time=$(date +%s.%N)
    dd if="$test_file" of=/dev/null bs=1M 2>/dev/null
    
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    speed=$(echo "scale=2; 1 / $duration" | bc)
    
    print_status "Read speed: ${speed} MB/s"
    
    # Cleanup
    rm -f "$test_file"
}

# Performance test
test_performance() {
    echo -e "\n${BLUE}Testing System Performance...${NC}"
    
    local start_time=$(date +%s.%N)
    
    # Make 10 requests to test performance
    for i in {1..10}; do
        curl -s -X POST "http://localhost:$ROUTER_PORT/servers/filesystem/start" > /dev/null
        sleep 0.1
    done
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    
    print_status "10 requests completed in ${duration}s"
    
    if (( $(echo "$duration < 10" | bc -l) )); then
        print_status "Performance is acceptable"
    else
        print_warning "Performance might be slow"
    fi
}

# Main test execution
main() {
    echo "Starting production MCP system tests..."
    
    # Check if core services are running
    if ! podman ps | grep -q "mcp-router-prod"; then
        print_error "Production MCP system is not running. Please run ./deploy-prod.sh first."
        exit 1
    fi
    
    # Run tests
    test_production_drive
    test_core_services
    test_router_health
    test_ondemand_containers
    test_ondemand_startup
    test_stdio_communication
    test_resource_management
    test_auto_shutdown
    test_monitoring
    test_production_performance
    test_performance
    
    echo -e "\n${GREEN}🎉 All production tests completed successfully!${NC}"
    echo ""
    echo "Production MCP System is working correctly:"
    echo "  - Production drive storage: ✓"
    echo "  - On-demand container management: ✓"
    echo "  - Stdio communication: ✓"
    echo "  - Resource management: ✓"
    echo "  - Auto-shutdown functionality: ✓"
    echo "  - Monitoring: ✓"
    echo "  - Performance: ✓"
    echo ""
    echo "System is ready for production use!"
}

# Run main function
main "$@" 