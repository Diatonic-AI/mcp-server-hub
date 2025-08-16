#!/usr/bin/env python3
"""
MCP Resource Manager
Handles on-demand startup/shutdown of MCP server containers for optimal resource usage.
"""

import os
import time
import json
import logging
import requests
import schedule
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import docker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/resource-manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MCPResourceManager:
    def __init__(self):
        self.prod_root = os.getenv('PROD_ROOT', '/mnt/environments/prod/mcp-system')
        self.auto_shutdown_timeout = int(os.getenv('AUTO_SHUTDOWN_TIMEOUT', 300))  # 5 minutes
        self.health_check_interval = int(os.getenv('HEALTH_CHECK_INTERVAL', 30))
        self.router_url = "http://localhost:8080"
        
        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.docker_client = None
        
        # MCP server containers (on-demand)
        self.mcp_servers = [
            'mcp-filesystem-prod',
            'mcp-memory-prod', 
            'mcp-fetch-prod',
            'mcp-everything-prod',
            'mcp-sequentialthinking-prod',
            'mcp-time-prod',
            'mcp-git-prod'
        ]
        
        # Always running containers
        self.always_running = [
            'mcp-router-prod',
            'mcp-monitor-prod',
            'mcp-resource-manager-prod'
        ]
        
        # Track container activity
        self.container_activity = {}
        self.last_requests = {}

    def get_container_status(self, container_name: str) -> Optional[str]:
        """Get the status of a container."""
        try:
            if self.docker_client:
                container = self.docker_client.containers.get(container_name)
                return container.status
            else:
                # Fallback to podman command
                result = subprocess.run(
                    ['podman', 'ps', '--filter', f'name={container_name}', '--format', '{{.Status}}'],
                    capture_output=True, text=True
                )
                return result.stdout.strip() if result.stdout.strip() else None
        except Exception as e:
            logger.error(f"Error getting status for {container_name}: {e}")
            return None

    def start_container(self, container_name: str) -> bool:
        """Start a container."""
        try:
            if self.docker_client:
                container = self.docker_client.containers.get(container_name)
                container.start()
            else:
                subprocess.run(['podman', 'start', container_name], check=True)
            
            logger.info(f"Started container: {container_name}")
            self.container_activity[container_name] = datetime.now()
            return True
        except Exception as e:
            logger.error(f"Failed to start container {container_name}: {e}")
            return False

    def stop_container(self, container_name: str) -> bool:
        """Stop a container."""
        try:
            if self.docker_client:
                container = self.docker_client.containers.get(container_name)
                container.stop(timeout=30)
            else:
                subprocess.run(['podman', 'stop', container_name], check=True)
            
            logger.info(f"Stopped container: {container_name}")
            if container_name in self.container_activity:
                del self.container_activity[container_name]
            return True
        except Exception as e:
            logger.error(f"Failed to stop container {container_name}: {e}")
            return False

    def check_router_health(self) -> bool:
        """Check if the MCP router is healthy."""
        try:
            response = requests.get(f"{self.router_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Router health check failed: {e}")
            return False

    def get_server_requests(self) -> Dict[str, datetime]:
        """Get recent requests for each server from the router."""
        try:
            response = requests.get(f"{self.router_url}/servers", timeout=5)
            if response.status_code == 200:
                servers = response.json()
                requests_data = {}
                for server in servers:
                    if 'lastActivity' in server:
                        try:
                            last_activity = datetime.fromisoformat(server['lastActivity'].replace('Z', '+00:00'))
                            requests_data[server['name']] = last_activity
                        except:
                            pass
                return requests_data
        except Exception as e:
            logger.error(f"Failed to get server requests: {e}")
        return {}

    def should_stop_container(self, container_name: str) -> bool:
        """Determine if a container should be stopped based on inactivity."""
        if container_name not in self.container_activity:
            return False
        
        last_activity = self.container_activity[container_name]
        time_since_activity = datetime.now() - last_activity
        
        # Check if container has been inactive for the timeout period
        if time_since_activity.total_seconds() > self.auto_shutdown_timeout:
            logger.info(f"Container {container_name} inactive for {time_since_activity.total_seconds():.0f}s, stopping")
            return True
        
        return False

    def update_container_activity(self, container_name: str):
        """Update the activity timestamp for a container."""
        self.container_activity[container_name] = datetime.now()
        logger.debug(f"Updated activity for {container_name}")

    def manage_containers(self):
        """Main container management logic."""
        logger.info("Running container management check...")
        
        # Check router health
        if not self.check_router_health():
            logger.warning("Router is not healthy, skipping container management")
            return
        
        # Get recent server requests
        server_requests = self.get_server_requests()
        
        # Check each MCP server container
        for container_name in self.mcp_servers:
            status = self.get_container_status(container_name)
            
            if status == 'running':
                # Check if there's been recent activity
                server_name = container_name.replace('-prod', '')
                if server_name in server_requests:
                    last_request = server_requests[server_name]
                    self.container_activity[container_name] = last_request
                
                # Check if container should be stopped
                if self.should_stop_container(container_name):
                    self.stop_container(container_name)
            
            elif status is None:
                # Container doesn't exist, that's okay for on-demand containers
                logger.debug(f"Container {container_name} doesn't exist (on-demand)")
        
        # Ensure always-running containers are up
        for container_name in self.always_running:
            status = self.get_container_status(container_name)
            if status != 'running':
                logger.warning(f"Always-running container {container_name} is not running, starting...")
                self.start_container(container_name)

    def start_server_on_demand(self, server_name: str) -> bool:
        """Start a specific server on demand."""
        container_name = f"mcp-{server_name}-prod"
        
        if container_name not in self.mcp_servers:
            logger.error(f"Unknown server: {server_name}")
            return False
        
        status = self.get_container_status(container_name)
        if status == 'running':
            logger.info(f"Server {server_name} is already running")
            self.update_container_activity(container_name)
            return True
        
        logger.info(f"Starting server {server_name} on demand...")
        if self.start_container(container_name):
            self.update_container_activity(container_name)
            return True
        
        return False

    def get_resource_usage(self) -> Dict:
        """Get current resource usage statistics."""
        try:
            if self.docker_client:
                containers = self.docker_client.containers.list()
                stats = {
                    'running_containers': len(containers),
                    'mcp_servers_running': 0,
                    'total_memory_mb': 0,
                    'total_cpu_percent': 0
                }
                
                for container in containers:
                    if container.name in self.mcp_servers:
                        stats['mcp_servers_running'] += 1
                    
                    # Get container stats
                    try:
                        container_stats = container.stats(stream=False)
                        memory_usage = container_stats['memory_stats']['usage'] / 1024 / 1024  # MB
                        stats['total_memory_mb'] += memory_usage
                    except:
                        pass
                
                return stats
        except Exception as e:
            logger.error(f"Error getting resource usage: {e}")
        
        return {}

    def run(self):
        """Main run loop."""
        logger.info("MCP Resource Manager started")
        logger.info(f"Production root: {self.prod_root}")
        logger.info(f"Auto shutdown timeout: {self.auto_shutdown_timeout}s")
        
        # Schedule regular management checks
        schedule.every(self.health_check_interval).seconds.do(self.manage_containers)
        
        # Initial management check
        self.manage_containers()
        
        # Main loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Shutting down resource manager...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(5)

if __name__ == "__main__":
    manager = MCPResourceManager()
    manager.run() 