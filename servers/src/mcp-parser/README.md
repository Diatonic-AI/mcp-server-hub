# MCP Database Insert Server

A Model Context Protocol server that provides specialized tools for parsing JSON-RPC responses and transforming/inserting data into databases. This server enables LLMs to efficiently process JSON-RPC data and store it in various database systems with automatic schema management and type conversion.

## Features

### 🚀 Core Functionality
- **JSON-RPC Parsing**: Comprehensive parsing and validation of JSON-RPC 2.0 responses, errors, and notifications
- **Multi-Database Support**: PostgreSQL, MongoDB, SQLite, Redis, and MySQL
- **Chained Operations**: Single atomic operation that handles parsing → transformation → schema management → insertion
- **Automatic Schema Management**: Infer database schemas from data and create tables/collections automatically
- **Batch Processing**: Efficient bulk operations with configurable batch sizes
- **Type Conversion**: Smart type inference and database-specific data transformation

### 🛠 Available Tools

#### 1. `insert_jsonrpc_to_db`
The primary tool that provides a complete pipeline for processing JSON-RPC responses:

1. **Parse & Validate**: JSON-RPC format validation (supports single responses and batches)
2. **Extract Data**: Extract structured records from response/error/notification content  
3. **Transform**: Type conversion, flattening, UUID generation, timestamp addition
4. **Schema Management**: Create tables/collections if they don't exist
5. **Insert**: Batch insert records for optimal performance

**Parameters:**
- `jsonrpc_response` (string, required): Raw JSON-RPC response string
- `database_type` (string, required): `postgresql`, `mongodb`, `sqlite`, `redis`, or `mysql`
- `connection_string` (string, required): Database connection URI
- `schema_name` (string, optional): Target schema name
- `table_name` (string, optional): Target table/collection name (defaults to `jsonrpc_data`)
- `uuid_fields` (array, optional): Field names that should receive generated UUIDs
- `create_if_missing` (boolean, optional): Auto-create tables/collections (default: `true`)
- `batch_size` (integer, optional): Batch size for bulk operations (default: `100`)
- `flatten_nested` (boolean, optional): Flatten nested JSON structures (default: `true`)
- `add_timestamps` (boolean, optional): Add created_at/updated_at fields (default: `true`)

#### 2. `query_schema`
Query database schema information for inspection.

**Parameters:**
- `database_type` (string, required): Database type
- `connection_string` (string, required): Database connection URI
- `table_name` (string, required): Table/collection to inspect

#### 3. `test_connection`
Test database connectivity and validate connection strings.

**Parameters:**
- `database_type` (string, required): Database type
- `connection_string` (string, required): Database connection URI

### 🗄 Supported Databases

| Database | Connection String Format | Notes |
|----------|-------------------------|-------|
| **PostgreSQL** | `postgresql://user:pass@host:port/dbname` | Uses asyncpg for optimal performance |
| **MySQL** | `mysql://user:pass@host:port/dbname` | Uses aiomysql with connection pooling |
| **SQLite** | `sqlite:///path/to/database.db` | Uses aiosqlite for async operations |
| **MongoDB** | `mongodb://user:pass@host:port/database` | Uses motor (async MongoDB driver) |
| **Redis** | `redis://[user:pass@]host:port/db` | Uses redis-py with async support |

## Installation

### Using uv (recommended)

```bash
uv add mcp-server-db-insert
```

### Using pip

```bash
pip install mcp-server-db-insert
```

### From Source

```bash
git clone <repository-url>
cd mcp-server-db-insert
pip install -e .
```

## Configuration

### Configure for Claude Desktop

Add to your Claude settings:

```json
{
  "mcpServers": {
    "database-insert": {
      "command": "uvx",
      "args": ["mcp-server-db-insert"]
    }
  }
}
```

### Configure for VS Code

Add to your VS Code MCP settings:

```json
{
  "mcp": {
    "servers": {
      "database-insert": {
        "command": "uvx",
        "args": ["mcp-server-db-insert"]
      }
    }
  }
}
```

### Advanced Configuration

You can customize the server behavior with command-line arguments:

```json
{
  "mcpServers": {
    "database-insert": {
      "command": "uvx",
      "args": [
        "mcp-server-db-insert",
        "--max-batch-size", "1000",
        "--connection-timeout", "30",
        "--enable-debug"
      ]
    }
  }
}
```

**Available Arguments:**
- `--max-batch-size`: Maximum batch size for bulk operations (default: 1000)
- `--connection-timeout`: Database connection timeout in seconds (default: 30)
- `--enable-debug`: Enable detailed debug logging

## Usage Examples

### Basic JSON-RPC Response Processing

```json
{
  "tool": "insert_jsonrpc_to_db",
  "arguments": {
    "jsonrpc_response": "{\"jsonrpc\":\"2.0\",\"id\":1,\"result\":{\"user_id\":123,\"name\":\"John Doe\",\"email\":\"john@example.com\"}}",
    "database_type": "postgresql",
    "connection_string": "postgresql://user:password@localhost:5432/mydb",
    "table_name": "users"
  }
}
```

### Batch Processing

```json
{
  "tool": "insert_jsonrpc_to_db", 
  "arguments": {
    "jsonrpc_response": "[{\"jsonrpc\":\"2.0\",\"id\":1,\"result\":{\"name\":\"Alice\"}},{\"jsonrpc\":\"2.0\",\"id\":2,\"result\":{\"name\":\"Bob\"}}]",
    "database_type": "mongodb",
    "connection_string": "mongodb://localhost:27017/testdb",
    "table_name": "people",
    "batch_size": 500
  }
}
```

### Error Response Handling

