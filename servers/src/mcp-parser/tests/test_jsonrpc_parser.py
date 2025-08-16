"""
Test cases for JSON-RPC parsing functionality.
"""

import pytest
import json
from mcp.shared.exceptions import McpError

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_server_db_insert.jsonrpc_parser import (
    parse_jsonrpc_response,
    validate_jsonrpc_batch,
    extract_data_from_jsonrpc,
    prepare_records_for_db,
    sanitize_field_name,
    flatten_nested_dict,
    JsonRpcResponse
)


class TestJsonRpcResponseParsing:
    """Test JSON-RPC response parsing functionality."""
    
    def test_valid_success_response(self):
        """Test parsing a valid success response."""
        response_json = '{"jsonrpc": "2.0", "id": 1, "result": {"name": "test"}}'
        response = parse_jsonrpc_response(response_json)
        
        assert response.jsonrpc == "2.0"
        assert response.id == 1
        assert response.result == {"name": "test"}
        assert response.error is None
        assert response.is_success
        assert not response.is_error
        assert not response.is_notification
    
    def test_valid_error_response(self):
        """Test parsing a valid error response."""
        response_json = '{"jsonrpc": "2.0", "id": 1, "error": {"code": -32600, "message": "Invalid Request"}}'
        response = parse_jsonrpc_response(response_json)
        
        assert response.jsonrpc == "2.0"
        assert response.id == 1
        assert response.result is None
        assert response.error == {"code": -32600, "message": "Invalid Request"}
        assert not response.is_success
        assert response.is_error
        assert not response.is_notification
    
    def test_valid_notification(self):
        """Test parsing a valid notification."""
        response_json = '{"jsonrpc": "2.0", "method": "update", "params": {"status": "online"}}'
        response = parse_jsonrpc_response(response_json)
        
        assert response.jsonrpc == "2.0"
        assert response.id is None
        assert response.method == "update"
        assert response.params == {"status": "online"}
        assert not response.is_success
        assert not response.is_error
        assert response.is_notification
    
    def test_null_result(self):
        """Test parsing response with null result."""
        response_json = '{"jsonrpc": "2.0", "id": 1, "result": null}'
        response = parse_jsonrpc_response(response_json)
        
        assert response.result is None
        assert response.is_success
    
    def test_invalid_json(self):
        """Test parsing invalid JSON."""
        with pytest.raises(McpError) as exc_info:
            parse_jsonrpc_response('{"invalid": json}')
        assert "Invalid JSON format" in str(exc_info.value.error.message)
    
    def test_wrong_jsonrpc_version(self):
        """Test parsing with wrong JSON-RPC version."""
        response_json = '{"jsonrpc": "1.0", "id": 1, "result": "test"}'
        with pytest.raises(McpError) as exc_info:
            parse_jsonrpc_response(response_json)
        assert "Unsupported JSON-RPC version" in str(exc_info.value.error.message)
    
    def test_missing_jsonrpc_field(self):
        """Test parsing without jsonrpc field."""
        response_json = '{"id": 1, "result": "test"}'
        with pytest.raises(McpError) as exc_info:
            parse_jsonrpc_response(response_json)
        assert "Unsupported JSON-RPC version" in str(exc_info.value.error.message)
    
    def test_both_result_and_error(self):
        """Test parsing response with both result and error."""
        response_json = '{"jsonrpc": "2.0", "id": 1, "result": "test", "error": {"code": -32600, "message": "Invalid Request"}}'
        with pytest.raises(McpError) as exc_info:
            parse_jsonrpc_response(response_json)
        assert "cannot have both 'result' and 'error' fields" in str(exc_info.value.error.message)
    
    def test_neither_result_nor_error(self):
        """Test parsing response with neither result nor error."""
        response_json = '{"jsonrpc": "2.0", "id": 1}'
        with pytest.raises(McpError) as exc_info:
            parse_jsonrpc_response(response_json)
        assert "must have either 'result' or 'error' field" in str(exc_info.value.error.message)
    
    def test_notification_with_result(self):
        """Test parsing notification with result field."""
        response_json = '{"jsonrpc": "2.0", "method": "test", "result": "invalid"}'
        with pytest.raises(McpError) as exc_info:
            parse_jsonrpc_response(response_json)
        assert "notification cannot have 'result' or 'error' fields" in str(exc_info.value.error.message)


