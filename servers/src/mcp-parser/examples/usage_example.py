#!/usr/bin/env python3
"""
Usage example for the MCP Database Insert Server.

This script demonstrates how to use the server's tools with various
database types and JSON-RPC response formats.
"""

import asyncio
import json
import sys
import os

# Add the src directory to the path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_server_db_insert.server import (
    process_jsonrpc_to_db,
    query_database_schema,
    test_database_connection,
    InsertJsonRpcToDb,
    QuerySchema,
    TestConnection
)
from sample_jsonrpc_responses import get_all_examples


async def demo_sqlite_usage():
    """Demonstrate basic usage with SQLite database."""
    print("=== SQLite Demo ===")
    
    # Sample JSON-RPC response
    jsonrpc_response = """{
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "user_id": 123,
            "name": "John Doe",
            "email": "john@example.com",
            "created": "2024-01-15T10:30:00Z",
            "active": true,
            "metadata": {
                "source": "api",
                "version": 2
            }
        }
    }"""
    
    # Test connection
    print("\n1. Testing SQLite connection...")
    connection_args = TestConnection(
        database_type="sqlite",
        connection_string="sqlite:///demo.db"
    )
    
    try:
        connection_result = await test_database_connection(connection_args)
        print(f"Connection test: {'✅ Success' if connection_result['connection_successful'] else '❌ Failed'}")
        if connection_result.get('error'):
            print(f"Error: {connection_result['error']}")
    except Exception as e:
        print(f"Connection test failed: {e}")
    
    # Insert data
    print("\n2. Inserting JSON-RPC data...")
    insert_args = InsertJsonRpcToDb(
        jsonrpc_response=jsonrpc_response,
        database_type="sqlite",
        connection_string="sqlite:///demo.db",
        table_name="users",
        uuid_fields=["record_id"],
        flatten_nested=True,
        add_timestamps=True
    )
    
    try:
        result = await process_jsonrpc_to_db(insert_args, enable_debug=True)
        print(f"Processed {result['processed_responses']} responses")
        print(f"Inserted {result['inserted_records']} records")
        print(f"Processing time: {result['processing_time_ms']}ms")
    except Exception as e:
        print(f"Insert failed: {e}")
    
    # Query schema
    print("\n3. Querying table schema...")
    schema_args = QuerySchema(
        database_type="sqlite",
        connection_string="sqlite:///demo.db",
        table_name="users"
    )
    
    try:
        schema_result = await query_database_schema(schema_args)
        print(f"Table exists: {schema_result['exists']}")
        if schema_result['schema']:
            print("Schema:")
            for field, type_name in schema_result['schema'].items():
                print(f"  {field}: {type_name}")
    except Exception as e:
        print(f"Schema query failed: {e}")


async def demo_error_handling():
    """Demonstrate handling of JSON-RPC error responses."""
    print("\n\n=== Error Response Demo ===")
    
    # JSON-RPC error response
    error_response = """{
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": -32602,
            "message": "Invalid params",
            "data": {
                "expected": "string",
                "got": "number",
                "field": "username"
            }
        }
    }"""
    
    insert_args = InsertJsonRpcToDb(
        jsonrpc_response=error_response,
        database_type="sqlite",
        connection_string="sqlite:///demo.db",
        table_name="errors",
        add_timestamps=True
    )
    
    try:
        result = await process_jsonrpc_to_db(insert_args, enable_debug=True)
        print(f"Inserted {result['inserted_records']} error records")
    except Exception as e:
        print(f"Error processing failed: {e}")


async def demo_batch_processing():
    """Demonstrate batch JSON-RPC processing."""
    print("\n\n=== Batch Processing Demo ===")
    
    # Batch JSON-RPC responses
    batch_response = """[
        {"jsonrpc": "2.0", "id": 1, "result": {"name": "Alice", "age": 30}},
        {"jsonrpc": "2.0", "id": 2, "result": {"name": "Bob", "age": 25}},
        {"jsonrpc": "2.0", "id": 3, "error": {"code": -32601, "message": "Method not found"}},
        {"jsonrpc": "2.0", "method": "notify", "params": {"event": "user_created", "user_id": 123}}
    ]"""
    
    insert_args = InsertJsonRpcToDb(
        jsonrpc_response=batch_response,
        database_type="sqlite",
        connection_string="sqlite:///demo.db",
        table_name="batch_data",
        batch_size=50,
        flatten_nested=False,
        add_timestamps=True
    )
    
    try:
        result = await process_jsonrpc_to_db(insert_args, enable_debug=True)
        print(f"Processed {result['processed_responses']} responses from batch")
        print(f"Inserted {result['inserted_records']} records")
    except Exception as e:
        print(f"Batch processing failed: {e}")


