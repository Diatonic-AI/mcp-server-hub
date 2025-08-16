"""
Sample JSON-RPC responses for testing the MCP Database Insert Server.

This module contains various JSON-RPC response examples that demonstrate
different scenarios and data types that the server can handle.
"""

# Successful JSON-RPC responses
SUCCESS_RESPONSES = {
    "simple_user": """{"jsonrpc": "2.0", "id": 1, "result": {"user_id": 123, "name": "John Doe", "email": "john@example.com", "active": true}}""",
    
    "nested_data": """{"jsonrpc": "2.0", "id": 2, "result": {"order_id": "ORD-001", "customer": {"name": "Alice Smith", "address": {"street": "123 Main St", "city": "Anytown", "zip": "12345"}}, "items": [{"product": "Widget", "quantity": 2, "price": 19.99}, {"product": "Gadget", "quantity": 1, "price": 39.99}], "total": 79.97}}""",
    
    "array_result": """{"jsonrpc": "2.0", "id": 3, "result": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}, {"name": "Charlie", "age": 35}]}""",
    
    "primitive_result": """{"jsonrpc": "2.0", "id": 4, "result": 42}""",
    
    "null_result": """{"jsonrpc": "2.0", "id": 5, "result": null}""",
    
    "complex_types": """{"jsonrpc": "2.0", "id": 6, "result": {"timestamp": "2024-01-15T10:30:00Z", "uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479", "decimal": 123.45, "boolean": true, "tags": ["important", "urgent"], "metadata": {"source": "api", "version": 2}}}"""
}

# Error JSON-RPC responses  
ERROR_RESPONSES = {
    "parse_error": """{"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": null}""",
    
    "invalid_request": """{"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": null}""",
    
    "method_not_found": """{"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": 1}""",
    
    "invalid_params": """{"jsonrpc": "2.0", "error": {"code": -32602, "message": "Invalid params", "data": {"expected": "string", "got": "number"}}, "id": 2}""",
    
    "internal_error": """{"jsonrpc": "2.0", "error": {"code": -32603, "message": "Internal error", "data": "Database connection failed"}, "id": 3}""",
    
    "custom_error": """{"jsonrpc": "2.0", "error": {"code": -32000, "message": "Server error", "data": {"error_type": "authentication_failed", "details": "Invalid API key"}}, "id": 4}"""
}

# JSON-RPC notifications (no id field)
NOTIFICATION_EXAMPLES = {
    "simple_notification": """{"jsonrpc": "2.0", "method": "update", "params": {"user_id": 123, "status": "online"}}""",
    
    "batch_notification": """{"jsonrpc": "2.0", "method": "log", "params": [{"level": "info", "message": "User logged in"}, {"level": "debug", "message": "Session created"}]}""",
    
    "no_params_notification": """{"jsonrpc": "2.0", "method": "heartbeat"}"""
}

# Batch JSON-RPC examples
BATCH_EXAMPLES = {
    "mixed_batch": """[
        {"jsonrpc": "2.0", "id": 1, "result": {"name": "Alice", "age": 30}},
        {"jsonrpc": "2.0", "id": 2, "error": {"code": -32601, "message": "Method not found"}},
        {"jsonrpc": "2.0", "method": "notify", "params": {"event": "user_created", "user_id": 123}}
    ]""",
    
    "success_batch": """[
        {"jsonrpc": "2.0", "id": 1, "result": {"product_id": 1, "name": "Widget", "price": 19.99}},
        {"jsonrpc": "2.0", "id": 2, "result": {"product_id": 2, "name": "Gadget", "price": 29.99}},
        {"jsonrpc": "2.0", "id": 3, "result": {"product_id": 3, "name": "Tool", "price": 39.99}}
    ]""",
    
    "error_batch": """[
        {"jsonrpc": "2.0", "id": 1, "error": {"code": -32600, "message": "Invalid Request"}},
        {"jsonrpc": "2.0", "id": 2, "error": {"code": -32601, "message": "Method not found"}},
        {"jsonrpc": "2.0", "id": 3, "error": {"code": -32602, "message": "Invalid params"}}
    ]"""
}

