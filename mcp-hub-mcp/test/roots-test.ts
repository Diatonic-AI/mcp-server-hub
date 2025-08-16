import { RootsManager } from '../src/roots-manager.js';
import { McpHubServer } from '../src/mcp-hub-server.js';
import { McpServerManager } from '../src/server-manager.js';
import { ClientCapabilities, Root } from '../src/types.js';

/**
 * Comprehensive test suite for roots functionality
 */
class RootsTest {
  private rootsManager: RootsManager;
  private testResults: { test: string; passed: boolean; message: string }[] = [];

  constructor() {
    this.rootsManager = new RootsManager();
  }

  /**
   * Run all tests
   */
  async runAllTests(): Promise<void> {
    console.log('🧪 Starting Roots Functionality Tests\n');

    await this.testRootsManagerInitialization();
    await this.testClientCapabilitiesDetection();
    await this.testPathValidation();
    await this.testFilePathExtraction();
    await this.testServerConfigUpdate();
    await this.testRootsQueryMock();

    this.printResults();
  }

  /**
   * Test roots manager initialization
   */
  private async testRootsManagerInitialization(): Promise<void> {
    try {
      const initialState = this.rootsManager.getSessionState();
      
      this.assert(
        'Roots Manager Initial State',
        !initialState.supportsRoots && 
        !initialState.rootsListChanged && 
        initialState.roots.length === 0,
        `Expected initial state to be empty, got: ${JSON.stringify(initialState)}`
      );
    } catch (error) {
      this.assert('Roots Manager Initial State', false, `Error: ${error.message}`);
    }
  }

  /**
   * Test client capabilities detection
   */
  private async testClientCapabilitiesDetection(): Promise<void> {
    try {
      // Test with roots support
      const capabilitiesWithRoots: ClientCapabilities = {
        roots: {
          listChanged: true
        }
      };

      this.rootsManager.initializeWithCapabilities(capabilitiesWithRoots);
      const stateWithRoots = this.rootsManager.getSessionState();

      this.assert(
        'Client Capabilities Detection (with roots)',
        stateWithRoots.supportsRoots && stateWithRoots.rootsListChanged,
        `Expected roots support enabled, got: ${JSON.stringify(stateWithRoots)}`
      );

      // Test without roots support
      const newRootsManager = new RootsManager();
      const capabilitiesWithoutRoots: ClientCapabilities = {
        tools: { listChanged: true }
      };

      newRootsManager.initializeWithCapabilities(capabilitiesWithoutRoots);
      const stateWithoutRoots = newRootsManager.getSessionState();

      this.assert(
        'Client Capabilities Detection (without roots)',
        !stateWithoutRoots.supportsRoots,
        `Expected no roots support, got: ${JSON.stringify(stateWithoutRoots)}`
      );
    } catch (error) {
      this.assert('Client Capabilities Detection', false, `Error: ${error.message}`);
    }
  }

  /**
   * Test path validation
   */
  private async testPathValidation(): Promise<void> {
    try {
      // Set up mock roots
      const mockRoots: Root[] = [
        { uri: 'file:///home/user/project', name: 'Project Root' },
        { uri: 'file:///home/user/documents', name: 'Documents' }
      ];

      // Manually set roots for testing
      (this.rootsManager as any).sessionState.supportsRoots = true;
      (this.rootsManager as any).sessionState.roots = mockRoots;

      // Test valid paths
      const validPaths = [
        '/home/user/project/src/main.ts',
        'file:///home/user/project/config.json',
        '/home/user/documents/readme.txt'
      ];

      const invalidPaths = [
        '/home/user/other/file.txt',
        'file:///tmp/temp.txt',
        '/etc/passwd'
      ];

      for (const path of validPaths) {
        this.assert(
          `Path Validation (valid): ${path}`,
          this.rootsManager.isPathInRoots(path),
          `Expected path ${path} to be valid within roots`
        );
      }

      for (const path of invalidPaths) {
        this.assert(
          `Path Validation (invalid): ${path}`,
          !this.rootsManager.isPathInRoots(path),
          `Expected path ${path} to be invalid outside roots`
        );
      }

      // Test without roots support (should allow all)
      const noRootsManager = new RootsManager();
      this.assert(
        'Path Validation (no roots support)',
        noRootsManager.isPathInRoots('/any/path'),
        'Expected all paths to be allowed when roots not supported'
      );

    } catch (error) {
      this.assert('Path Validation', false, `Error: ${error.message}`);
    }
  }

  /**
   * Test file path extraction from roots
   */
  private async testFilePathExtraction(): Promise<void> {
    try {
      const mockRoots: Root[] = [
        { uri: 'file:///home/user/project', name: 'Project' },
        { uri: 'https://example.com/api', name: 'API' },
        { uri: 'file:///home/user/docs', name: 'Docs' }
      ];

      (this.rootsManager as any).sessionState.roots = mockRoots;

      const filePaths = this.rootsManager.getFilePathsFromRoots();
      const expectedPaths = ['/home/user/project', '/home/user/docs'];

      this.assert(
        'File Path Extraction',
        JSON.stringify(filePaths.sort()) === JSON.stringify(expectedPaths.sort()),
        `Expected ${JSON.stringify(expectedPaths)}, got ${JSON.stringify(filePaths)}`
      );

    } catch (error) {
      this.assert('File Path Extraction', false, `Error: ${error.message}`);
    }
  }

