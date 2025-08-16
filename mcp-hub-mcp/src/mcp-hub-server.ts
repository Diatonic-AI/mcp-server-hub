import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { RootsManager } from "./roots-manager.js";
import { ClientCapabilities } from "./types.js";

/**
 * Custom MCP Hub Server that extends the standard MCP server to support roots capability
 */
export class McpHubServer extends McpServer {
  private rootsManager: RootsManager;
  private transport: any;
  private initialized = false;

  constructor(info: { name: string; version: string; description?: string }, rootsManager: RootsManager) {
    super(info);
    this.rootsManager = rootsManager;
  }

  /**
   * Override the connect method to intercept initialization
   */
  async connect(transport: any): Promise<void> {
    this.transport = transport;
    
    // Set up message handlers for roots functionality
    this.setupRootsMessageHandlers();
    
    // Call the parent connect method
    await super.connect(transport);
  }

  /**
   * Set up message handlers for roots functionality
   */
  private setupRootsMessageHandlers(): void {
    if (!this.transport) {
      return;
    }

    // Store the original message handler
    const originalOnMessage = this.transport.onmessage;
    
    // Override the message handler to intercept initialize and other messages
    this.transport.onmessage = (message: any) => {
      try {
        const parsed = JSON.parse(message);
        
        // Handle initialize method to detect roots capability
        if (parsed.method === "initialize" && !this.initialized) {
          this.handleInitialize(parsed);
          this.initialized = true;
        }
        
        // Handle roots-related responses and notifications
        if (parsed.id && typeof parsed.id === "string" && parsed.id.startsWith("roots-")) {
          this.handleRootsResponse(parsed);
          return; // Don't pass to original handler
        }
        
        // Handle roots/list_changed notification
        if (parsed.method === "notifications/roots/list_changed") {
          this.handleRootsListChanged();
          return; // Don't pass to original handler
        }
        
      } catch (error) {
        console.error("[McpHubServer] Error parsing message:", error);
      }
      
      // Pass to original handler
      if (originalOnMessage) {
        originalOnMessage.call(this.transport, message);
      }
    };
  }

  /**
   * Handle the initialize method to detect client capabilities
   */
  private handleInitialize(message: any): void {
    if (message.params && message.params.capabilities) {
      const clientCapabilities: ClientCapabilities = message.params.capabilities;
      
      console.log("[McpHubServer] Initializing with client capabilities:", JSON.stringify(clientCapabilities, null, 2));
      
      // Initialize roots manager with client capabilities
      this.rootsManager.initializeWithCapabilities(clientCapabilities);
      
      // If client supports roots, query for the initial roots list
      if (this.rootsManager.supportsRoots) {
        // Delay the roots query slightly to allow initialization to complete
        setTimeout(() => {
          this.queryClientRoots();
        }, 100);
      }
    }
  }

  /**
   * Query the client for roots
   */
  private async queryClientRoots(): Promise<void> {
    if (!this.transport || !this.rootsManager.supportsRoots) {
      return;
    }

    try {
      await this.rootsManager.queryRoots((request: any) => {
        if (this.transport && this.transport.send) {
          this.transport.send(JSON.stringify(request));
        }
      });
      
      console.log(`[McpHubServer] Successfully queried client roots: ${this.rootsManager.roots.length} root(s)`);
    } catch (error) {
      console.error("[McpHubServer] Failed to query client roots:", error);
    }
  }

  /**
   * Handle roots-related responses from the client
   */
  private handleRootsResponse(message: any): void {
    const requestId = message.id;
    
    if (message.result) {
      this.rootsManager.handleRootsListResponse(requestId, message.result);
    } else if (message.error) {
      this.rootsManager.handleRootsListError(requestId, message.error);
    }
  }

  /**
   * Handle roots/list_changed notification
   */
  private async handleRootsListChanged(): Promise<void> {
    if (!this.transport) {
      return;
    }

    await this.rootsManager.handleRootsListChanged((request: any) => {
      if (this.transport && this.transport.send) {
        this.transport.send(JSON.stringify(request));
      }
    });
  }

  /**
   * Get the roots manager instance
   */
  getRootsManager(): RootsManager {
    return this.rootsManager;
  }

  /**
   * Check if a path is within the allowed roots
   */
  isPathAllowed(path: string): boolean {
    return this.rootsManager.isPathInRoots(path);
  }
}