class TestBatchValidation:
    """Test JSON-RPC batch validation."""
    
    def test_valid_batch(self):
        """Test parsing a valid batch."""
        batch_json = """[
            {"jsonrpc": "2.0", "id": 1, "result": {"name": "Alice"}},
            {"jsonrpc": "2.0", "id": 2, "error": {"code": -32600, "message": "Invalid Request"}},
            {"jsonrpc": "2.0", "method": "notify", "params": {"status": "online"}}
        ]"""
        responses = validate_jsonrpc_batch(batch_json)
        
        assert len(responses) == 3
        assert responses[0].is_success
        assert responses[1].is_error
        assert responses[2].is_notification
    
    def test_single_response_as_batch(self):
        """Test parsing single response (not in array)."""
        response_json = '{"jsonrpc": "2.0", "id": 1, "result": {"name": "test"}}'
        responses = validate_jsonrpc_batch(response_json)
        
        assert len(responses) == 1
        assert responses[0].is_success
    
    def test_empty_batch(self):
        """Test parsing empty batch."""
        with pytest.raises(McpError) as exc_info:
            validate_jsonrpc_batch('[]')
        assert "batch cannot be empty" in str(exc_info.value.error.message)
    
    def test_batch_with_invalid_item(self):
        """Test parsing batch with invalid item."""
        batch_json = """[
            {"jsonrpc": "2.0", "id": 1, "result": {"name": "Alice"}},
            {"jsonrpc": "1.0", "id": 2, "result": "invalid"}
        ]"""
        with pytest.raises(McpError) as exc_info:
            validate_jsonrpc_batch(batch_json)
        assert "Invalid item at index 1" in str(exc_info.value.error.message)


class TestDataExtraction:
    """Test data extraction from JSON-RPC responses."""
    
    def test_extract_from_success_response(self):
        """Test extracting data from success response."""
        response = JsonRpcResponse(
            jsonrpc="2.0",
            id=1,
            result={"name": "Alice", "age": 30}
        )
        records = extract_data_from_jsonrpc(response)
        
        assert len(records) == 1
        assert records[0]["name"] == "Alice"
        assert records[0]["age"] == 30
        assert records[0]["jsonrpc_id"] == 1
        assert records[0]["is_success"] is True
    
    def test_extract_from_error_response(self):
        """Test extracting data from error response."""
        response = JsonRpcResponse(
            jsonrpc="2.0",
            id=1,
            error={"code": -32600, "message": "Invalid Request", "data": "extra info"}
        )
        records = extract_data_from_jsonrpc(response)
        
        assert len(records) == 1
        assert records[0]["error_code"] == -32600
        assert records[0]["error_message"] == "Invalid Request"
        assert records[0]["error_data"] == "extra info"
        assert records[0]["is_error"] is True
    
    def test_extract_from_notification(self):
        """Test extracting data from notification."""
        response = JsonRpcResponse(
            jsonrpc="2.0",
            id=None,
            method="update",
            params={"status": "online"}
        )
        records = extract_data_from_jsonrpc(response)
        
        assert len(records) == 1
        assert records[0]["method"] == "update"
        assert records[0]["params"] == {"status": "online"}
        assert records[0]["is_notification"] is True
    
    def test_extract_from_array_result(self):
        """Test extracting data from array result."""
        response = JsonRpcResponse(
            jsonrpc="2.0",
            id=1,
            result=[{"name": "Alice"}, {"name": "Bob"}]
        )
        records = extract_data_from_jsonrpc(response)
        
        assert len(records) == 2
        assert records[0]["name"] == "Alice"
        assert records[0]["result_index"] == 0
        assert records[1]["name"] == "Bob"
        assert records[1]["result_index"] == 1
    
    def test_extract_primitive_result(self):
        """Test extracting primitive result."""
        response = JsonRpcResponse(
            jsonrpc="2.0",
            id=1,
            result=42
        )
        records = extract_data_from_jsonrpc(response)
        
        assert len(records) == 1
        assert records[0]["result_value"] == 42
        assert records[0]["result_type"] == "int"


