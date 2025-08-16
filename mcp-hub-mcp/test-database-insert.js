#!/usr/bin/env node

/**
 * Test script to verify that the database-insert server is properly integrated with the MCP Hub
 */

import { spawn } from 'child_process';
import { readFileSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Test data - a sample JSON-RPC response
const testJsonRpcResponse = JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    result: {
        user_id: 123,
        name: "Test User",
        email: "test@example.com",
        created: "2024-01-15T10:30:00Z",
        active: true
    }
});

async function testDatabaseInsertServer() {
    console.log("🧪 Testing Database Insert Server Integration with MCP Hub");
    console.log("=" * 60);

    // Start the MCP Hub server
    console.log("\n1. Starting MCP Hub server...");
    
    const hubProcess = spawn('node', ['dist/index.js'], {
        cwd: __dirname,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, MCP_CONFIG_PATH: path.join(__dirname, 'mcp-config.json') }
    });

    let hubOutput = '';
    let hubError = '';

    hubProcess.stdout.on('data', (data) => {
        hubOutput += data.toString();
        console.log(`Hub stdout: ${data.toString().trim()}`);
    });

    hubProcess.stderr.on('data', (data) => {
        hubError += data.toString();
        console.log(`Hub stderr: ${data.toString().trim()}`);
    });

    // Give the hub time to start and connect to servers
    console.log("\n2. Waiting for hub to initialize...");
    await new Promise(resolve => setTimeout(resolve, 5000));

    // Test 1: List all tools to see if database-insert tools are available
    console.log("\n3. Testing tool discovery...");
    
    const listToolsMessage = JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "tools/list",
        params: {}
    }) + '\n';

    hubProcess.stdin.write(listToolsMessage);

    // Test 2: Try to call the database-insert server's test_connection tool
    console.log("\n4. Testing database connection test...");
    
    const testConnectionMessage = JSON.stringify({
        jsonrpc: "2.0",
        id: 2,
        method: "tools/call",
        params: {
            name: "call-tool",
            arguments: {
                serverName: "database-insert",
                toolName: "test_connection",
                toolArgs: {
                    database_type: "sqlite",
                    connection_string: "sqlite:///test.db"
                }
            }
        }
    }) + '\n';

    hubProcess.stdin.write(testConnectionMessage);

    // Test 3: Try the main insert tool with our test data
    console.log("\n5. Testing JSON-RPC to database insert...");
    
    const insertMessage = JSON.stringify({
        jsonrpc: "2.0",
        id: 3,
        method: "tools/call",
        params: {
            name: "call-tool",
            arguments: {
                serverName: "database-insert",
                toolName: "insert_jsonrpc_to_db",
                toolArgs: {
                    jsonrpc_response: testJsonRpcResponse,
                    database_type: "sqlite",
                    connection_string: "sqlite:///test_integration.db",
                    table_name: "test_users",
                    add_timestamps: true
                }
            }
        }
    }) + '\n';

    hubProcess.stdin.write(insertMessage);

    // Wait for responses
    console.log("\n6. Waiting for responses...");
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Cleanup
    console.log("\n7. Cleaning up...");
    hubProcess.kill('SIGTERM');

    // Wait for process to exit
    await new Promise(resolve => {
        hubProcess.on('exit', resolve);
        setTimeout(() => {
            hubProcess.kill('SIGKILL');
            resolve();
        }, 2000);
    });

    console.log("\n✅ Test completed!");
    console.log("\n📊 Results:");
    console.log(`- Hub output length: ${hubOutput.length} chars`);
    console.log(`- Hub error length: ${hubError.length} chars`);
    
    if (hubOutput.includes('database-insert') || hubOutput.includes('insert_jsonrpc_to_db')) {
        console.log("✅ Database insert server detected in tool listings");
    } else {
        console.log("❌ Database insert server NOT detected in tool listings");
    }

    if (hubError.length > 0) {
        console.log("\n⚠️  Errors detected:");
        console.log(hubError);
    }

    console.log("\nTo manually test the hub, run:");
    console.log(`cd ${__dirname} && node dist/index.js --config-path mcp-config.json`);
}

// Run the test
testDatabaseInsertServer().catch(console.error);
