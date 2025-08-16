# MCP Hub Complete Setup Guide

This guide provides complete setup instructions for your MCP Hub with all available servers properly configured.

## 📁 File Structure

```
/home/daclab-work001/DEV/mcp/
├── mcp-hub-mcp/                          # MCP Hub server (submodule)
├── typescript-sdk/                       # TypeScript SDK (submodule)
├── servers/src/
│   ├── mcp-servers/                      # Official reference servers
│   │   └── src/
│   │       ├── filesystem/               # ✅ Ready - File operations
│   │       ├── memory/                   # ✅ Ready - Knowledge graph
│   │       ├── sequentialthinking/       # ✅ Ready - Structured thinking
│   │       ├── everything/               # ✅ Ready - Reference tools
│   │       ├── git/                      # ⚠️  Python - Git operations
│   │       ├── time/                     # ⚠️  Python - Time conversion
│   │       └── fetch/                    # ⚠️  Python - Web fetching
│   └── mcp-servers-archived/             # DevOps/Integration servers
│       └── src/
│           ├── github/                   # 🔑 GitHub integration
│           ├── gdrive/                   # 🔑 Google Drive access
│           ├── google-maps/              # 🔑 Google Maps API
│           ├── postgres/                 # 🗄️ PostgreSQL database
│           ├── redis/                    # 🗄️ Redis key-value store
│           ├── sqlite/                   # 🗄️ SQLite database
│           └── puppeteer/                # 🌐 Web automation
├── mcp-hub-config-minimal.json          # ✅ Working - 4 servers
├── mcp-hub-config-complete.json         # 🔧 Complete - All servers
├── mcp-hub-main.json                    # Main Warp configuration
└── setup-python-servers.sh             # Setup script
```

## 🚀 Quick Start (Minimal Setup)

The minimal setup includes 4 working servers that require no external dependencies:

### 1. Test the Minimal Configuration

```bash
cd /home/daclab-work001/DEV/mcp
node mcp-hub-mcp/dist/index.js --config-path ./mcp-hub-config-minimal.json
```

This includes:
- **Filesystem Server** - Secure file operations
- **Memory Server** - Persistent knowledge graph  
- **Sequential Thinking Server** - Structured problem solving
- **Everything Server** - Reference tools and examples

### 2. Use with Warp

Point Warp MCP configuration to:
```
/home/daclab-work001/DEV/mcp/mcp-hub-main.json
```

## 🔧 Complete Setup (All Servers)

### Step 1: Install Python Server Dependencies

```bash
# Run the setup script
./setup-python-servers.sh

# Or manually:
cd /home/daclab-work001/DEV/mcp/servers/src/mcp-servers/src/git && pip install -e .
cd /home/daclab-work001/DEV/mcp/servers/src/mcp-servers/src/time && pip install -e .
cd /home/daclab-work001/DEV/mcp/servers/src/mcp-servers/src/fetch && pip install -e .
```

### Step 2: Configure API Keys and Credentials

