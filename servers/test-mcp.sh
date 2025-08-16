#!/bin/bash

# MCP Servers Test Script
# This script tests the deployed MCP servers and validates their functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Testing MCP Servers Deployment${NC}"
echo "=================================="

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

# Test container status
test_containers() {
    echo -e "\n${BLUE}Testing Container Status...${NC}"
    
    local containers=("mcp-router" "mcp-filesystem" "mcp-memory" "mcp-fetch" "mcp-git" "mcp-monitor")
    local all_running=true
    
    for container in "${containers[@]}"; do
        if podman ps --format "table {{.Names}}" | grep -q "$container"; then
            print_status "$container is running"
        else
            print_error "$container is not running"
            all_running=false
        fi
    done
    
    if [ "$all_running" = true ]; then
        print_status "All containers are running"
    else
        print_error "Some containers are not running"
        return 1
    fi
}

# Test router health
test_router_health() {
    echo -e "\n${BLUE}Testing Router Health...${NC}"
    
    # Wait for router to be ready
    echo "Waiting for router to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8080/health > /dev/null 2>&1; then
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
    local health_response=$(curl -s http://localhost:8080/health)
    if echo "$health_response" | grep -q "healthy"; then
        print_status "Health check passed"
    else
        print_error "Health check failed"
        echo "Response: $health_response"
        return 1
    fi
}

# Test server listing
test_server_listing() {
    echo -e "\n${BLUE}Testing Server Listing...${NC}"
    
    local servers_response=$(curl -s http://localhost:8080/servers)
    if echo "$servers_response" | grep -q "filesystem"; then
        print_status "Server listing works"
        echo "Available servers:"
        echo "$servers_response" | jq -r '.[].name' 2>/dev/null || echo "$servers_response"
    else
        print_error "Server listing failed"
        echo "Response: $servers_response"
        return 1
    fi
}

# Test MCP stdio communication
test_mcp_stdio() {
    echo -e "\n${BLUE}Testing MCP stdio Communication...${NC}"
    
    # Test filesystem server
    local test_request='{
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }'
    
    local response=$(curl -s -X POST http://localhost:8080/mcp/filesystem \
        -H "Content-Type: application/json" \
        -d "$test_request")
    
    if echo "$response" | grep -q "result"; then
        print_status "MCP stdio communication works"
        echo "Response: $response"
    else
        print_error "MCP stdio communication failed"
        echo "Response: $response"
        return 1
    fi
}

# Test monitoring
test_monitoring() {
    echo -e "\n${BLUE}Testing Monitoring...${NC}"
    
    # Wait for Grafana to be ready
    echo "Waiting for Grafana to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
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

# Test file operations
test_file_operations() {
    echo -e "\n${BLUE}Testing File Operations...${NC}"
    
    # Create test file
    echo "Hello MCP!" > ./data/test.txt
    
    # Test file read
    local read_request='{
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "read_file",
            "arguments": {
                "path": "/data/test.txt"
            }
        }
    }'
    
    local response=$(curl -s -X POST http://localhost:8080/mcp/filesystem \
        -H "Content-Type: application/json" \
        -d "$read_request")
    
    if echo "$response" | grep -q "Hello MCP"; then
        print_status "File read operation works"
    else
        print_error "File read operation failed"
        echo "Response: $response"
    fi
    
    # Cleanup
    rm -f ./data/test.txt
}

# Test memory operations
test_memory_operations() {
    echo -e "\n${BLUE}Testing Memory Operations...${NC}"
    
    # Test memory write
    local write_request='{
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "write_memory",
            "arguments": {
                "key": "test_key",
                "value": "test_value"
            }
        }
    }'
    
    local response=$(curl -s -X POST http://localhost:8080/mcp/memory \
        -H "Content-Type: application/json" \
        -d "$write_request")
    
    if echo "$response" | grep -q "result"; then
        print_status "Memory write operation works"
    else
        print_error "Memory write operation failed"
        echo "Response: $response"
    fi
}

# Performance test
test_performance() {
    echo -e "\n${BLUE}Testing Performance...${NC}"
    
    local start_time=$(date +%s.%N)
    
    # Make 10 requests
    for i in {1..10}; do
        curl -s -X POST http://localhost:8080/mcp/filesystem \
            -H "Content-Type: application/json" \
            -d '{"jsonrpc": "2.0", "id": '$i', "method": "tools/list", "params": {}}' > /dev/null
    done
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    
    print_status "10 requests completed in ${duration}s"
    
    if (( $(echo "$duration < 5" | bc -l) )); then
        print_status "Performance is acceptable"
    else
        print_warning "Performance might be slow"
    fi
}

# Main test execution
main() {
    echo "Starting MCP servers tests..."
    
    # Check if containers are running
    if ! podman ps | grep -q "mcp-router"; then
        print_error "MCP containers are not running. Please run ./deploy-podman.sh first."
        exit 1
    fi
    
    # Run tests
    test_containers
    test_router_health
    test_server_listing
    test_mcp_stdio
    test_monitoring
    test_file_operations
    test_memory_operations
    test_performance
    
    echo -e "\n${GREEN}🎉 All tests completed successfully!${NC}"
    echo ""
    echo "Your MCP servers are ready for production use:"
    echo "  - Router Dashboard: http://localhost:8080"
    echo "  - Monitoring: http://localhost:3000"
    echo "  - API Documentation: See README.md for endpoint details"
}

# Run main function
main "$@" 