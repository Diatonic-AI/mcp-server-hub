#!/usr/bin/env node

/**
 * Cross-platform MCP Credential Manager
 * Handles secure credential storage and environment variable management
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const os = require('os');

class MCPCredentialManager {
    constructor() {
        this.platform = process.platform;
        this.credentialsDir = this.getCredentialsDirectory();
        this.templatePath = path.join(this.credentialsDir, '.env.template');
        this.envPath = path.join('.', '.env');
        
        // Ensure credentials directory exists
        if (!fs.existsSync(this.credentialsDir)) {
            fs.mkdirSync(this.credentialsDir, { recursive: true, mode: 0o700 });
        }
    }

    getCredentialsDirectory() {
        switch (this.platform) {
            case 'win32':
                return path.join(process.env.APPDATA || '.', 'mcp-credentials');
            case 'darwin':
                return path.join(os.homedir(), '.mcp-credentials');
            default: // linux, wsl
                return path.join(os.homedir(), '.mcp-credentials');
        }
    }

    generateTemplate() {
        const template = `# MCP Server Configuration Template
# Copy this file to .env and fill in your credentials

# GitHub Integration
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token_here

# Google Services
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
GDRIVE_CREDENTIALS_PATH=.credentials/.gdrive-server-credentials.json

# Database Connections
DATABASE_URL=postgresql://user:password@localhost:5432/database_name
REDIS_URL=redis://localhost:6379

# PostgreSQL (for Docker)
POSTGRES_PASSWORD=secure_random_password
REDIS_PASSWORD=secure_random_redis_password

# Platform Detection (auto-filled)
PLATFORM=${this.platform}
HOME_DIR=${os.homedir()}
NODE_ENV=development

# Paths (auto-configured based on platform)
MEMORY_FILE_PATH=${this.platform === 'win32' ? '.mcp-memory.json' : './.mcp-memory.json'}
SQLITE_DB_PATH=${this.platform === 'win32' ? '.sqlite-db.db' : './.sqlite-db.db'}

# Browser Executable Paths
PUPPETEER_EXECUTABLE_PATH=${this.getBrowserPath()}
`;

        fs.writeFileSync(this.templatePath, template, { mode: 0o600 });
        console.log(`✅ Template created at: ${this.templatePath}`);
        return template;
    }

    getBrowserPath() {
        switch (this.platform) {
            case 'win32':
                return 'C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe';
            case 'darwin':
                return '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
            default:
                return '/usr/bin/chromium-browser';
        }
    }

    validateCredentials() {
        if (!fs.existsSync(this.envPath)) {
            console.log('❌ .env file not found. Run: node credential-manager.js generate');
            return false;
        }

        const envContent = fs.readFileSync(this.envPath, 'utf8');
        const missingVars = [];

        const requiredVars = [
            'GITHUB_PERSONAL_ACCESS_TOKEN',
            'GOOGLE_MAPS_API_KEY',
            'DATABASE_URL',
            'REDIS_URL'
        ];

        requiredVars.forEach(varName => {
            if (!envContent.includes(`${varName}=`) || envContent.includes(`${varName}=your_`)) {
                missingVars.push(varName);
            }
        });

        if (missingVars.length > 0) {
            console.log('❌ Missing or placeholder credentials:');
            missingVars.forEach(varName => console.log(`   - ${varName}`));
            return false;
        }

        console.log('✅ All required credentials are configured');
        return true;
    }

    secureCredentialsFile() {
        if (fs.existsSync(this.envPath)) {
            if (this.platform !== 'win32') {
                fs.chmodSync(this.envPath, 0o600);
                console.log('✅ Secured .env file permissions (owner read/write only)');
            }
        }
    }

    generateSecrets() {
        const secrets = {
            postgres_password: crypto.randomBytes(32).toString('hex'),
            redis_password: crypto.randomBytes(32).toString('hex'),
            jwt_secret: crypto.randomBytes(64).toString('hex')
        };

        const secretsDir = path.join('.', 'platform-configs', 'docker', 'secrets');
        if (!fs.existsSync(secretsDir)) {
            fs.mkdirSync(secretsDir, { recursive: true, mode: 0o700 });
        }

        Object.entries(secrets).forEach(([name, value]) => {
            const secretFile = path.join(secretsDir, `${name}.txt`);
            fs.writeFileSync(secretFile, value, { mode: 0o600 });
        });

        console.log('✅ Generated secure random passwords for Docker services');
        return secrets;
    }

    getPlatformConfig() {
        const configMap = {
            'win32': 'platform-configs/windows/mcp-hub-config-windows.json',
            'darwin': 'platform-configs/linux/mcp-hub-config-linux.json', // macOS uses Linux config
            'linux': 'platform-configs/linux/mcp-hub-config-linux.json'
        };

        return configMap[this.platform] || configMap['linux'];
    }

    showStatus() {
        console.log('📊 MCP Credential Manager Status');
        console.log('================================');
        console.log(`Platform: ${this.platform}`);
        console.log(`Credentials Dir: ${this.credentialsDir}`);
        console.log(`Template: ${fs.existsSync(this.templatePath) ? '✅' : '❌'}`);
        console.log(`Environment: ${fs.existsSync(this.envPath) ? '✅' : '❌'}`);
        console.log(`Config File: ${this.getPlatformConfig()}`);
        
        if (fs.existsSync(this.envPath)) {
            this.validateCredentials();
        }
    }
}

// CLI Interface
const manager = new MCPCredentialManager();
const command = process.argv[2];

switch (command) {
    case 'generate':
        manager.generateTemplate();
        console.log('\n📋 Next steps:');
        console.log('1. Copy the template to .env: cp .mcp-credentials/.env.template .env');
        console.log('2. Edit .env and fill in your actual credentials');
        console.log('3. Run: node credential-manager.js validate');
        break;
    
    case 'validate':
        manager.validateCredentials();
        manager.secureCredentialsFile();
        break;
    
    case 'secrets':
        manager.generateSecrets();
        break;
    
    case 'status':
        manager.showStatus();
        break;
    
    case 'config':
        console.log(`Platform config file: ${manager.getPlatformConfig()}`);
        break;
    
    default:
        console.log('🔐 MCP Credential Manager');
        console.log('Usage: node credential-manager.js [command]');
        console.log('');
        console.log('Commands:');
        console.log('  generate  - Create .env template');
        console.log('  validate  - Check credential configuration');
        console.log('  secrets   - Generate Docker secrets');
        console.log('  status    - Show current status');
        console.log('  config    - Show platform config path');
        break;
}

module.exports = MCPCredentialManager;
