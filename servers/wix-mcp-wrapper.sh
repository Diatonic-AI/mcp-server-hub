#!/bin/bash

# Set environment
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export HOME="/home/daclab-work001"

# Load Wix OAuth credentials from auth directory
WIX_AUTH_DIR="$HOME/.wix/auth"
if [ -f "$WIX_AUTH_DIR/account.json" ]; then
    # Extract access token from account.json
    export WIX_ACCESS_TOKEN=$(cat "$WIX_AUTH_DIR/account.json" | grep -o '"accessToken":"[^"]*' | cut -d'"' -f4)
    echo "Wix OAuth credentials loaded" >&2
else
    echo "Warning: Wix OAuth credentials not found at $WIX_AUTH_DIR/account.json" >&2
    echo "Please run 'wix login' to authenticate first" >&2
fi

# Change to home directory
cd "$HOME"

# Run the Wix MCP remote server with OAuth
exec /usr/bin/npx -y @wix/mcp-remote@latest https://mcp.wix.com/mcp