# Database-specific test cases
DATABASE_TEST_CASES = {
    "postgresql": {
        "connection_string": "postgresql://user:password@localhost:5432/testdb",
        "table_name": "jsonrpc_test",
        "sample_data": SUCCESS_RESPONSES["nested_data"]
    },
    
    "mysql": {
        "connection_string": "mysql://user:password@localhost:3306/testdb", 
        "table_name": "jsonrpc_test",
        "sample_data": SUCCESS_RESPONSES["complex_types"]
    },
    
    "sqlite": {
        "connection_string": "sqlite:///test.db",
        "table_name": "jsonrpc_test", 
        "sample_data": SUCCESS_RESPONSES["array_result"]
    },
    
    "mongodb": {
        "connection_string": "mongodb://localhost:27017/testdb",
        "table_name": "jsonrpc_test",
        "sample_data": SUCCESS_RESPONSES["nested_data"]
    },
    
    "redis": {
        "connection_string": "redis://localhost:6379/0",
        "table_name": "jsonrpc_test",
        "sample_data": SUCCESS_RESPONSES["simple_user"]
    }
}

# Edge cases for testing
EDGE_CASES = {
    "empty_result": """{"jsonrpc": "2.0", "id": 1, "result": {}}""",
    
    "very_large_number": """{"jsonrpc": "2.0", "id": 1, "result": {"big_number": 9223372036854775807}}""",
    
    "unicode_strings": """{"jsonrpc": "2.0", "id": 1, "result": {"name": "José María", "emoji": "😀🎉", "chinese": "你好世界"}}""",
    
    "special_characters": """{"jsonrpc": "2.0", "id": 1, "result": {"field with spaces": "value", "field-with-dashes": "value", "field.with.dots": "value", "field_with_underscores": "value"}}""",
    
    "deeply_nested": """{"jsonrpc": "2.0", "id": 1, "result": {"level1": {"level2": {"level3": {"level4": {"level5": {"value": "deep"}}}}}}}""",
    
    "large_array": """{"jsonrpc": "2.0", "id": 1, "result": {"items": [""" + ", ".join([f'{{"id": {i}, "value": "item_{i}"}}' for i in range(100)]) + """]}}""",
    
    "mixed_array_types": """{"jsonrpc": "2.0", "id": 1, "result": {"mixed": [1, "string", true, null, {"nested": "object"}, [1, 2, 3]]}}""",
    
    "empty_batch": """[]"""
}


def get_all_examples():
    """Get all example JSON-RPC responses organized by category."""
    return {
        "success_responses": SUCCESS_RESPONSES,
        "error_responses": ERROR_RESPONSES, 
        "notifications": NOTIFICATION_EXAMPLES,
        "batch_examples": BATCH_EXAMPLES,
        "database_test_cases": DATABASE_TEST_CASES,
        "edge_cases": EDGE_CASES
    }


def get_example_by_name(name: str) -> str:
    """Get a specific example by name from any category."""
    all_examples = get_all_examples()
    
    for category, examples in all_examples.items():
        if category == "database_test_cases":
            # Handle nested structure for database test cases
            for db_type, config in examples.items():
                if name == f"{db_type}_test":
                    return config["sample_data"]
        else:
            if name in examples:
                return examples[name]
    
    raise ValueError(f"Example '{name}' not found")


def get_examples_for_database(database_type: str):
    """Get relevant examples for a specific database type."""
    if database_type not in DATABASE_TEST_CASES:
        raise ValueError(f"Database type '{database_type}' not supported")
    
    config = DATABASE_TEST_CASES[database_type]
    return {
        "connection_string": config["connection_string"],
        "table_name": config["table_name"], 
        "sample_data": config["sample_data"],
        "additional_examples": [
            SUCCESS_RESPONSES["simple_user"],
            ERROR_RESPONSES["invalid_params"],
            BATCH_EXAMPLES["mixed_batch"]
        ]
    }


if __name__ == "__main__":
    """Print all examples for inspection."""
    import json
    
    all_examples = get_all_examples()
    
    for category, examples in all_examples.items():
        print(f"\n=== {category.upper()} ===")
        
        if category == "database_test_cases":
            for db_type, config in examples.items():
                print(f"\n{db_type}:")
                print(f"  Connection: {config['connection_string']}")
                print(f"  Table: {config['table_name']}")
                print(f"  Sample: {config['sample_data']}")
        else:
            for name, content in examples.items():
                print(f"\n{name}:")
                try:
                    # Pretty print JSON if possible
                    parsed = json.loads(content)
                    print(json.dumps(parsed, indent=2))
                except json.JSONDecodeError:
                    print(content)
