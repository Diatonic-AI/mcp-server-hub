# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

This is the **Model Context Protocol (MCP) TypeScript SDK** - the official TypeScript/JavaScript implementation of the MCP specification. It provides both client and server implementations, making it easy to build MCP servers that expose resources, prompts, and tools, as well as clients that can connect to any MCP server.

## Architecture

This is a comprehensive TypeScript SDK that implements the full MCP protocol specification. It provides high-level abstractions for building MCP applications while maintaining protocol compliance and supporting all transport mechanisms.

### Project Structure
```
/
├── src/
│   ├── client/              # MCP client implementations
│   │   ├── index.ts         # High-level client interface
│   │   ├── stdio.ts         # Stdio transport for clients
│   │   ├── streamableHttp.ts # HTTP transport for clients
│   │   ├── sse.ts           # Server-Sent Events transport (legacy)
│   │   └── websocket.ts     # WebSocket transport
│   ├── server/              # MCP server implementations
│   │   ├── index.ts         # Low-level server interface
│   │   ├── mcp.ts           # High-level server interface (McpServer)
│   │   ├── stdio.ts         # Stdio transport for servers
│   │   ├── streamableHttp.ts # HTTP transport for servers
│   │   └── sse.ts           # SSE transport for servers (legacy)
│   ├── shared/              # Shared utilities and types
│   ├── types.ts             # Core MCP protocol types
│   ├── cli.ts               # CLI tool for development/testing
│   ├── examples/            # Example implementations
│   └── integration-tests/   # Integration test suites
├── package.json             # Package configuration with dual ESM/CJS exports
├── tsconfig*.json           # Multiple TypeScript configurations
├── jest.config.js           # Jest testing configuration
└── README.md                # Comprehensive usage documentation
```

### Key Technologies
- **TypeScript**: ES2018 target with Node16 module resolution
- **Dual Package**: Supports both ESM and CommonJS exports
- **Zod**: Runtime type validation and schema generation
- **Express**: HTTP server framework for transport implementations
- **Jest**: Testing framework with comprehensive test coverage
- **Node.js**: Requires Node.js 18+ for optimal compatibility

## Development Commands

### Building
```bash
# Build both ESM and CJS distributions
npm run build

# Build only ESM (recommended for new projects)
npm run build:esm

# Build only CommonJS (for legacy compatibility)
npm run build:cjs

# Watch mode for ESM development
npm run build:esm:w

# Watch mode for CJS development  
npm run build:cjs:w
```

### Testing
```bash
# Run all tests including fetching spec types
npm test

# Run linting
npm run lint
```

### Development and Examples
```bash
# Run example server with OAuth support
npm run examples:simple-server:w

# Start development server
npm run server

# Start development client
npm run client
```

### Package Management
```bash
# Prepare package for publishing (builds both distributions)
npm run prepack

# Fetch latest MCP specification types
npm run fetch:spec-types
```

## Core Architecture Concepts

### High-Level vs Low-Level APIs

The SDK provides two levels of abstraction:

#### High-Level API (Recommended)
- **`McpServer`** - Declarative server with resource/tool/prompt registration
- **`Client`** - Simple client interface with method-based interactions
- Automatic protocol compliance and error handling
- Built-in schema validation with Zod

#### Low-Level API (Advanced Use Cases)
- **`Server`** - Direct protocol message handling
- **`Transport`** classes for custom transport implementations
- Manual request/response handling
- Full control over MCP protocol messages

### Transport Architecture

The SDK supports multiple transport mechanisms:

#### Stdio Transport
- Process-based communication via stdin/stdout
- Ideal for command-line tools and local integrations
- Automatic process lifecycle management

#### Streamable HTTP Transport
- Modern HTTP-based transport with bidirectional communication
- Supports session management and server-to-client notifications
- DNS rebinding protection for security
- CORS support for browser clients

#### Legacy Transports
- **SSE (Server-Sent Events)** - Deprecated, maintained for backwards compatibility
- **WebSocket** - Bidirectional real-time communication

### Core MCP Concepts Implementation

#### Resources
- Static and dynamic data exposure
- Template-based URIs with parameter extraction
- Context-aware completion support
- MIME type and metadata handling

#### Tools
- Function execution with side effects
- Zod-based input schema validation
- ResourceLink support for performance optimization
- Comprehensive error handling

#### Prompts
- Reusable LLM interaction templates
- Parameter validation and completion
- Message generation with role-based content

#### Sampling
- LLM completion requests from servers to clients
- Integration with client-side language models
- Structured response handling

## Development Patterns

### High-Level Server Development
```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({
  name: "example-server",
  version: "1.0.0"
});

// Register tools with automatic schema validation
server.registerTool("calculator", {
  title: "Calculator",
  description: "Basic arithmetic operations",
  inputSchema: { a: z.number(), b: z.number() }
}, async ({ a, b }) => ({
  content: [{ type: "text", text: String(a + b) }]
}));
```

### Client Development
```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const client = new Client({
  name: "example-client",
  version: "1.0.0"
});

const transport = new StdioClientTransport({
  command: "node",
  args: ["server.js"]
});

await client.connect(transport);
const result = await client.callTool({
  name: "calculator",
  arguments: { a: 5, b: 3 }
});
```

### Schema Validation
Extensive use of Zod for runtime type safety:

```typescript
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";

const schema = z.object({
  name: z.string(),
  age: z.number().optional()
});

// Automatic JSON schema generation for MCP protocol
const jsonSchema = zodToJsonSchema(schema);
```

## Testing Infrastructure

### Test Categories
- **Unit Tests** - Individual component testing
- **Integration Tests** - Full protocol workflow testing
- **Transport Tests** - Transport-specific functionality
- **Example Tests** - Validation of example implementations

### Test Patterns
- Mocking of external dependencies
- Async operation testing
- Error condition validation
- Protocol compliance verification

## Build System

### Dual Package Support
The SDK is built to support both ESM and CommonJS:

```json
{
  "exports": {
    ".": {
      "import": "./dist/esm/index.js",
      "require": "./dist/cjs/index.js"
    }
  }
}
```

### TypeScript Configuration
Multiple TypeScript configurations for different build targets:
- `tsconfig.json` - Development configuration
- `tsconfig.prod.json` - Production ESM build
- `tsconfig.cjs.json` - CommonJS build

## Security Considerations

### DNS Rebinding Protection
Built-in protection for HTTP transports:
```typescript
const transport = new StreamableHTTPServerTransport({
  enableDnsRebindingProtection: true,
  allowedHosts: ['127.0.0.1'],
  allowedOrigins: ['https://trusted-domain.com']
});
```

### CORS Configuration
Proper CORS setup for browser compatibility:
```typescript
app.use(cors({
  exposedHeaders: ['Mcp-Session-Id'],
  allowedHeaders: ['Content-Type', 'mcp-session-id']
}));
```

## Backwards Compatibility

The SDK maintains backwards compatibility with older MCP protocol versions:
- Automatic fallback between transport types
- Legacy SSE transport support
- Protocol version negotiation
- Graceful degradation for unsupported features

## Performance Optimizations

- **ResourceLinks** - Avoid embedding large content in responses
- **Notification Debouncing** - Coalesce rapid notification updates
- **Session Management** - Efficient connection reuse
- **Lazy Loading** - Dynamic resource and tool registration

## CLI Development Tools

The SDK includes development utilities:
```bash
# Interactive server testing
tsx src/cli.ts server

# Interactive client testing  
tsx src/cli.ts client
```
