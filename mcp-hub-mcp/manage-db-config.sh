#!/bin/bash

# =============================================================================
# MCP Database Configuration Manager
# =============================================================================
# This script helps manage database configurations for the MCP Hub

CREDENTIALS_DIR="/home/daclab-work001/DEV/mcp/.credentials"
HUB_DIR="/home/daclab-work001/DEV/mcp/mcp-hub-mcp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}=== MCP Database Configuration Manager ===${NC}"
    echo
}

show_usage() {
    echo "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "  list-databases    Show all configured databases"
    echo "  test-connection   Test database connections"
    echo "  show-env         Show environment variables"
    echo "  create-test      Create test database entries"
    echo "  backup-config    Backup current configuration"
    echo "  restore-config   Restore configuration from backup"
    echo "  help             Show this help message"
    echo
}

list_databases() {
    echo -e "${GREEN}📊 Configured Production Databases:${NC}"
    echo
    
    echo -e "${YELLOW}PostgreSQL Databases (Port 5433):${NC}"
    echo "  • livesmartgrowth_prod (existing LSG data)"
    echo "  • mcp_hub_prod (MCP Hub configuration)"
    echo "  • analytics_prod (analytics data)"
    echo "  • mcp_data_prod (general MCP data)"
    echo "  • jsonrpc_logs_prod (JSON-RPC logs)"
    echo
    
    echo -e "${YELLOW}MySQL Databases (Port 3306):${NC}"
    echo "  • web_applications_prod (web app data)"
    echo "  • ecommerce_prod (e-commerce)"
    echo "  • cms_prod (content management)"
    echo
    
    echo -e "${YELLOW}MongoDB Databases (Port 27017):${NC}"
    echo "  • documents_prod (document storage)"
    echo "  • sessions_prod (user sessions)"
    echo "  • logs_prod (application logs)"
    echo "  • api_data_prod (API data)"
    echo
    
    echo -e "${YELLOW}Redis Databases (Port 6379):${NC}"
    echo "  • DB 0: cache_prod (general caching)"
    echo "  • DB 1: sessions_prod (session storage)"
    echo "  • DB 2: ratelimit_prod (rate limiting)"
    echo "  • DB 3: queue_prod (queue management)"
    echo
    
    echo -e "${YELLOW}SQLite Databases:${NC}"
    echo "  • development.db (development data)"
    echo "  • testing.db (test data)"
    echo "  • backup_metadata.db (backup metadata)"
    echo "  • application_logs.db (application logs)"
    echo
}

test_connection() {
    echo -e "${GREEN}🔍 Testing Database Connections...${NC}"
    echo
    
    # Source environment variables
    if [ -f "$CREDENTIALS_DIR/.env.databases" ]; then
        source "$CREDENTIALS_DIR/.env.databases" 2>/dev/null
    fi
    
    # Test SQLite (simple file check)
    echo -e "${YELLOW}Testing SQLite...${NC}"
    if [ -d "/srv/databases/prod/sqlite" ]; then
        echo -e "✅ SQLite directory exists"
        # Test if we can create a test file
        if touch "/srv/databases/prod/sqlite/test.tmp" 2>/dev/null; then
            echo -e "✅ SQLite directory is writable"
            rm -f "/srv/databases/prod/sqlite/test.tmp"
        else
            echo -e "❌ SQLite directory is not writable"
        fi
    else
        echo -e "❌ SQLite directory not found"
    fi
    echo
    
    # Test PostgreSQL using the MCP database insert server
    echo -e "${YELLOW}Testing PostgreSQL via MCP Database Insert Server...${NC}"
    if command -v /home/daclab-work001/DEV/mcp/mcp-python-env/bin/python &> /dev/null; then
        echo -e "✅ Python environment found"
        
        # Test database insert server tool
        echo '{"database_type": "postgresql", "connection_string": "postgresql://mcp_data_admin:McP_D4ta_Pr0d_2024!@localhost:5433/mcp_data_prod"}' > /tmp/test_db_conn.json
        
        # This would require the actual server to be running, so we'll just check if the module loads
        if /home/daclab-work001/DEV/mcp/mcp-python-env/bin/python -c "import mcp_server_db_insert" 2>/dev/null; then
            echo -e "✅ MCP Database Insert Server module loads successfully"
        else
            echo -e "❌ MCP Database Insert Server module not found"
        fi
        
        rm -f /tmp/test_db_conn.json
    else
        echo -e "❌ Python environment not found"
    fi
    echo
}

