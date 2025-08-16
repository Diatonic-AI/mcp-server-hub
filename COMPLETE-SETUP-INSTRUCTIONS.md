# Complete Setup Instructions for All 14 MCP Servers

This guide provides detailed setup instructions for every single MCP server in your hub configuration.

## 🎯 Server Overview

| Server | Status | Type | Setup Required |
|--------|---------|------|----------------|
| 1. Filesystem | ✅ Ready | Node.js | None |
| 2. Memory | ✅ Ready | Node.js | None |
| 3. Sequential Thinking | ✅ Ready | Node.js | None |
| 4. Everything | ✅ Ready | Node.js | None |
| 5. Git | ⚠️ Dependencies | Python | pip install |
| 6. Time | ⚠️ Dependencies | Python | pip install |
| 7. Fetch | ⚠️ Dependencies | Python | pip install |
| 8. GitHub | 🔑 API Key | Node.js | Personal Access Token |
| 9. Google Drive | 🔑 OAuth | Node.js | Google Cloud Setup |
| 10. Google Maps | 🔑 API Key | Node.js | Google Maps API |
| 11. PostgreSQL | 🗄️ Database | Node.js | Database Connection |
| 12. Redis | 🗄️ Database | Node.js | Redis Server |
| 13. SQLite | 🗄️ Database | Node.js | Auto-created |
| 14. Puppeteer | 🌐 Browser | Node.js | Chromium Install |

---

## 📦 PHASE 1: Ready-to-Use Servers (1-4)

These servers work immediately with no additional setup required.

### 1. Filesystem Server ✅
**Status**: Ready  
**Configuration**: Already configured with proper directory access
```json
{
  "command": "node",
  "args": [
    "/home/daclab-work001/DEV/mcp/servers/src/mcp-servers/src/filesystem/dist/index.js",
    "/home/daclab-work001/DEV/mcp",
    "/home/daclab-work001",
    "/tmp",
    "/home/daclab-work001/Cloud-Drives"
  ]
}
```
**Capabilities**: File operations, directory management, search, secure access control  
**Test Command**: Already working in minimal config

### 2. Memory Server ✅
**Status**: Ready  
**Configuration**: Configured with persistent storage
```json
{
  "env": {
    "MEMORY_FILE_PATH": "/home/daclab-work001/DEV/mcp/.mcp-memory.json"
  }
}
```
**Capabilities**: Persistent knowledge graph, entities and relations, search and retrieval  
**Storage Location**: `/home/daclab-work001/DEV/mcp/.mcp-memory.json` (auto-created)

### 3. Sequential Thinking Server ✅
**Status**: Ready  
**Configuration**: No additional configuration needed
**Capabilities**: Structured problem solving, thought sequences, reasoning workflows

### 4. Everything Server ✅
**Status**: Ready  
**Configuration**: Reference server with multiple tools
**Capabilities**: Reference tools, multiple capabilities, testing and examples

---

## 🐍 PHASE 2: Python Servers (5-7)

These require Python dependencies to be installed.

### 5. Git Server ⚠️
**Setup Required**: Python dependencies

#### Step 1: Install Dependencies
```bash
cd /home/daclab-work001/DEV/mcp/servers/src/mcp-servers/src/git
pip install -e .
```

#### Step 2: Verify Installation
```bash
python3 -c "import mcp_server_git; print('Git server ready')"
```

#### Step 3: Test
```bash
cd /home/daclab-work001/DEV/mcp
python3 -m mcp_server_git --help
```

**Capabilities**: Repository operations, commit management, branch operations, diff analysis

### 6. Time Server ⚠️
**Setup Required**: Python dependencies

#### Step 1: Install Dependencies
```bash
cd /home/daclab-work001/DEV/mcp/servers/src/mcp-servers/src/time
pip install -e .
```

#### Step 2: Verify Installation
```bash
python3 -c "import mcp_server_time; print('Time server ready')"
```

#### Step 3: Test
```bash
python3 -m mcp_server_time --help
```

**Capabilities**: Time conversion, timezone handling, date operations

### 7. Fetch Server ⚠️
**Setup Required**: Python dependencies

#### Step 1: Install Dependencies
```bash
cd /home/daclab-work001/DEV/mcp/servers/src/mcp-servers/src/fetch
pip install -e .
```

#### Step 2: Verify Installation
```bash
python3 -c "import mcp_server_fetch; print('Fetch server ready')"
```

#### Step 3: Test
```bash
python3 -m mcp_server_fetch --help
```

**Capabilities**: Web content retrieval, HTTP requests, content conversion

### 📝 Python Servers Quick Setup
Run all Python installs at once:
```bash
./setup-python-servers.sh
```

---

## 🔑 PHASE 3: API Key Servers (8-10)

These require external API keys and credentials.

