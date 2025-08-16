import { Root, RootsListResult, SessionState, ClientCapabilities } from "./types.js";

/**
 * Manages the roots capability for the MCP Hub Server
 * Handles client roots detection, querying, and updates
 */
export class RootsManager {
  private sessionState: SessionState;
  private requestIdCounter = 0;
  private pendingRequests = new Map<string, { resolve: (value: any) => void; reject: (error: Error) => void }>();

  constructor() {
    this.sessionState = {
      supportsRoots: false,
      rootsListChanged: false,
      roots: []
    };
  }

  /**
   * Initialize roots capability during client connection
   */
  initializeWithCapabilities(clientCapabilities: ClientCapabilities): void {
    this.sessionState.clientCapabilities = clientCapabilities;
    
    if (clientCapabilities.roots) {
      this.sessionState.supportsRoots = true;
      this.sessionState.rootsListChanged = clientCapabilities.roots.listChanged || false;
      
      console.log(`[RootsManager] Client supports roots capability (listChanged: ${this.sessionState.rootsListChanged})`);
    } else {
      console.log("[RootsManager] Client does not support roots capability");
    }
  }

  /**
   * Check if the client supports roots
   */
  get supportsRoots(): boolean {
    return this.sessionState.supportsRoots;
  }

  /**
   * Get current roots list
   */
  get roots(): Root[] {
    return this.sessionState.roots;
  }

  /**
   * Query the client for the current roots list
   * This sends a roots/list request to the client
   */
  async queryRoots(sendRequest: (request: any) => void): Promise<Root[]> {
    if (!this.sessionState.supportsRoots) {
      console.log("[RootsManager] Client does not support roots, returning empty list");
      return [];
    }

    const requestId = this.generateRequestId();
    const request = {
      jsonrpc: "2.0",
      id: requestId,
      method: "roots/list"
    };

    console.log(`[RootsManager] Querying client for roots (request ID: ${requestId})`);
    
    return new Promise((resolve, reject) => {
      // Store the pending request
      this.pendingRequests.set(requestId, { resolve, reject });
      
      // Set timeout for the request (10 seconds)
      setTimeout(() => {
        if (this.pendingRequests.has(requestId)) {
          this.pendingRequests.delete(requestId);
          reject(new Error("Roots query timeout"));
        }
      }, 10000);

      // Send the request
      try {
        sendRequest(request);
      } catch (error) {
        this.pendingRequests.delete(requestId);
        reject(error);
      }
    });
  }

  /**
   * Handle response from client to roots/list request
   */
  handleRootsListResponse(requestId: string, result: RootsListResult): void {
    const pendingRequest = this.pendingRequests.get(requestId);
    if (!pendingRequest) {
      console.warn(`[RootsManager] Received response for unknown request ID: ${requestId}`);
      return;
    }

    this.pendingRequests.delete(requestId);
    
    // Update stored roots
    this.sessionState.roots = result.roots || [];
    
    console.log(`[RootsManager] Updated roots list: ${this.sessionState.roots.length} root(s)`);
    this.sessionState.roots.forEach((root, index) => {
      console.log(`[RootsManager]   ${index + 1}. ${root.uri}${root.name ? ` (${root.name})` : ""}`);
    });

    pendingRequest.resolve(this.sessionState.roots);
  }

  /**
   * Handle error response from client to roots/list request
   */
  handleRootsListError(requestId: string, error: any): void {
    const pendingRequest = this.pendingRequests.get(requestId);
    if (!pendingRequest) {
      console.warn(`[RootsManager] Received error for unknown request ID: ${requestId}`);
      return;
    }

    this.pendingRequests.delete(requestId);
    console.error(`[RootsManager] Error querying roots:`, error);
    pendingRequest.reject(new Error(`Roots query error: ${error.message || "Unknown error"}`));
  }

  /**
   * Handle roots/list_changed notification from client
   */
  async handleRootsListChanged(sendRequest: (request: any) => void): Promise<void> {
    console.log("[RootsManager] Received roots/list_changed notification, re-querying roots");
    
    try {
      await this.queryRoots(sendRequest);
    } catch (error) {
      console.error("[RootsManager] Failed to re-query roots after change notification:", error);
    }
  }

  /**
   * Validate if a path/URI is within the allowed roots
   */
  isPathInRoots(path: string): boolean {
    if (!this.sessionState.supportsRoots || this.sessionState.roots.length === 0) {
      // If no roots are specified, allow all operations
      return true;
    }

    // Convert path to URI format if it's a local file path
    let pathUri = path;
    if (!path.includes("://")) {
      // Assume it's a file path
      pathUri = `file://${path.startsWith("/") ? "" : "/"}${path}`;
    }

    return this.sessionState.roots.some(root => {
      // Check if the path is within this root
      if (pathUri.startsWith(root.uri)) {
        return true;
      }
      
      // For file:// URIs, also check without the protocol
      if (root.uri.startsWith("file://") && pathUri.startsWith("file://")) {
        const rootPath = root.uri.replace("file://", "");
        const checkPath = pathUri.replace("file://", "");
        return checkPath.startsWith(rootPath);
      }
      
      return false;
    });
  }

  /**
   * Get file paths from roots (filter file:// URIs and extract paths)
   */
  getFilePathsFromRoots(): string[] {
    return this.sessionState.roots
      .filter(root => root.uri.startsWith("file://"))
      .map(root => root.uri.replace("file://", ""));
  }

  /**
   * Update server configuration with roots information
   * This can be used to dynamically configure child MCP servers
   */
  updateServerConfigWithRoots(config: any): any {
    if (!this.sessionState.supportsRoots || this.sessionState.roots.length === 0) {
      return config;
    }

    const filePaths = this.getFilePathsFromRoots();
    if (filePaths.length === 0) {
      return config;
    }

    // Clone the config to avoid modifying the original
    const updatedConfig = JSON.parse(JSON.stringify(config));

    // Update filesystem-related servers with root paths
    if (updatedConfig.mcpServers) {
      for (const [serverName, serverConfig] of Object.entries(updatedConfig.mcpServers)) {
        // Look for filesystem or file-related servers and update their arguments
        if (serverName.toLowerCase().includes("filesystem") || 
            serverName.toLowerCase().includes("file")) {
          
          const config = serverConfig as any;
          if (config.args) {
            // Remove existing path arguments and add root paths
            config.args = config.args.filter((arg: string) => !arg.startsWith("/"));
            config.args.push(...filePaths);
          } else {
            config.args = filePaths;
          }
          
          console.log(`[RootsManager] Updated ${serverName} with root paths:`, filePaths);
        }
      }
    }

    return updatedConfig;
  }

  /**
   * Generate a unique request ID
   */
  private generateRequestId(): string {
    return `roots-${++this.requestIdCounter}-${Date.now()}`;
  }

  /**
   * Get session state for debugging
   */
  getSessionState(): SessionState {
    return { ...this.sessionState };
  }
}
