import json
import logging
from typing import Annotated, Dict, List, Optional, Union, Literal
from datetime import datetime

from mcp.shared.exceptions import McpError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    ErrorData,
    TextContent,
    Tool,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)
from pydantic import BaseModel, Field

from .jsonrpc_parser import (
    parse_jsonrpc_response,
    validate_jsonrpc_batch,
    extract_data_from_jsonrpc,
    prepare_records_for_db
)
from .database_manager import DatabaseManager, DatabaseConnection
from .data_transformer import DatabaseType, DataTransformer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InsertJsonRpcToDb(BaseModel):
    """Parameters for inserting JSON-RPC responses into database."""
    
    jsonrpc_response: Annotated[str, Field(
        description="Raw JSON-RPC response string to parse and insert"
    )]
    database_type: Annotated[Literal["postgresql", "mongodb", "sqlite", "redis", "mysql"], Field(
        description="Database type to insert into"
    )]
    connection_string: Annotated[str, Field(
        description="Database connection string (e.g., 'postgresql://user:pass@host/db')"
    )]
    schema_name: Annotated[Optional[str], Field(
        default=None,
        description="Target schema name (optional, will be inferred if not provided)"
    )]
    table_name: Annotated[Optional[str], Field(
        default=None,
        description="Target table/collection name (optional, defaults to 'jsonrpc_data')"
    )]
    uuid_fields: Annotated[Optional[List[str]], Field(
        default=None,
        description="List of field names that should receive generated UUIDs"
    )]
    create_if_missing: Annotated[bool, Field(
        default=True,
        description="Automatically create tables/collections if they don't exist"
    )]
    batch_size: Annotated[int, Field(
        default=100,
        ge=1,
        le=10000,
        description="Batch size for bulk insert operations"
    )]
    flatten_nested: Annotated[bool, Field(
        default=True,
        description="Flatten nested JSON structures for relational databases"
    )]
    add_timestamps: Annotated[bool, Field(
        default=True,
        description="Add created_at/updated_at timestamp fields"
    )]


class QuerySchema(BaseModel):
    """Parameters for querying database schema."""
    
    database_type: Annotated[Literal["postgresql", "mongodb", "sqlite", "redis", "mysql"], Field(
        description="Database type to query"
    )]
    connection_string: Annotated[str, Field(
        description="Database connection string"
    )]
    table_name: Annotated[str, Field(
        description="Table/collection name to inspect"
    )]


class TestConnection(BaseModel):
    """Parameters for testing database connectivity."""
    
    database_type: Annotated[Literal["postgresql", "mongodb", "sqlite", "redis", "mysql"], Field(
        description="Database type to test"
    )]
    connection_string: Annotated[str, Field(
        description="Database connection string"
    )]