#### GitHub Server 🔑
1. Go to [GitHub Personal Access Tokens](https://github.com/settings/tokens)
2. Create token with `repo` scope
3. Edit `mcp-hub-config-complete.json`:
   ```json
   "GITHUB_PERSONAL_ACCESS_TOKEN": "your_actual_token_here"
   ```

#### Google Drive Server 🔑
1. Create [Google Cloud Project](https://console.cloud.google.com/)
2. Enable Google Drive API
3. Create OAuth credentials (Desktop App)
4. Run authentication:
   ```bash
   node /home/daclab-work001/DEV/mcp/servers/src/mcp-servers-archived/src/gdrive/dist/auth.js
   ```
5. Credentials saved automatically to `/home/daclab-work001/DEV/mcp/.gdrive-server-credentials.json`

#### Google Maps Server 🔑
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Maps JavaScript API
3. Create API key
4. Edit `mcp-hub-config-complete.json`:
   ```json
   "GOOGLE_MAPS_API_KEY": "your_actual_api_key_here"
   ```

### Step 3: Configure Databases 🗄️

#### PostgreSQL
```json
"DATABASE_URL": "postgresql://username:password@localhost:5432/database_name"
```

#### Redis
```json
"REDIS_URL": "redis://localhost:6379"
```

#### SQLite
Will be created automatically at:
```
/home/daclab-work001/DEV/mcp/.sqlite-db.db
```

### Step 4: Install Browser Dependencies 🌐

```bash
sudo apt update
sudo apt install chromium-browser
```

### Step 5: Test Complete Configuration

```bash
cd /home/daclab-work001/DEV/mcp
node mcp-hub-mcp/dist/index.js --config-path ./mcp-hub-config-complete.json
```

## 📋 Server Status & Capabilities

### ✅ Ready (No Setup Required)
- **filesystem**: File operations, directory management, search, secure access control
- **memory**: Persistent knowledge graph, entities and relations, search and retrieval  
- **sequential-thinking**: Structured problem solving, thought sequences, reasoning workflows
- **everything**: Reference tools, multiple capabilities, testing and examples

### ⚠️ Requires Dependencies
- **git**: Repository operations, commit management, branch operations, diff analysis
- **time**: Time conversion, timezone handling, date operations
- **fetch**: Web content retrieval, HTTP requests, content conversion

### 🔑 Requires API Keys
- **github**: Repository management, issue tracking, pull requests, code search
- **google-drive**: File access, search, workspace document conversion
- **google-maps**: Location services, directions, place details, geocoding

### 🗄️ Requires Database Setup
- **postgres**: Database querying, schema inspection, read-only access
- **redis**: Key-value operations, data structures, caching
- **sqlite**: Local database operations, business intelligence, SQL queries

### 🌐 Requires System Dependencies
- **puppeteer**: Web scraping, browser automation, screenshot capture

## 🔄 Configuration Files

### mcp-hub-config-minimal.json
- 4 servers, no external dependencies
- Ready to use immediately
- Perfect for testing and basic functionality

### mcp-hub-config-complete.json
- All 14 servers configured
- Includes setup instructions and placeholders
- Requires setup steps above

### mcp-hub-main.json
- Main configuration for Warp
- Points to complete configuration
- Can be switched to minimal if needed

## 🎯 Usage Examples

### With Minimal Setup
```bash
# Start hub
node mcp-hub-mcp/dist/index.js --config-path ./mcp-hub-config-minimal.json

# Available capabilities:
# - File operations in /home/daclab-work001, /tmp, Cloud-Drives
# - Persistent memory and knowledge graphs
# - Structured problem-solving workflows
# - Reference tools and examples
```

### With Complete Setup
```bash
# Start hub with all servers
node mcp-hub-mcp/dist/index.js --config-path ./mcp-hub-config-complete.json

# Additional capabilities:
# - GitHub repository management
# - Google Drive file access
# - Google Maps location services
# - Database operations (PostgreSQL, Redis, SQLite)
# - Web automation with Puppeteer
# - Git repository operations
# - Time/timezone conversions
# - Web content fetching
```

## 🔧 Troubleshooting

### Python Server Issues
```bash
# Check Python path
echo $PYTHONPATH

# Reinstall if needed
pip install -e /home/daclab-work001/DEV/mcp/servers/src/mcp-servers/src/git
```

### Permission Issues
```bash
# Fix file permissions
chmod +x setup-python-servers.sh
chmod -R 755 /home/daclab-work001/DEV/mcp/servers/
```

### API Key Issues
- Verify tokens have correct scopes
- Check rate limits
- Ensure credentials files exist with correct paths

## 📝 Next Steps

1. Start with minimal configuration for immediate use
2. Gradually add services as needed
3. Set up API keys for external integrations
4. Configure databases for data operations
5. Install browser dependencies for web automation

## 🎉 Success!

Your MCP Hub is now fully configured with:
- ✅ 4 immediately working servers (minimal)
- 🔧 14 total servers available (complete)
- 📚 Comprehensive documentation
- 🛠️ Easy setup scripts
- 🎯 Flexible configuration options

Use with Warp by pointing to `/home/daclab-work001/DEV/mcp/mcp-hub-main.json`!