class TestFieldSanitization:
    """Test field name sanitization."""
    
    def test_sanitize_normal_field(self):
        """Test sanitizing normal field name."""
        assert sanitize_field_name("user_name") == "user_name"
        assert sanitize_field_name("userName") == "username"
    
    def test_sanitize_special_characters(self):
        """Test sanitizing field names with special characters."""
        assert sanitize_field_name("field with spaces") == "field_with_spaces"
        assert sanitize_field_name("field-with-dashes") == "field_with_dashes"
        assert sanitize_field_name("field.with.dots") == "field_with_dots"
        assert sanitize_field_name("field@with#symbols") == "field_with_symbols"
    
    def test_sanitize_leading_number(self):
        """Test sanitizing field name starting with number."""
        assert sanitize_field_name("123field") == "field_123field"
    
    def test_sanitize_long_field_name(self):
        """Test sanitizing very long field name."""
        long_name = "a" * 100
        result = sanitize_field_name(long_name)
        assert len(result) <= 63
        assert result.startswith("a")


class TestNestedFlattening:
    """Test nested dictionary flattening."""
    
    def test_flatten_simple_nested(self):
        """Test flattening simple nested dictionary."""
        nested = {
            "user": {
                "name": "Alice",
                "age": 30
            },
            "active": True
        }
        flattened = flatten_nested_dict(nested)
        
        assert flattened["user_name"] == "Alice"
        assert flattened["user_age"] == 30
        assert flattened["active"] is True
    
    def test_flatten_deeply_nested(self):
        """Test flattening deeply nested dictionary."""
        nested = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep"
                    }
                }
            }
        }
        flattened = flatten_nested_dict(nested)
        
        assert flattened["level1_level2_level3_value"] == "deep"
    
    def test_flatten_with_arrays(self):
        """Test flattening dictionary with arrays."""
        nested = {
            "user": {
                "name": "Alice",
                "tags": ["admin", "user"]
            }
        }
        flattened = flatten_nested_dict(nested)
        
        assert flattened["user_name"] == "Alice"
        assert json.loads(flattened["user_tags"]) == ["admin", "user"]
    
    def test_flatten_empty_dict(self):
        """Test flattening empty dictionary."""
        flattened = flatten_nested_dict({})
        assert flattened == {}


class TestRecordPreparation:
    """Test record preparation for database insertion."""
    
    def test_prepare_with_flattening(self):
        """Test preparing records with flattening."""
        records = [
            {
                "user": {
                    "name": "Alice",
                    "contact": {
                        "email": "alice@example.com"
                    }
                },
                "active": True
            }
        ]
        prepared = prepare_records_for_db(records, flatten=True)
        
        assert len(prepared) == 1
        assert "user_name" in prepared[0]
        assert "user_contact_email" in prepared[0]
        assert prepared[0]["active"] is True
    
    def test_prepare_without_flattening(self):
        """Test preparing records without flattening."""
        records = [
            {
                "user": {
                    "name": "Alice"
                },
                "tags": ["admin", "user"]
            }
        ]
        prepared = prepare_records_for_db(records, flatten=False)
        
        assert len(prepared) == 1
        assert isinstance(prepared[0]["user"], str)  # Should be JSON string
        assert isinstance(prepared[0]["tags"], str)  # Should be JSON string
    
    def test_prepare_field_name_sanitization(self):
        """Test field name sanitization during preparation."""
        records = [
            {
                "field with spaces": "value1",
                "field.with.dots": "value2",
                "field-with-dashes": "value3"
            }
        ]
        prepared = prepare_records_for_db(records, flatten=False)
        
        assert "field_with_spaces" in prepared[0]
        assert "field_with_dots" in prepared[0] 
        assert "field_with_dashes" in prepared[0]


if __name__ == "__main__":
    pytest.main([__file__])
