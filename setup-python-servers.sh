#!/bin/bash

echo "🔧 Setting up Python MCP servers..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if command was successful
check_success() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1 completed successfully${NC}"
    else
        echo -e "${RED}❌ $1 failed${NC}"
        return 1
    fi
}

# Install Git server
echo -e "${YELLOW}📦 Installing Git MCP server...${NC}"
cd /home/daclab-work001/DEV/mcp/servers/src/mcp-servers/src/git
pip install -e . --quiet
check_success "Git server installation"

# Install Time server
echo -e "${YELLOW}📦 Installing Time MCP server...${NC}"
cd /home/daclab-work001/DEV/mcp/servers/src/mcp-servers/src/time
pip install -e . --quiet
check_success "Time server installation"

# Install Fetch server
echo -e "${YELLOW}📦 Installing Fetch MCP server...${NC}"
cd /home/daclab-work001/DEV/mcp/servers/src/mcp-servers/src/fetch
pip install -e . --quiet
check_success "Fetch server installation"

echo -e "${GREEN}🎉 All Python MCP servers installed successfully!${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. For GitHub server: Set up GitHub Personal Access Token"
echo "2. For Google Drive: Set up Google Cloud OAuth credentials"
echo "3. For Google Maps: Get Google Maps API key"
echo "4. For databases: Configure PostgreSQL/Redis/SQLite connections"
echo "5. For Puppeteer: Install Chromium browser"
echo ""
echo "Run the MCP Hub with:"
echo "node /home/daclab-work001/DEV/mcp/mcp-hub-mcp/dist/index.js --config-path /home/daclab-work001/DEV/mcp/mcp-hub-config-complete.json"