```json
{
  "tool": "insert_jsonrpc_to_db",
  "arguments": {
    "jsonrpc_response": "{\"jsonrpc\":\"2.0\",\"id\":1,\"error\":{\"code\":-32600,\"message\":\"Invalid Request\"}}",
    "database_type": "sqlite",
    "connection_string": "sqlite:///errors.db",
    "table_name": "rpc_errors"
  }
}
```

### With UUID Generation

```json
{
  "tool": "insert_jsonrpc_to_db",
  "arguments": {
    "jsonrpc_response": "{\"jsonrpc\":\"2.0\",\"id\":1,\"result\":{\"data\":\"sample\"}}",
    "database_type": "mysql",
    "connection_string": "mysql://user:pass@localhost:3306/testdb",
    "uuid_fields": ["id", "tracking_id"],
    "add_timestamps": true
  }
}
```

### Schema Inspection

```json
{
  "tool": "query_schema",
  "arguments": {
    "database_type": "postgresql", 
    "connection_string": "postgresql://user:pass@localhost:5432/mydb",
    "table_name": "users"
  }
}
```

## Data Processing Pipeline

### 1. JSON-RPC Parsing
- Validates JSON-RPC 2.0 format
- Supports single responses and batch arrays
- Handles success results, error responses, and notifications
- Extracts structured data for database insertion

### 2. Data Extraction & Transformation
- **Success Responses**: Extract data from `result` field
- **Error Responses**: Create records with error code, message, and data
- **Notifications**: Extract method and parameters
- **Type Conversion**: Automatic type inference and database-specific conversion
- **Flattening**: Optional flattening of nested objects (e.g., `user.address.city` → `user_address_city`)

### 3. Schema Management
- **Inference**: Analyze data to determine appropriate database types
- **Auto-Creation**: Generate CREATE TABLE statements or collections
- **Compatibility**: Handle type conflicts across multiple records

### 4. Database Operations
- **Connection Management**: Automatic connection pooling and cleanup
- **Batch Processing**: Efficient bulk inserts with configurable batch sizes
- **Transaction Safety**: Proper error handling and rollback support
- **Performance Optimization**: Database-specific optimizations

## Type Mapping

### Relational Databases (PostgreSQL, MySQL, SQLite)

| JSON Type | PostgreSQL | MySQL | SQLite |
|-----------|------------|-------|--------|
| string | TEXT | TEXT | TEXT |
| number (int) | INTEGER | INT | INTEGER |
| number (float) | REAL | DOUBLE | REAL |
| boolean | BOOLEAN | BOOLEAN | INTEGER |
| object/array | JSONB | JSON | TEXT |
| null | NULL | NULL | NULL |

### NoSQL Databases

| JSON Type | MongoDB | Redis |
|-----------|---------|-------|
| string | string | string |
| number | int/double | string |
| boolean | bool | string |
| object | object | hash/string |
| array | array | string |

## Security Considerations

### Connection String Safety
- Connection strings are not logged or exposed in error messages
- Use environment variables for sensitive credentials
- Support for connection pooling and timeout controls

### Input Validation
- Comprehensive JSON-RPC format validation
- SQL injection prevention through parameterized queries
- Field name sanitization for database compatibility

### Error Handling
- Detailed error messages without exposing sensitive information
- Graceful handling of malformed JSON-RPC data
- Database connection cleanup on errors

## Performance Optimizations

### Batch Processing
- Configurable batch sizes (1-10,000 records)
- Optimized INSERT statements for each database type
- Memory-efficient streaming for large datasets

### Connection Management
- Automatic connection pooling
- Configurable timeouts and retry logic
- Proper connection cleanup and resource management

### Database-Specific Optimizations
- **PostgreSQL**: Uses asyncpg for optimal performance
- **MongoDB**: Bulk operations with `insert_many()`
- **Redis**: Hash-based storage for structured data
- **SQLite**: Transaction batching for improved write performance

## Debugging

### Enable Debug Mode

```bash
uvx mcp-server-db-insert --enable-debug
```

### Using MCP Inspector

```bash
npx @modelcontextprotocol/inspector uvx mcp-server-db-insert
```

### Common Issues

#### Connection Failures
- Verify database server is running and accessible
- Check connection string format and credentials
- Ensure network connectivity and firewall settings

#### Schema Creation Issues
- Verify database permissions for DDL operations
- Check for reserved keywords in field names
- Review database-specific type limitations

#### Data Type Mismatches
- Enable debug logging to see type inference decisions
- Use custom field mappings for specific type requirements
- Consider flattening complex nested structures

## Development

### Project Structure

```
mcp-server-db-insert/
├── src/mcp_server_db_insert/
│   ├── __init__.py           # Entry point and CLI
│   ├── __main__.py           # Module execution
│   ├── server.py             # Main MCP server implementation
│   ├── jsonrpc_parser.py     # JSON-RPC parsing and validation
│   ├── data_transformer.py   # Data transformation and type conversion
│   └── database_manager.py   # Database connection management
├── tests/                    # Test suite
├── examples/                 # Usage examples
├── pyproject.toml           # Project configuration
└── README.md                # This documentation
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the test suite: `pytest`
5. Submit a pull request

### Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=mcp_server_db_insert
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

- **Issues**: Report bugs and request features on GitHub
- **Documentation**: See examples/ directory for usage patterns
- **Community**: Join the Model Context Protocol community discussions

## Changelog

### v0.1.0
- Initial release
- Support for PostgreSQL, MongoDB, SQLite, Redis, MySQL
- JSON-RPC 2.0 parsing and validation
- Automatic schema inference and creation
- Batch processing capabilities
- Comprehensive error handling and logging