### 8. GitHub Server 🔑
**Setup Required**: GitHub Personal Access Token

#### Step 1: Create GitHub Token
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `read:org` (Read org membership)
   - ✅ `read:user` (Read user profile data)
4. Set expiration (recommend 90 days or no expiration for development)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again)

#### Step 2: Update Configuration
Edit `/home/daclab-work001/DEV/mcp/mcp-hub-config-complete.json`:
```json
{
  "github": {
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_TOKEN_HERE"
    }
  }
}
```

#### Step 3: Test
```bash
# Test the token works
curl -H "Authorization: token YOUR_GITHUB_TOKEN_HERE" https://api.github.com/user
```

**Capabilities**: Repository management, issue tracking, pull requests, code search

### 9. Google Drive Server 🔑
**Setup Required**: Google Cloud OAuth Setup

#### Step 1: Google Cloud Project Setup
1. Go to: https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable Google Drive API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click "Enable"

#### Step 2: OAuth Consent Screen
1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "Internal" (for personal/organization use)
3. Fill required fields:
   - App name: "MCP Google Drive Server"
   - User support email: Your email
   - Developer contact: Your email
4. Add scope: `https://www.googleapis.com/auth/drive.readonly`
5. Save and continue

#### Step 3: Create OAuth Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Application type: "Desktop application"
4. Name: "MCP Drive Client"
5. Download the JSON file

#### Step 4: Setup Credentials File
```bash
# Move the downloaded file to the correct location
mv ~/Downloads/client_secret_*.json /home/daclab-work001/DEV/mcp/gcp-oauth.keys.json
```

#### Step 5: Run Authentication
```bash
cd /home/daclab-work001/DEV/mcp/servers/src/mcp-servers-archived/src/gdrive
node dist/index.js auth
```
This will:
- Open a browser window
- Ask you to sign in to Google
- Save credentials to `/home/daclab-work001/DEV/mcp/.gdrive-server-credentials.json`

#### Step 6: Verify Setup
```bash
# Check credentials file exists
ls -la /home/daclab-work001/DEV/mcp/.gdrive-server-credentials.json
```

**Capabilities**: File access, search, workspace document conversion

### 10. Google Maps Server 🔑
**Setup Required**: Google Maps API Key

#### Step 1: Enable Maps API
1. Go to: https://console.cloud.google.com/
2. Select your project (same as Google Drive)
3. Go to "APIs & Services" > "Library"
4. Search for "Maps JavaScript API"
5. Click "Enable"

#### Step 2: Create API Key
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "API key"
3. Copy the API key

#### Step 3: Secure the API Key (Recommended)
1. Click "Restrict Key"
2. Under "API restrictions":
   - Select "Restrict key"
   - Choose "Maps JavaScript API"
3. Under "Application restrictions":
   - Choose "HTTP referrers" or "IP addresses" as appropriate
4. Save

#### Step 4: Update Configuration
Edit `/home/daclab-work001/DEV/mcp/mcp-hub-config-complete.json`:
```json
{
  "google-maps": {
    "env": {
      "GOOGLE_MAPS_API_KEY": "AIza_your_actual_api_key_here"
    }
  }
}
```

#### Step 5: Test
```bash
# Test the API key
curl "https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=AIza_your_actual_api_key_here"
```

**Capabilities**: Location services, directions, place details, geocoding

---

## 🗄️ PHASE 4: Database Servers (11-13)

These require database setup and connections.

### 11. PostgreSQL Server 🗄️
**Setup Required**: PostgreSQL database connection

#### Option A: Install PostgreSQL Locally
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE mcp_database;
CREATE USER mcp_user WITH ENCRYPTED PASSWORD 'mcp_secure_password';
GRANT ALL PRIVILEGES ON DATABASE mcp_database TO mcp_user;
\q
```

#### Option B: Use Docker PostgreSQL
```bash
# Run PostgreSQL in Docker
docker run --name mcp-postgres \
  -e POSTGRES_DB=mcp_database \
  -e POSTGRES_USER=mcp_user \
  -e POSTGRES_PASSWORD=mcp_secure_password \
  -p 5432:5432 \
  -d postgres:15
```

#### Step 2: Update Configuration
Edit `/home/daclab-work001/DEV/mcp/mcp-hub-config-complete.json`:
```json
{
  "postgres": {
    "env": {
      "DATABASE_URL": "postgresql://mcp_user:mcp_secure_password@localhost:5432/mcp_database"
    }
  }
}
```

#### Step 3: Test Connection
```bash
# Test connection
psql postgresql://mcp_user:mcp_secure_password@localhost:5432/mcp_database -c "SELECT version();"
```

**Capabilities**: Database querying, schema inspection, read-only access

### 12. Redis Server 🗄️
**Setup Required**: Redis server connection

#### Option A: Install Redis Locally
```bash
# Install Redis
sudo apt update
sudo apt install redis-server

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping
```

#### Option B: Use Docker Redis
```bash
# Run Redis in Docker
docker run --name mcp-redis -p 6379:6379 -d redis:7-alpine
```

#### Step 2: Configuration Already Set
The configuration already points to `redis://localhost:6379` which is the default.

