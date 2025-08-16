# Cross-Platform MCP Server Hub 🚀

A comprehensive, containerized solution for running MCP (Model Context Protocol) servers across Windows, Linux, WSL2, and Docker environments.

[![GitHub](https://img.shields.io/github/license/Diatonic-AI/mcp-server-hub)](https://github.com/Diatonic-AI/mcp-server-hub/blob/main/LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20WSL2%20%7C%20Docker-blue)]()
[![Node.js](https://img.shields.io/badge/node-%3E%3D18.0.0-green)]()
[![Python](https://img.shields.io/badge/python-%3E%3D3.8-green)]()

## ✨ Features

### 🐳 **Full Containerization**
- Docker containers for Node.js and Python MCP servers
- Isolated environments with all dependencies pre-installed
- Production-ready with health checks and proper resource management

### 🔧 **Cross-Platform Configuration**
- Automatically detects platform (Windows, Linux, macOS, WSL2)
- Platform-specific MCP Hub configurations
- Path and command adaptation for each environment

### 🔐 **Secure Credential Management**
- Secure credential template system
- No secrets committed to repository
- Cross-platform credential storage (Windows: `%APPDATA%`, Linux/macOS: `~/.mcp-credentials`)
- Automatic permission management (`0600` on Unix systems)

### 🚀 **One-Command Setup**
- **Linux/macOS**: `./start-mcp.sh setup`
- **Windows**: `start-mcp.bat setup`  
- **Docker**: `./start-mcp.sh docker`

### 📦 **Comprehensive MCP Server Collection**

#### Core Servers
- **filesystem** - Safe file operations with access control
- **memory** - Persistent knowledge graph and entity relationships
- **sequential-thinking** - Structured reasoning and problem-solving workflows
- **everything** - Reference server with multiple capabilities

#### Version Control & Development
- **git** - Repository operations, commits, branches, diffs
- **time** - Timezone handling and date operations
- **fetch** - HTTP requests and web content retrieval

#### External Integrations
- **github** - Repository management, issues, pull requests
- **google-drive** - File access and workspace document conversion
- **google-maps** - Location services, directions, geocoding

#### Database Support
- **postgresql** - Database querying and schema inspection
- **redis** - Key-value operations and caching
- **sqlite** - Local database operations and business intelligence

#### Browser Automation
- **puppeteer** - Web scraping, screenshots, browser automation

## 🎯 Quick Start

### Prerequisites

**All Platforms:**
- Node.js 18+ and npm
- Python 3.8+ 
- Git

**Additional for Docker:**
- Docker and Docker Compose

**Platform-specific:**
- **Windows**: Visual Studio Build Tools or Visual Studio
- **Linux**: `build-essential` package
- **Browser automation**: Chrome/Chromium installed

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Diatonic-AI/mcp-server-hub.git
cd mcp-server-hub

# Run platform-appropriate setup
# Linux/macOS/WSL2:
./start-mcp.sh setup

# Windows:
start-mcp.bat setup
```

### 2. Configure Credentials

```bash
# Generate credential template
node credential-manager.js generate

# Edit the .env file with your actual credentials
# Linux/macOS:
cp ~/.mcp-credentials/.env.template .env
nano .env

# Windows:
copy %APPDATA%\mcp-credentials\.env.template .env
notepad .env
```

Required credentials:
- `GITHUB_PERSONAL_ACCESS_TOKEN` - GitHub API access
- `GOOGLE_MAPS_API_KEY` - Google Maps functionality  
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

### 3. Start MCP Servers

```bash
# Native platform execution
./start-mcp.sh run        # Linux/macOS/WSL2
start-mcp.bat run         # Windows

# Docker containerized execution  
./start-mcp.sh docker     # All platforms with Docker
```

### 4. Configure Your MCP Client

Use the appropriate configuration file for your platform:

- **Linux/macOS/WSL2**: `platform-configs/linux/mcp-hub-config-linux.json`
- **Windows**: `platform-configs/windows/mcp-hub-config-windows.json`  
- **Docker**: `platform-configs/docker/mcp-hub-config-docker.json`

## 🛠️ Advanced Usage

### Docker Compose Management

```bash
# View logs
docker-compose -f platform-configs/docker/docker-compose.yml logs -f

# Stop services
docker-compose -f platform-configs/docker/docker-compose.yml down

# Rebuild containers
docker-compose -f platform-configs/docker/docker-compose.yml up --build -d
```

### Credential Management Commands

```bash
node credential-manager.js status     # Show current configuration status
node credential-manager.js validate   # Validate credential completeness  
node credential-manager.js secrets    # Generate Docker secrets
node credential-manager.js config     # Show platform config path
```

### Development Mode

```bash
# Install Node.js dependencies
cd servers && npm install && npm run build-all

# Activate Python environment  
source mcp-python-env/bin/activate    # Linux/macOS
mcp-python-env\Scripts\activate.bat   # Windows

# Install Python MCP servers in development mode
pip install -e servers/src/mcp-servers/src/git
pip install -e servers/src/mcp-servers/src/time
pip install -e servers/src/mcp-servers/src/fetch
```

## 📁 Project Structure

```
mcp-server-hub/
├── platform-configs/           # Platform-specific configurations
│   ├── windows/                # Windows-specific paths and executables
│   ├── linux/                  # Linux/macOS/WSL2 configurations  
│   └── docker/                 # Docker Compose and container configs
├── servers/                    # MCP server implementations
│   ├── src/mcp-servers/       # Core MCP servers (Node.js)
│   └── src/mcp-servers-archived/ # Additional servers
├── credential-manager.js       # Cross-platform credential management
├── start-mcp.sh               # Linux/macOS startup script
├── start-mcp.bat              # Windows startup script  
├── Dockerfile.node            # Node.js server container
├── Dockerfile.python          # Python server container
└── requirements.txt           # Python dependencies
```

## 🔧 Configuration Details

### MCP Hub Configuration

Each platform has its own configuration file that handles:
- **Path formatting** (forward vs backslashes)
- **Executable locations** (different Python/Node paths)
- **Environment variables** (HOME vs USERPROFILE)
- **Browser paths** (Chrome vs Chromium locations)

### Environment Variables

The system automatically configures based on detected platform:

```bash
PLATFORM=linux|win32|darwin      # Auto-detected
HOME_DIR=/path/to/home           # Platform-appropriate
MEMORY_FILE_PATH=./memory.json   # Relative path handling
PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium  # Browser location
```

## 🐳 Docker Architecture

The Docker setup provides:
- **Multi-stage builds** optimized for production
- **Health checks** for all services
- **Volume management** for persistent data
- **Network isolation** with secure inter-service communication
- **Secret management** via Docker secrets
- **Database initialization** with PostgreSQL and Redis

### Container Services:
- `mcp-node` - Node.js MCP servers
- `mcp-python` - Python MCP servers  
- `postgres` - PostgreSQL database
- `redis` - Redis cache
- `mcp-hub` - Central MCP Hub coordinator

## 📊 Monitoring and Logs

### Log Locations:
- **Native**: `./logs/` directory
- **Docker**: `docker-compose logs [service-name]`
- **Credential Manager**: `~/.mcp-credentials/` or `%APPDATA%\mcp-credentials\`

### Health Checks:
```bash
# Check all service status
./start-mcp.sh status    # Linux/macOS
start-mcp.bat status     # Windows

# Docker service health
docker-compose -f platform-configs/docker/docker-compose.yml ps
```

## 🛡️ Security Considerations

- **No secrets in repository** - All credentials are templated
- **Secure file permissions** - Credential files automatically set to `0600`
- **Platform-appropriate storage** - Uses OS-standard credential locations
- **Docker secrets** - Production-ready secret management
- **Network isolation** - Docker containers use internal networks
- **Regular updates** - Dependency management via dependabot

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/Diatonic-AI/mcp-server-hub/issues)
- **Documentation**: [Wiki](https://github.com/Diatonic-AI/mcp-server-hub/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/Diatonic-AI/mcp-server-hub/discussions)

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for the MCP specification
- [Model Context Protocol](https://github.com/modelcontextprotocol) community
- All contributors to the individual MCP server implementations

---

**Made with ❤️ by [Diatonic AI](https://github.com/Diatonic-AI)**
