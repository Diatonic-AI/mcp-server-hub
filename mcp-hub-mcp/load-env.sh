#!/bin/bash

# =============================================================================
# MCP Hub Environment Loader
# =============================================================================
# This script loads environment variables from the .credentials directory
# for use with the MCP Hub server.

# Set credentials directory path
CREDENTIALS_DIR="/home/daclab-work001/DEV/mcp/.credentials"

# Function to load environment file
load_env_file() {
    local env_file="$1"
    if [ -f "$env_file" ]; then
        echo "Loading environment from: $env_file"
        # Load variables line by line, ignoring comments and empty lines
        while IFS= read -r line; do
            # Skip empty lines and comments
            if [[ "$line" =~ ^[[:space:]]*$ ]] || [[ "$line" =~ ^[[:space:]]*# ]]; then
                continue
            fi
            # Export valid variable assignments
            if [[ "$line" =~ ^[a-zA-Z_][a-zA-Z0-9_]*= ]]; then
                export "$line"
            fi
        done < "$env_file"
    else
        echo "Warning: Environment file not found: $env_file"
    fi
}

echo "=== MCP Hub Environment Loader ==="
echo "Loading environment variables from: $CREDENTIALS_DIR"
echo

# Load main environment file
load_env_file "$CREDENTIALS_DIR/.env"

# Load database-specific environment file
load_env_file "$CREDENTIALS_DIR/.env.databases"

# Load other specific environment files if they exist
load_env_file "$CREDENTIALS_DIR/.env.github"
load_env_file "$CREDENTIALS_DIR/.env.googledrive"
load_env_file "$CREDENTIALS_DIR/.env.googlemaps"

# Verify some key variables are loaded
echo
echo "=== Environment Variables Verification ==="

# Check database connections
if [ -n "$DEFAULT_POSTGRES_URL" ]; then
    echo "✅ PostgreSQL default connection configured"
else
    echo "❌ PostgreSQL default connection not configured"
fi

if [ -n "$DEFAULT_MONGODB_URL" ]; then
    echo "✅ MongoDB default connection configured"
else
    echo "❌ MongoDB default connection not configured"
fi

if [ -n "$DEFAULT_REDIS_URL" ]; then
    echo "✅ Redis default connection configured"
else
    echo "❌ Redis default connection not configured"
fi

if [ -n "$DEFAULT_MYSQL_URL" ]; then
    echo "✅ MySQL default connection configured"
else
    echo "❌ MySQL default connection not configured"
fi

if [ -n "$DEFAULT_SQLITE_URL" ]; then
    echo "✅ SQLite default connection configured"
else
    echo "❌ SQLite default connection not configured"
fi

# Check API keys
if [ -n "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
    echo "✅ GitHub token configured"
else
    echo "❌ GitHub token not configured"
fi

if [ -n "$GOOGLE_MAPS_API_KEY" ]; then
    echo "✅ Google Maps API key configured"
else
    echo "❌ Google Maps API key not configured"
fi

# Check file paths
if [ -n "$GDRIVE_CREDENTIALS_PATH" ] && [ -f "$GDRIVE_CREDENTIALS_PATH" ]; then
    echo "✅ Google Drive credentials file found"
else
    echo "❌ Google Drive credentials file not found"
fi

if [ -n "$MEMORY_FILE_PATH" ]; then
    echo "✅ Memory file path configured"
else
    echo "❌ Memory file path not configured"
fi

echo
echo "=== MCP Database Insert Server Configuration ==="
echo "Max Batch Size: ${MCP_DB_INSERT_MAX_BATCH_SIZE:-'not set'}"
echo "Connection Timeout: ${MCP_DB_INSERT_CONNECTION_TIMEOUT:-'not set'}"
echo "Debug Mode: ${MCP_DB_INSERT_ENABLE_DEBUG:-'not set'}"
echo "Environment: ${NODE_ENV:-'not set'}"

# Apply selective proxy configuration
if [ -f "/etc/profile.d/proxy_config.sh" ]; then
    source /etc/profile.d/proxy_config.sh
fi

echo
echo "Environment loading complete!"
echo "You can now run the MCP Hub with these environment variables loaded."
echo
echo "Network Configuration:"
echo "  - Browsers: Direct internet access"
echo "  - Databases: Via HAProxy load balancer (10.0.0.10)"
echo "  - Docker: Via Squid proxy when needed"
echo
echo "Usage examples:"
echo "  source load-env.sh && node dist/index.js"
echo "  source load-env.sh && npm run dev"
echo "  source load-env.sh && npx @modelcontextprotocol/inspector node dist/index.js"
echo