async def process_jsonrpc_to_db(
    args: InsertJsonRpcToDb,
    connection_timeout: int = 30,
    enable_debug: bool = False
) -> Dict[str, Union[int, str, List[str]]]:
    """
    Process JSON-RPC response and insert into database.
    This is the main chained operation that handles the entire pipeline.
    """
    start_time = datetime.utcnow()
    result = {
        "processed_responses": 0,
        "inserted_records": 0,
        "table_name": args.table_name or "jsonrpc_data",
        "database_type": args.database_type,
        "errors": [],
        "processing_time_ms": 0
    }
    
    db_connection = None
    
    try:
        # Step 1: Parse JSON-RPC response(s)
        if enable_debug:
            logger.info("Step 1: Parsing JSON-RPC response")
        
        responses = validate_jsonrpc_batch(args.jsonrpc_response)
        result["processed_responses"] = len(responses)
        
        if enable_debug:
            logger.info(f"Parsed {len(responses)} JSON-RPC responses")
        
        # Step 2: Extract data records from responses
        if enable_debug:
            logger.info("Step 2: Extracting data records")
        
        all_records = []
        for response in responses:
            records = extract_data_from_jsonrpc(response)
            all_records.extend(records)
        
        if not all_records:
            result["errors"].append("No data records extracted from JSON-RPC responses")
            return result
        
        if enable_debug:
            logger.info(f"Extracted {len(all_records)} data records")
        
        # Step 3: Transform and prepare records
        if enable_debug:
            logger.info("Step 3: Transforming data records")
        
        # Create database connection
        db_connection = DatabaseManager.create_connection(
            args.connection_string, 
            connection_timeout
        )
        await db_connection.connect()
        
        # Transform records for database compatibility
        transformer = db_connection.transformer
        
        # Prepare records (flatten if requested)
        prepared_records = prepare_records_for_db(all_records, args.flatten_nested)
        
        # Transform records with UUIDs and timestamps
        transformed_records = transformer.transform_records(
            prepared_records,
            uuid_fields=args.uuid_fields,
            add_timestamps=args.add_timestamps
        )
        
        if enable_debug:
            logger.info(f"Transformed {len(transformed_records)} records")
        
        # Step 4: Schema management
        table_name = args.table_name or "jsonrpc_data"
        result["table_name"] = table_name
        
        if enable_debug:
            logger.info(f"Step 4: Schema management for table '{table_name}'")
        
        # Check if table exists
        table_exists = await db_connection.table_exists(table_name)
        
        if not table_exists and args.create_if_missing:
            # Infer schema from transformed records
            schema = transformer.infer_schema(transformed_records)
            if enable_debug:
                logger.info(f"Inferred schema: {schema}")
            
            # Create table/collection
            await db_connection.create_table_or_collection(table_name, schema)
            if enable_debug:
                logger.info(f"Created table/collection '{table_name}'")
        
        elif not table_exists:
            raise McpError(ErrorData(
                code=INVALID_PARAMS,
                message=f"Table/collection '{table_name}' does not exist and create_if_missing is False"
            ))
        
        # Step 5: Insert records
        if enable_debug:
            logger.info("Step 5: Inserting records into database")
        
        inserted_count = await db_connection.insert_records(
            table_name,
            transformed_records,
            args.batch_size
        )
        
        result["inserted_records"] = inserted_count
        
        if enable_debug:
            logger.info(f"Successfully inserted {inserted_count} records")
    
    except McpError:
        # Re-raise MCP errors as-is
        raise
    except Exception as e:
        # Wrap unexpected errors
        error_msg = f"Unexpected error in JSON-RPC to DB processing: {str(e)}"
        result["errors"].append(error_msg)
        logger.error(error_msg, exc_info=True)
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=error_msg
        ))
    
    finally:
        # Always clean up database connection
        if db_connection:
            try:
                await db_connection.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting from database: {e}")
        
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds() * 1000
        result["processing_time_ms"] = round(processing_time, 2)
    
    return result


async def query_database_schema(
    args: QuerySchema,
    connection_timeout: int = 30
) -> Dict[str, Union[str, Dict[str, str], bool]]:
    """Query database schema information."""
    
    result = {
        "table_name": args.table_name,
        "database_type": args.database_type,
        "exists": False,
        "schema": {},
        "error": None
    }
    
    db_connection = None
    
    try:
        # Create connection
        db_connection = DatabaseManager.create_connection(
            args.connection_string,
            connection_timeout
        )
        await db_connection.connect()
        
        # Check if table exists
        table_exists = await db_connection.table_exists(args.table_name)
        result["exists"] = table_exists
        
        if table_exists:
            # Get schema
            schema = await db_connection.get_schema(args.table_name)
            result["schema"] = schema or {}
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Error querying schema for {args.table_name}: {e}")
    
    finally:
        if db_connection:
            try:
                await db_connection.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting from database: {e}")
    
    return result


async def test_database_connection(
    args: TestConnection,
    connection_timeout: int = 30
) -> Dict[str, Union[str, bool]]:
    """Test database connectivity."""
    
    result = {
        "database_type": args.database_type,
        "connection_successful": False,
        "error": None
    }
    
    db_connection = None
    
    try:
        # Create and test connection
        db_connection = DatabaseManager.create_connection(
            args.connection_string,
            connection_timeout
        )
        await db_connection.connect()
        
        # Test connection
        is_connected = await db_connection.test_connection()
        result["connection_successful"] = is_connected
        
        if not is_connected:
            result["error"] = "Connection test failed"
    
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Connection test failed for {args.database_type}: {e}")
    
    finally:
        if db_connection:
            try:
                await db_connection.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting from database: {e}")
    
    return result


async def serve(
    max_batch_size: int = 1000,
    connection_timeout: int = 30,
    enable_debug: bool = False
) -> None:
    """Run the database insert MCP server."""
    
    if enable_debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Debug logging enabled")
    
    server = Server("mcp-db-insert")
    
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available MCP tools."""
        return [
            Tool(
                name="insert_jsonrpc_to_db",
                description="""Parse JSON-RPC responses and insert data into databases.

