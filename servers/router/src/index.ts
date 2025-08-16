import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import winston from 'winston';
import { spawn } from 'child_process';
import { EventEmitter } from 'events';
import Docker from 'dockerode';

interface MCPServer {
  name: string;
  command: string;
  args: string[];
  env?: Record<string, string>;
  status: 'running' | 'stopped' | 'error';
  process?: any;
  lastActivity: Date;
}

class MCPRouter {
  private servers: Map<string, MCPServer> = new Map();
  private docker: Docker;
  private logger!: winston.Logger;
  private app!: express.Application;

  constructor() {
    this.docker = new Docker();
    this.setupLogger();
    this.setupExpress();
    this.loadServerConfig();
  }

  private setupLogger(): void {
    this.logger = winston.createLogger({
      level: 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
      ),
      defaultMeta: { service: 'mcp-router' },
      transports: [
        new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
        new winston.transports.File({ filename: 'logs/combined.log' }),
        new winston.transports.Console({
          format: winston.format.simple()
        })
      ]
    });
  }

  private setupExpress(): void {
    this.app = express();
    this.app.use(helmet());
    this.app.use(cors());
    this.app.use(express.json());

    // Health check endpoint
    this.app.get('/health', (req, res) => {
      res.json({ status: 'healthy', servers: Array.from(this.servers.keys()) });
    });

    // List all servers
    this.app.get('/servers', (req, res) => {
      const serverList = Array.from(this.servers.values()).map(server => ({
        name: server.name,
        status: server.status,
        lastActivity: server.lastActivity
      }));
      res.json(serverList);
    });

    // Start a server
    this.app.post('/servers/:name/start', async (req, res) => {
      const { name } = req.params;
      try {
        await this.startServer(name);
        res.json({ success: true, message: `Server ${name} started` });
      } catch (error) {
        this.logger.error(`Failed to start server ${name}:`, error);
        res.status(500).json({ success: false, error: (error as Error).message });
      }
    });

    // Stop a server
    this.app.post('/servers/:name/stop', async (req, res) => {
      const { name } = req.params;
      try {
        await this.stopServer(name);
        res.json({ success: true, message: `Server ${name} stopped` });
      } catch (error) {
        this.logger.error(`Failed to stop server ${name}:`, error);
        res.status(500).json({ success: false, error: (error as Error).message });
      }
    });

    // MCP stdio endpoint
    this.app.post('/mcp/:server', async (req, res) => {
      const { server } = req.params;
      const { method, params } = req.body;

      try {
        const result = await this.forwardToServer(server, method, params);
        res.json(result);
      } catch (error) {
        this.logger.error(`MCP request failed for ${server}:`, error);
        res.status(500).json({ error: (error as Error).message });
      }
    });
  }

  private loadServerConfig(): void {
    // Default server configurations
    const defaultServers: MCPServer[] = [
      {
        name: 'filesystem',
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-filesystem', '/data'],
        status: 'stopped',
        lastActivity: new Date()
      },
      {
        name: 'memory',
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-memory'],
        status: 'stopped',
        lastActivity: new Date()
      },
      {
        name: 'git',
        command: 'uvx',
        args: ['mcp-server-git', '--repository', '/repos'],
        status: 'stopped',
        lastActivity: new Date()
      },
      {
        name: 'fetch',
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-fetch'],
        status: 'stopped',
        lastActivity: new Date()
      },
      {
        name: 'time',
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-time'],
        status: 'stopped',
        lastActivity: new Date()
      }
    ];

    defaultServers.forEach(server => {
      this.servers.set(server.name, server);
    });
  }

  private async startServer(name: string): Promise<void> {
    const server = this.servers.get(name);
    if (!server) {
      throw new Error(`Server ${name} not found`);
    }

    if (server.status === 'running') {
      this.logger.info(`Server ${name} is already running`);
      return;
    }

    try {
      // Start the server process
      const serverProcess = spawn(server.command, server.args, {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, ...server.env }
      });

      server.process = serverProcess;
      server.status = 'running';
      server.lastActivity = new Date();

      serverProcess.on('error', (error: Error) => {
        this.logger.error(`Server ${name} process error:`, error);
        server.status = 'error';
      });

      serverProcess.on('exit', (code: number | null) => {
        this.logger.info(`Server ${name} exited with code ${code}`);
        server.status = 'stopped';
        server.process = undefined;
      });

      this.logger.info(`Server ${name} started successfully`);
    } catch (error) {
      server.status = 'error';
      throw error;
    }
  }

  private async stopServer(name: string): Promise<void> {
    const server = this.servers.get(name);
    if (!server) {
      throw new Error(`Server ${name} not found`);
    }

    if (server.status !== 'running' || !server.process) {
      this.logger.info(`Server ${name} is not running`);
      return;
    }

    try {
      server.process.kill('SIGTERM');
      server.status = 'stopped';
      server.process = undefined;
      this.logger.info(`Server ${name} stopped successfully`);
    } catch (error) {
      throw error;
    }
  }

  private async forwardToServer(name: string, method: string, params: any): Promise<any> {
    const server = this.servers.get(name);
    if (!server) {
      throw new Error(`Server ${name} not found`);
    }

    if (server.status !== 'running' || !server.process) {
      throw new Error(`Server ${name} is not running`);
    }

    // Create MCP request
    const request = {
      jsonrpc: '2.0',
      id: Date.now(),
      method,
      params
    };

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error(`Request to ${name} timed out`));
      }, 30000);

      // Send request to server via stdio
      server.process!.stdin.write(JSON.stringify(request) + '\n');

      // Handle response
      const handleResponse = (data: Buffer) => {
        try {
          const response = JSON.parse(data.toString());
          clearTimeout(timeout);
          server.lastActivity = new Date();
          resolve(response);
        } catch (error) {
          clearTimeout(timeout);
          reject(error);
        }
      };

      server.process!.stdout.once('data', handleResponse);
      server.process!.stderr.once('data', (data: Buffer) => {
        this.logger.error(`Server ${name} stderr:`, data.toString());
      });
    });
  }

  public async start(): Promise<void> {
    const port = process.env.PORT || 8080;
    
    this.app.listen(port, () => {
      this.logger.info(`MCP Router started on port ${port}`);
    });

    // Start all servers by default
    for (const [name] of this.servers) {
      try {
        await this.startServer(name);
      } catch (error) {
        this.logger.error(`Failed to start server ${name}:`, error);
      }
    }
  }
}

// Start the router
const router = new MCPRouter();
router.start().catch(console.error); 