show_env() {
    echo -e "${GREEN}🔧 Environment Variables Status:${NC}"
    echo
    
    # Load environment
    source "$HUB_DIR/load-env.sh" 2>/dev/null | grep -E "(✅|❌)"
}

create_test() {
    echo -e "${GREEN}🧪 Creating Test Database Configuration...${NC}"
    echo
    
    # Create a test configuration file
    cat > "$CREDENTIALS_DIR/.env.test" << EOF
# Test Database Configuration
# This file contains test database connections for development

# Test SQLite Database
TEST_SQLITE_URL=sqlite:///tmp/test_mcp.db

# Test PostgreSQL (if available)
TEST_POSTGRES_URL=postgresql://postgres:test@localhost:5432/test_mcp

# Test MongoDB (if available)
TEST_MONGODB_URL=mongodb://localhost:27017/test_mcp

# Test Redis (if available)
TEST_REDIS_URL=redis://localhost:6379/15

# Test MySQL (if available)
TEST_MYSQL_URL=mysql://root:test@localhost:3306/test_mcp
EOF
    
    echo -e "✅ Test database configuration created at: $CREDENTIALS_DIR/.env.test"
    echo -e "${YELLOW}Note: This uses safe test databases that won't affect production data${NC}"
    echo
}

backup_config() {
    echo -e "${GREEN}💾 Backing up Database Configuration...${NC}"
    echo
    
    BACKUP_DIR="$CREDENTIALS_DIR/backups"
    mkdir -p "$BACKUP_DIR"
    
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_FILE="$BACKUP_DIR/db_config_backup_$TIMESTAMP.tar.gz"
    
    # Backup database-related configuration files
    tar -czf "$BACKUP_FILE" -C "$CREDENTIALS_DIR" .env .env.databases .env.test 2>/dev/null
    
    if [ -f "$BACKUP_FILE" ]; then
        echo -e "✅ Configuration backed up to: $BACKUP_FILE"
    else
        echo -e "❌ Backup failed"
    fi
    echo
}

restore_config() {
    echo -e "${GREEN}📥 Available Configuration Backups:${NC}"
    echo
    
    BACKUP_DIR="$CREDENTIALS_DIR/backups"
    if [ -d "$BACKUP_DIR" ]; then
        ls -la "$BACKUP_DIR"/db_config_backup_*.tar.gz 2>/dev/null | head -10
        echo
        echo -e "${YELLOW}To restore a backup, run:${NC}"
        echo "  cd $CREDENTIALS_DIR && tar -xzf backups/[backup_file_name]"
    else
        echo -e "${YELLOW}No backups found${NC}"
    fi
    echo
}

# Main script logic
case "$1" in
    list-databases)
        print_header
        list_databases
        ;;
    test-connection)
        print_header
        test_connection
        ;;
    show-env)
        print_header
        show_env
        ;;
    create-test)
        print_header
        create_test
        ;;
    backup-config)
        print_header
        backup_config
        ;;
    restore-config)
        print_header
        restore_config
        ;;
    help|--help|-h)
        print_header
        show_usage
        ;;
    "")
        print_header
        echo -e "${YELLOW}No command specified. Available commands:${NC}"
        echo
        show_usage
        ;;
    *)
        print_header
        echo -e "${RED}Unknown command: $1${NC}"
        echo
        show_usage
        exit 1
        ;;
esac