#### Step 3: Test Connection
```bash
# Test Redis connection
redis-cli ping
# Should return: PONG
```

**Capabilities**: Key-value operations, data structures, caching

### 13. SQLite Server 🗄️
**Setup Required**: None (auto-created)

#### Automatic Setup
The SQLite database will be automatically created at:
```
/home/daclab-work001/DEV/mcp/.sqlite-db.db
```

#### Manual Creation (Optional)
```bash
# Create database file manually if desired
sqlite3 /home/daclab-work001/DEV/mcp/.sqlite-db.db "SELECT 'Database created successfully';"
```

#### Test
```bash
# Test SQLite
sqlite3 /home/daclab-work001/DEV/mcp/.sqlite-db.db ".databases"
```

**Capabilities**: Local database operations, business intelligence, SQL queries

---

## 🌐 PHASE 5: System Dependency Server (14)

### 14. Puppeteer Server 🌐
**Setup Required**: Chromium browser installation

#### Step 1: Install Chromium
```bash
# Update package list
sudo apt update

# Install Chromium browser
sudo apt install chromium-browser

# Verify installation
chromium-browser --version
```

#### Step 2: Configuration Already Set
The configuration points to `/usr/bin/chromium-browser` which is correct for Ubuntu.

#### Step 3: Test
```bash
# Test Chromium can start in headless mode
chromium-browser --headless --no-sandbox --disable-gpu --dump-dom https://example.com
```

**Capabilities**: Web scraping, browser automation, screenshot capture

---

## 🧪 TESTING ALL SERVERS

### Test Individual Server Types

#### 1. Test Ready Servers
```bash
cd /home/daclab-work001/DEV/mcp
node mcp-hub-mcp/dist/index.js --config-path ./mcp-hub-config-minimal.json
```

#### 2. Test Python Servers
```bash
# After installing Python dependencies
python3 -m mcp_server_git --help
python3 -m mcp_server_time --help
python3 -m mcp_server_fetch --help
```

#### 3. Test Complete Configuration
```bash
# After all setup is complete
cd /home/daclab-work001/DEV/mcp
node mcp-hub-mcp/dist/index.js --config-path ./mcp-hub-config-complete.json
```

---

## 📋 SETUP CHECKLIST

### Phase 1: Ready Servers ✅
- [x] Filesystem server - Ready
- [x] Memory server - Ready
- [x] Sequential thinking server - Ready
- [x] Everything server - Ready

### Phase 2: Python Dependencies ⚠️
- [ ] Install Git server dependencies
- [ ] Install Time server dependencies  
- [ ] Install Fetch server dependencies
- [ ] Run `./setup-python-servers.sh`

### Phase 3: API Keys 🔑
- [ ] Create GitHub Personal Access Token
- [ ] Set up Google Cloud Project for Drive
- [ ] Create Google Drive OAuth credentials
- [ ] Create Google Maps API key
- [ ] Update configuration with actual keys

### Phase 4: Databases 🗄️
- [ ] Install/setup PostgreSQL
- [ ] Install/setup Redis
- [ ] SQLite (auto-created)
- [ ] Test all database connections

### Phase 5: System Dependencies 🌐
- [ ] Install Chromium browser
- [ ] Test Puppeteer functionality

### Final Testing 🧪
- [ ] Test minimal configuration
- [ ] Test complete configuration
- [ ] Verify all 14 servers connect
- [ ] Configure Warp to use MCP Hub

---

## 🚀 QUICK START COMMANDS

### Install Everything at Once
```bash
# 1. Python servers
./setup-python-servers.sh

# 2. System dependencies
sudo apt update && sudo apt install chromium-browser redis-server postgresql postgresql-contrib

# 3. Start services
sudo systemctl start redis-server postgresql

# 4. Test minimal config
node mcp-hub-mcp/dist/index.js --config-path ./mcp-hub-config-minimal.json
```

### Final Test
```bash
# After all API keys are configured
node mcp-hub-mcp/dist/index.js --config-path ./mcp-hub-config-complete.json
```

## 🎉 SUCCESS!

When complete, you'll have:
- ✅ **14 fully configured MCP servers**
- 🔧 **Flexible minimal/complete configurations**
- 📚 **Complete documentation and troubleshooting**
- 🛠️ **Automated setup scripts**
- 🎯 **Production-ready environment**

Your MCP Hub will be the most comprehensive MCP server management system available!
