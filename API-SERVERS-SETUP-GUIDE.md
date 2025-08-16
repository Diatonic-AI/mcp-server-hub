# API Servers Setup Guide

## Overview
This guide covers the complete setup for all three API-based MCP servers:
- **GitHub Server**: Repository management, issues, PRs, code search
- **Google Drive Server**: File access and search in Google Drive  
- **Google Maps Server**: Geocoding, places search, directions

## ✅ Completed Setup

### 🗝️ Google Cloud Project Configuration
- **Project**: `chromatix-central-mgmt` (Global Configuration Project)
- **APIs Enabled**:
  - Google Drive API (`drive.googleapis.com`)
  - Maps Backend API (`maps-backend.googleapis.com`)
  - Geocoding Backend API (`geocoding-backend.googleapis.com`)
  - Places Backend API (`places-backend.googleapis.com`)

### 🔐 Service Account Created
- **Name**: `mcp-services`
- **Email**: `mcp-services@chromatix-central-mgmt.iam.gserviceaccount.com`
- **Roles**: `roles/viewer`
- **Key File**: `/home/daclab-work001/DEV/mcp/.credentials/google-drive-service-account.json`

### 🗺️ Google Maps API Key ✅
- **API Key**: `${GOOGLE_MAPS_API_KEY}`
- **Restrictions**: Limited to Maps, Geocoding, and Places APIs
- **Status**: Ready for use

## 🔧 Remaining Setup Tasks

### 1. GitHub Personal Access Token
**Manual Step Required**: Create GitHub PAT

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Configure:
   - **Name**: "MCP Server - Development"
   - **Expiration**: 90 days (or as needed)
   - **Scopes**:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `read:org` (Read org membership)
     - ✅ `read:user` (Read user profile data)
4. **Copy the token** and update `.env.api-servers`

### 2. Google Drive OAuth Credentials  
**Manual Step Required**: Create OAuth Client

The service account approach may not work for Google Drive personal file access. You need OAuth credentials:

1. Go to: https://console.cloud.google.com/apis/credentials?project=chromatix-central-mgmt
2. Click "CREATE CREDENTIALS" → "OAuth client ID"
3. Configure:
   - **Application type**: Desktop application
   - **Name**: "MCP Google Drive Client"
4. Download the JSON file as: `/home/daclab-work001/DEV/mcp/.credentials/google-drive-oauth-client.json`
5. Update the environment variable to point to this file

## 📂 Directory Structure
```
/home/daclab-work001/DEV/mcp/
├── .env.api-servers                                    # Environment variables
├── .credentials/                                       # Credential files (secure)
│   ├── google-drive-service-account.json              # Service account (created)
│   └── google-drive-oauth-client.json                 # OAuth client (needs creation)
└── servers/src/mcp-servers-archived/src/
    ├── github/                                         # GitHub server
    ├── gdrive/                                         # Google Drive server  
    └── google-maps/                                    # Google Maps server
```

## 🔒 Security Notes
- All credential files are stored in `/home/daclab-work001/DEV/mcp/.credentials/`
- The `.env.api-servers` file contains API keys and paths
- **Never commit these files to version control**
- Add to `.gitignore`: `.env.api-servers`, `.credentials/`

## 🧪 Testing Commands

### Test Google Maps Server (Ready)
```bash
cd /home/daclab-work001/DEV/mcp/servers/src/mcp-servers-archived/src/google-maps
export GOOGLE_MAPS_API_KEY="${GOOGLE_MAPS_API_KEY}"
npm run build  # if not built
node dist/index.js
```

### Test GitHub Server (After PAT setup)
```bash
cd /home/daclab-work001/DEV/mcp/servers/src/mcp-servers-archived/src/github
export GITHUB_PERSONAL_ACCESS_TOKEN="your_token_here"
npm run build  # if not built  
node dist/index.js
```

### Test Google Drive Server (After OAuth setup)
```bash
cd /home/daclab-work001/DEV/mcp/servers/src/mcp-servers-archived/src/gdrive
export GDRIVE_CREDENTIALS_PATH="/home/daclab-work001/DEV/mcp/.credentials/google-drive-oauth-client.json"
npm run build  # if not built
node dist/index.js auth  # First run for authentication
node dist/index.js       # Normal operation
```

## 📋 MCP Hub Integration

Once all credentials are set up, the servers can be integrated into the MCP Hub configuration:

```json
{
  "mcpServers": {
    "github": {
      "command": "node",
      "args": ["/home/daclab-work001/DEV/mcp/servers/src/mcp-servers-archived/src/github/dist/index.js"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    },
    "google-drive": {
      "command": "node", 
      "args": ["/home/daclab-work001/DEV/mcp/servers/src/mcp-servers-archived/src/gdrive/dist/index.js"],
      "env": {
        "GDRIVE_CREDENTIALS_PATH": "${GOOGLE_DRIVE_CREDENTIALS_PATH}"
      }
    },
    "google-maps": {
      "command": "node",
      "args": ["/home/daclab-work001/DEV/mcp/servers/src/mcp-servers-archived/src/google-maps/dist/index.js"], 
      "env": {
        "GOOGLE_MAPS_API_KEY": "${GOOGLE_MAPS_API_KEY}"
      }
    }
  }
}
```

## ✅ Next Steps
1. **Create GitHub Personal Access Token** (manual)
2. **Create Google Drive OAuth Client** (manual) 
3. **Test all three servers** with credentials
4. **Integrate into MCP Hub** configuration
5. **Verify end-to-end functionality**

The infrastructure is ready - only the manual credential creation steps remain!
