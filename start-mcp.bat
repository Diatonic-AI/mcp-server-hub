@echo off
REM MCP Server Startup Script (Windows)
setlocal enabledelayedexpansion

REM Color setup (limited on Windows)
set "LOG_PREFIX=[MCP]"

echo %LOG_PREFIX% Starting MCP Server Manager for Windows...

REM Check if we're in the right directory
if not exist "credential-manager.js" (
    echo %LOG_PREFIX% ERROR: Please run this script from the MCP project root directory
    pause
    exit /b 1
)

REM Check for required tools
call :check_requirements
if !errorlevel! neq 0 exit /b 1

REM Handle command line arguments
set "COMMAND=%~1"
if "%COMMAND%"=="" set "COMMAND=help"

if "%COMMAND%"=="setup" (
    call :setup
) else if "%COMMAND%"=="run" (
    call :start_servers "native"
) else if "%COMMAND%"=="docker" (
    call :start_servers "docker"
) else if "%COMMAND%"=="stop" (
    call :stop_servers
) else if "%COMMAND%"=="status" (
    call :show_status
) else (
    call :show_help
)

goto :eof

:check_requirements
echo %LOG_PREFIX% Checking requirements...

where node >nul 2>&1
if !errorlevel! neq 0 (
    echo %LOG_PREFIX% ERROR: Node.js not found. Please install Node.js
    exit /b 1
)

where python >nul 2>&1
if !errorlevel! neq 0 (
    where python3 >nul 2>&1
    if !errorlevel! neq 0 (
        echo %LOG_PREFIX% ERROR: Python not found. Please install Python 3
        exit /b 1
    )
)

where git >nul 2>&1
if !errorlevel! neq 0 (
    echo %LOG_PREFIX% ERROR: Git not found. Please install Git
    exit /b 1
)

echo %LOG_PREFIX% All requirements satisfied
exit /b 0

:setup
echo %LOG_PREFIX% Setting up MCP environment...

REM Generate credential template
node credential-manager.js generate

REM Create Python virtual environment if it doesn't exist
if not exist "mcp-python-env" (
    echo %LOG_PREFIX% Creating Python virtual environment...
    python -m venv mcp-python-env
    
    REM Activate virtual environment and install dependencies
    call mcp-python-env\Scripts\activate.bat
    pip install --upgrade pip
    
    REM Install Python MCP servers
    if exist "setup-python-servers.sh" (
        REM Convert shell script to Windows commands (basic)
        echo %LOG_PREFIX% Installing Python MCP servers...
        pip install -e servers/src/mcp-servers/src/git
        pip install -e servers/src/mcp-servers/src/time  
        pip install -e servers/src/mcp-servers/src/fetch
    )
    
    call deactivate
)

REM Install Node.js dependencies
if exist "servers\package.json" (
    echo %LOG_PREFIX% Installing Node.js dependencies...
    pushd servers
    npm install
    npm run build-all 2>nul || echo %LOG_PREFIX% WARNING: Some builds may have failed
    popd
)

echo %LOG_PREFIX% Setup complete! Please:
echo   1. Edit .env with your credentials
echo   2. Run: start-mcp.bat run
goto :eof

:start_servers
set "MODE=%~1"
echo %LOG_PREFIX% Starting MCP servers...

REM Check credentials
node credential-manager.js validate
if !errorlevel! neq 0 (
    echo %LOG_PREFIX% ERROR: Please configure credentials first
    echo   Run: node credential-manager.js generate
    exit /b 1
)

if "%MODE%"=="docker" (
    if exist "platform-configs\docker\docker-compose.yml" (
        where docker-compose >nul 2>&1
        if !errorlevel! equ 0 (
            echo %LOG_PREFIX% Starting with Docker Compose...
            docker-compose -f platform-configs\docker\docker-compose.yml up -d
        ) else (
            echo %LOG_PREFIX% ERROR: Docker Compose not found
            echo   Please install Docker Desktop for Windows
            exit /b 1
        )
    )
) else (
    set "CONFIG_FILE=platform-configs\windows\mcp-hub-config-windows.json"
    echo %LOG_PREFIX% Using config: !CONFIG_FILE!
    echo %LOG_PREFIX% MCP Hub will use configuration from: !CONFIG_FILE!
    echo %LOG_PREFIX% Configuration file path: %CD%\!CONFIG_FILE!
)
goto :eof

:stop_servers
echo %LOG_PREFIX% Stopping MCP servers...

if exist "platform-configs\docker\docker-compose.yml" (
    where docker-compose >nul 2>&1
    if !errorlevel! equ 0 (
        docker-compose -f platform-configs\docker\docker-compose.yml down
    )
)

REM Kill any running MCP processes (Windows style)
taskkill /F /IM node.exe 2>nul || echo %LOG_PREFIX% No Node.js processes found
taskkill /F /IM python.exe 2>nul || echo %LOG_PREFIX% No Python processes found

echo %LOG_PREFIX% All MCP servers stopped
goto :eof

:show_status
node credential-manager.js status
goto :eof

:show_help
echo MCP Server Manager (Windows)
echo Usage: %~n0 {setup^|run^|docker^|stop^|status}
echo.
echo Commands:
echo   setup   - Initial setup of MCP environment
echo   run     - Start MCP servers (native)
echo   docker  - Start MCP servers using Docker
echo   stop    - Stop all MCP servers  
echo   status  - Show current status
goto :eof
