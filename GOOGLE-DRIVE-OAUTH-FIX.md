# Google Drive OAuth Client Fix

## 🚨 Issue: redirect_uri_mismatch Error

**Problem**: OAuth client was created as "Web application" but Google Drive MCP server needs "Desktop application" type.

## ✅ Solution: Update OAuth Client

### Go to Google Cloud Console:
https://console.cloud.google.com/apis/credentials?project=chromatix-central-mgmt

### Edit existing OAuth client:
**Client ID**: `514503039126-tcjnhd1g236s6t78ldcavq9m96n8jhnj.apps.googleusercontent.com`

### Change configuration:
1. **Application type**: Change from "Web application" to **"Desktop application"** 
2. **Authorized redirect URIs**: Delete all URIs (Desktop apps don't need them)
3. **Save changes**
4. **Download new JSON file**

### Replace credentials file:
```bash
# Move new downloaded file to:
/home/daclab-work001/DEV/mcp/.credentials/google-drive-oauth-client.json
```

## 🧪 Test After Fix:
```bash
cd /home/daclab-work001/DEV/mcp/servers/src/mcp-servers-archived/src/gdrive
GDRIVE_OAUTH_PATH="/home/daclab-work001/DEV/mcp/.credentials/google-drive-oauth-client.json" \
GDRIVE_CREDENTIALS_PATH="/home/daclab-work001/DEV/mcp/.credentials/.gdrive-server-credentials.json" \
node dist/index.js auth
```

**Expected**: Browser opens for Google sign-in, authentication succeeds, credentials saved.

## 📝 Technical Details:
- **Desktop applications**: Use built-in OAuth flow, no redirect URIs needed
- **Web applications**: Require explicit redirect URI matching
- **@google-cloud/local-auth**: Designed for desktop/CLI applications