async def demo_complex_nested_data():
    """Demonstrate handling of complex nested JSON data."""
    print("\n\n=== Complex Nested Data Demo ===")
    
    # Complex nested JSON-RPC response
    complex_response = """{
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "order_id": "ORD-001",
            "customer": {
                "name": "Alice Smith",
                "contact": {
                    "email": "alice@example.com",
                    "phone": "+1-555-123-4567"
                },
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "zip": "12345",
                    "coordinates": {
                        "lat": 37.7749,
                        "lng": -122.4194
                    }
                }
            },
            "items": [
                {"product": "Widget", "quantity": 2, "price": 19.99},
                {"product": "Gadget", "quantity": 1, "price": 39.99}
            ],
            "shipping": {
                "method": "standard",
                "cost": 5.99,
                "tracking": "TRK123456789"
            },
            "total": 85.96,
            "timestamp": "2024-01-15T10:30:00Z"
        }
    }"""
    
    # Process with flattening
    print("\n1. Processing with nested structure flattening...")
    insert_args = InsertJsonRpcToDb(
        jsonrpc_response=complex_response,
        database_type="sqlite",
        connection_string="sqlite:///demo.db",
        table_name="orders_flat",
        flatten_nested=True,
        add_timestamps=True
    )
    
    try:
        result = await process_jsonrpc_to_db(insert_args, enable_debug=True)
        print(f"Flattened: Inserted {result['inserted_records']} records")
    except Exception as e:
        print(f"Flattened processing failed: {e}")
    
    # Process without flattening  
    print("\n2. Processing without flattening (JSON storage)...")
    insert_args.flatten_nested = False
    insert_args.table_name = "orders_json"
    
    try:
        result = await process_jsonrpc_to_db(insert_args, enable_debug=True)
        print(f"JSON storage: Inserted {result['inserted_records']} records")
    except Exception as e:
        print(f"JSON processing failed: {e}")


async def demo_all_examples():
    """Demonstrate processing of all example types from sample_jsonrpc_responses.py."""
    print("\n\n=== All Examples Demo ===")
    
    examples = get_all_examples()
    
    for category, example_dict in examples.items():
        if category == "database_test_cases":
            continue  # Skip database test cases as they have different structure
        
        print(f"\n--- {category.replace('_', ' ').title()} ---")
        
        for name, jsonrpc_data in example_dict.items():
            if name == "empty_batch":
                continue  # Skip empty batch as it will cause validation error
            
            print(f"\nProcessing {name}...")
            
            insert_args = InsertJsonRpcToDb(
                jsonrpc_response=jsonrpc_data,
                database_type="sqlite",
                connection_string="sqlite:///demo.db",
                table_name=f"example_{name}",
                add_timestamps=True
            )
            
            try:
                result = await process_jsonrpc_to_db(insert_args, enable_debug=False)
                print(f"  ✅ Success: {result['inserted_records']} records inserted")
            except Exception as e:
                print(f"  ❌ Failed: {str(e)}")


async def cleanup_demo_db():
    """Clean up demo database file."""
    try:
        if os.path.exists("demo.db"):
            os.remove("demo.db")
            print("Cleaned up demo.db")
    except Exception as e:
        print(f"Cleanup error: {e}")


async def main():
    """Run all demonstration examples."""
    print("MCP Database Insert Server - Usage Examples")
    print("=" * 50)
    
    try:
        # Run demonstrations
        await demo_sqlite_usage()
        await demo_error_handling()
        await demo_batch_processing()
        await demo_complex_nested_data()
        await demo_all_examples()
        
        print("\n\n=== Demo Complete ===")
        print("Check 'demo.db' file to see the inserted data.")
        print("\nYou can inspect the SQLite database with:")
        print("  sqlite3 demo.db")
        print("  .tables")
        print("  SELECT * FROM users;")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    # Optional cleanup
    response = input("\nDelete demo.db file? (y/N): ").strip().lower()
    if response == 'y':
        await cleanup_demo_db()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