  /**
   * Test server configuration update with roots
   */
  private async testServerConfigUpdate(): Promise<void> {
    try {
      const mockRoots: Root[] = [
        { uri: 'file:///home/user/project', name: 'Project' },
        { uri: 'file:///home/user/documents', name: 'Docs' }
      ];

      (this.rootsManager as any).sessionState.supportsRoots = true;
      (this.rootsManager as any).sessionState.roots = mockRoots;

      const originalConfig = {
        mcpServers: {
          filesystem: {
            command: 'filesystem-server',
            args: ['--some-arg']
          },
          other: {
            command: 'other-server',
            args: []
          }
        }
      };

      const updatedConfig = this.rootsManager.updateServerConfigWithRoots(originalConfig);

      this.assert(
        'Server Config Update',
        updatedConfig.mcpServers.filesystem.args.includes('/home/user/project') &&
        updatedConfig.mcpServers.filesystem.args.includes('/home/user/documents'),
        `Expected filesystem server args to include root paths, got: ${JSON.stringify(updatedConfig.mcpServers.filesystem.args)}`
      );

      this.assert(
        'Server Config Update (other servers unchanged)',
        updatedConfig.mcpServers.other.args.length === 0,
        `Expected other servers to remain unchanged, got: ${JSON.stringify(updatedConfig.mcpServers.other.args)}`
      );

    } catch (error) {
      this.assert('Server Config Update', false, `Error: ${error.message}`);
    }
  }

  /**
   * Test roots query functionality (mock)
   */
  private async testRootsQueryMock(): Promise<void> {
    try {
      let sentRequest: any = null;
      const mockSendRequest = (request: any) => {
        sentRequest = request;
      };

      (this.rootsManager as any).sessionState.supportsRoots = true;

      // Start the query (it will timeout, but we can check the request)
      const queryPromise = this.rootsManager.queryRoots(mockSendRequest);

      // Wait a bit for the request to be sent
      await new Promise(resolve => setTimeout(resolve, 10));

      this.assert(
        'Roots Query Request Format',
        sentRequest && 
        sentRequest.method === 'roots/list' &&
        sentRequest.jsonrpc === '2.0' &&
        typeof sentRequest.id === 'string',
        `Expected valid roots/list request, got: ${JSON.stringify(sentRequest)}`
      );

      // Clean up the pending promise (it will timeout)
      queryPromise.catch(() => {});

    } catch (error) {
      this.assert('Roots Query Mock', false, `Error: ${error.message}`);
    }
  }

  /**
   * Assert helper
   */
  private assert(testName: string, condition: boolean, message: string): void {
    this.testResults.push({
      test: testName,
      passed: condition,
      message: condition ? 'PASSED' : message
    });

    const emoji = condition ? '✅' : '❌';
    const status = condition ? 'PASSED' : 'FAILED';
    console.log(`${emoji} ${testName}: ${status}`);
    if (!condition) {
      console.log(`   └─ ${message}\n`);
    }
  }

  /**
   * Print test results summary
   */
  private printResults(): void {
    const passed = this.testResults.filter(r => r.passed).length;
    const total = this.testResults.length;
    const failed = total - passed;

    console.log('\n📊 Test Results Summary');
    console.log('═'.repeat(50));
    console.log(`Total Tests: ${total}`);
    console.log(`Passed: ${passed} ✅`);
    console.log(`Failed: ${failed} ❌`);
    console.log(`Success Rate: ${((passed / total) * 100).toFixed(1)}%`);

    if (failed > 0) {
      console.log('\n🔍 Failed Tests:');
      this.testResults
        .filter(r => !r.passed)
        .forEach(r => {
          console.log(`   • ${r.test}: ${r.message}`);
        });
    }

    console.log('\n🎯 Roots functionality tests completed!');
  }
}

/**
 * Integration test for the complete roots flow
 */
async function testCompleteRootsFlow(): Promise<void> {
  console.log('\n🔄 Testing Complete Roots Integration Flow\n');

  try {
    const rootsManager = new RootsManager();
    const serverManager = new McpServerManager({
      configPath: './test-roots-config.json',
      rootsManager: rootsManager
    });

    const server = new McpHubServer({
      name: 'Test-MCP-Hub-Server',
      version: '1.0.0-test',
      description: 'Test server for roots functionality'
    }, rootsManager);

    console.log('✅ Server components initialized successfully');

    // Test roots manager methods
    const sessionState = rootsManager.getSessionState();
    console.log('📋 Initial session state:', JSON.stringify(sessionState, null, 2));

    // Test path validation with no roots (should allow all)
    const testPath = '/home/user/test.txt';
    const isAllowed = rootsManager.isPathInRoots(testPath);
    console.log(`🔍 Path validation (no roots): ${testPath} → ${isAllowed ? 'ALLOWED' : 'DENIED'}`);

    console.log('✅ Complete roots integration test passed!');

  } catch (error) {
    console.error('❌ Complete roots integration test failed:', error);
  }
}

// Run tests
async function main() {
  const tester = new RootsTest();
  await tester.runAllTests();
  await testCompleteRootsFlow();
}

main().catch(console.error);