This tool provides a complete pipeline for processing JSON-RPC responses:
1. Parse and validate JSON-RPC format (supports both single responses and batches)
2. Extract data records from response/error/notification content
3. Transform data for database compatibility (type conversion, flattening, UUID generation)
4. Create database tables/collections if they don't exist
5. Insert records in batches for optimal performance

Supports PostgreSQL, MongoDB, SQLite, Redis, and MySQL databases.""",
                inputSchema=InsertJsonRpcToDb.model_json_schema(),
            ),
            Tool(
                name="query_schema",
                description="""Query database schema information for a specific table or collection.

Returns information about:
- Whether the table/collection exists
- Field names and types (schema)
- Database-specific type information

Useful for inspecting existing database structures before inserting data.""",
                inputSchema=QuerySchema.model_json_schema(),
            ),
            Tool(
                name="test_connection",
                description="""Test database connectivity with the provided connection string.

Validates that:
- Connection string format is correct
- Database server is reachable  
- Authentication credentials are valid
- Database/schema is accessible

Returns connection status and any error messages.""",
                inputSchema=TestConnection.model_json_schema(),
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> List[TextContent]:
        """Handle tool calls."""
        
        try:
            if name == "insert_jsonrpc_to_db":
                try:
                    args = InsertJsonRpcToDb(**arguments)
                except ValueError as e:
                    raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
                
                # Validate batch size against server max
                if args.batch_size > max_batch_size:
                    args.batch_size = max_batch_size
                    logger.warning(f"Batch size capped at {max_batch_size}")
                
                result = await process_jsonrpc_to_db(
                    args, 
                    connection_timeout=connection_timeout,
                    enable_debug=enable_debug
                )
                
                response_text = f"""JSON-RPC to Database Insert Results:

📊 Summary:
- Processed {result['processed_responses']} JSON-RPC response(s)  
- Inserted {result['inserted_records']} record(s)
- Target: {result['database_type']} table '{result['table_name']}'
- Processing time: {result['processing_time_ms']}ms

✅ Operation completed successfully"""
                
                if result.get('errors'):
                    response_text += f"\n\n⚠️ Warnings:\n" + '\n'.join(f"- {error}" for error in result['errors'])
                
                return [TextContent(type="text", text=response_text)]
            
            elif name == "query_schema":
                try:
                    args = QuerySchema(**arguments)
                except ValueError as e:
                    raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
                
                result = await query_database_schema(args, connection_timeout)
                
                if result.get('error'):
                    response_text = f"""❌ Schema Query Failed:

Database: {result['database_type']}
Table: {result['table_name']}
Error: {result['error']}"""
                else:
                    response_text = f"""📋 Database Schema Information:

Database: {result['database_type']}
Table: {result['table_name']}
Exists: {'✅ Yes' if result['exists'] else '❌ No'}"""
                    
                    if result['exists'] and result['schema']:
                        response_text += "\n\n📝 Schema:\n"
                        for field_name, field_type in result['schema'].items():
                            response_text += f"- {field_name}: {field_type}\n"
                    elif result['exists']:
                        response_text += "\n\n(Schema could not be determined)"
                
                return [TextContent(type="text", text=response_text)]
            
            elif name == "test_connection":
                try:
                    args = TestConnection(**arguments)
                except ValueError as e:
                    raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
                
                result = await test_database_connection(args, connection_timeout)
                
                if result['connection_successful']:
                    response_text = f"""✅ Database Connection Successful:

Database Type: {result['database_type']}
Status: Connected and responsive"""
                else:
                    response_text = f"""❌ Database Connection Failed:

Database Type: {result['database_type']}
Status: Connection failed"""
                    
                    if result.get('error'):
                        response_text += f"\nError: {result['error']}"
                
                return [TextContent(type="text", text=response_text)]
            
            else:
                raise McpError(ErrorData(
                    code=INVALID_PARAMS,
                    message=f"Unknown tool: {name}"
                ))
        
        except McpError:
            # Re-raise MCP errors
            raise
        except Exception as e:
            # Wrap unexpected errors
            logger.error(f"Unexpected error in tool '{name}': {e}", exc_info=True)
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Internal server error in tool '{name}': {str(e)}"
            ))
    
    # Run the server
    logger.info("Starting MCP Database Insert Server")
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
