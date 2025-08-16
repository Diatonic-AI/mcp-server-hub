import json
import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INVALID_PARAMS, INTERNAL_ERROR

logger = logging.getLogger(__name__)


@dataclass
class JsonRpcResponse:
    """Structured representation of a JSON-RPC response."""
    jsonrpc: str
    id: Optional[Union[str, int, None]]
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    method: Optional[str] = None  # For notifications
    params: Optional[Any] = None  # For notifications
    
    @property
    def is_success(self) -> bool:
        """Check if the response indicates success."""
        return self.error is None
    
    @property
    def is_error(self) -> bool:
        """Check if the response indicates an error."""
        return self.error is not None
    
    @property
    def is_notification(self) -> bool:
        """Check if this is a notification (has method but no id)."""
        return self.method is not None and self.id is None


def parse_jsonrpc_response(jsonrpc_string: str) -> JsonRpcResponse:
    """
    Parse a JSON-RPC response string into a structured format.
    
    Args:
        jsonrpc_string: Raw JSON-RPC response string
        
    Returns:
        JsonRpcResponse object with parsed data
        
    Raises:
        McpError: If parsing fails or format is invalid
    """
    try:
        data = json.loads(jsonrpc_string.strip())
    except json.JSONDecodeError as e:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message=f"Invalid JSON format: {str(e)}"
        ))
    
    if not isinstance(data, dict):
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="JSON-RPC response must be an object"
        ))
    
    # Validate JSON-RPC version
    jsonrpc_version = data.get("jsonrpc")
    if jsonrpc_version != "2.0":
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message=f"Unsupported JSON-RPC version: {jsonrpc_version}. Only 2.0 is supported."
        ))
    
    # Extract fields
    rpc_id = data.get("id")
    result = data.get("result")
    error = data.get("error")
    method = data.get("method")  # For notifications
    params = data.get("params")   # For notifications
    
    # Validate response structure
    if "id" in data:  # Regular response
        if result is not None and error is not None:
            raise McpError(ErrorData(
                code=INVALID_PARAMS,
                message="JSON-RPC response cannot have both 'result' and 'error' fields"
            ))
        if result is None and error is None:
            raise McpError(ErrorData(
                code=INVALID_PARAMS,
                message="JSON-RPC response must have either 'result' or 'error' field"
            ))
    elif "method" in data:  # Notification
        if "result" in data or "error" in data:
            raise McpError(ErrorData(
                code=INVALID_PARAMS,
                message="JSON-RPC notification cannot have 'result' or 'error' fields"
            ))
    else:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="JSON-RPC response must have either 'id' or 'method' field"
        ))
    
    return JsonRpcResponse(
        jsonrpc=jsonrpc_version,
        id=rpc_id,
        result=result,
        error=error,
        method=method,
        params=params
    )


def extract_data_from_jsonrpc(response: JsonRpcResponse) -> List[Dict[str, Any]]:
    """
    Extract data records from a JSON-RPC response for database insertion.
    
    Args:
        response: Parsed JSON-RPC response
        
    Returns:
        List of dictionaries representing records to insert
        
    Raises:
        McpError: If data extraction fails
    """
    records = []
    
    if response.is_error:
        # For error responses, create a record with error information
        error_record = {
            "jsonrpc_id": response.id,
            "jsonrpc_version": response.jsonrpc,
            "error_code": response.error.get("code") if response.error else None,
            "error_message": response.error.get("message") if response.error else None,
            "error_data": response.error.get("data") if response.error else None,
            "is_error": True
        }
        records.append(error_record)
        
    elif response.is_notification:
        # For notifications, extract method and params
        notification_record = {
            "jsonrpc_version": response.jsonrpc,
            "method": response.method,
            "params": response.params,
            "is_notification": True
        }
        records.append(notification_record)
        
    else:
        # For successful responses, extract result data
        if response.result is None:
            records.append({
                "jsonrpc_id": response.id,
                "jsonrpc_version": response.jsonrpc,
                "result": None,
                "is_success": True
            })
        elif isinstance(response.result, dict):
            # Single record
            record = dict(response.result)
            record.update({
                "jsonrpc_id": response.id,
                "jsonrpc_version": response.jsonrpc,
                "is_success": True
            })
            records.append(record)
        elif isinstance(response.result, list):
            # Multiple records
            for i, item in enumerate(response.result):
                if isinstance(item, dict):
                    record = dict(item)
                    record.update({
                        "jsonrpc_id": response.id,
                        "jsonrpc_version": response.jsonrpc,
                        "result_index": i,
                        "is_success": True
                    })
                    records.append(record)
                else:
                    # Primitive values in array
                    records.append({
                        "jsonrpc_id": response.id,
                        "jsonrpc_version": response.jsonrpc,
                        "result_value": item,
                        "result_index": i,
                        "result_type": type(item).__name__,
                        "is_success": True
                    })
        else:
            # Primitive result value
            records.append({
                "jsonrpc_id": response.id,
                "jsonrpc_version": response.jsonrpc,
                "result_value": response.result,
                "result_type": type(response.result).__name__,
                "is_success": True
            })
    
    return records


def validate_jsonrpc_batch(jsonrpc_string: str) -> List[JsonRpcResponse]:
    """
    Parse and validate a JSON-RPC batch request/response.
    
    Args:
        jsonrpc_string: Raw JSON-RPC string (may be batch)
        
    Returns:
        List of JsonRpcResponse objects
        
    Raises:
        McpError: If parsing fails or format is invalid
    """
    try:
        data = json.loads(jsonrpc_string.strip())
    except json.JSONDecodeError as e:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message=f"Invalid JSON format: {str(e)}"
        ))
    
    if isinstance(data, list):
        # Batch request/response
        if len(data) == 0:
            raise McpError(ErrorData(
                code=INVALID_PARAMS,
                message="JSON-RPC batch cannot be empty"
            ))
        
        responses = []
        for i, item in enumerate(data):
            try:
                item_json = json.dumps(item)
                response = parse_jsonrpc_response(item_json)
                responses.append(response)
            except McpError as e:
                raise McpError(ErrorData(
                    code=INVALID_PARAMS,
                    message=f"Invalid item at index {i} in batch: {e.error.message}"
                ))
        return responses
    else:
        # Single request/response
        return [parse_jsonrpc_response(jsonrpc_string)]


def sanitize_field_name(name: str) -> str:
    """
    Sanitize field names for database compatibility.
    
    Args:
        name: Original field name
        
    Returns:
        Sanitized field name safe for database use
    """
    import re
    
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', str(name))
    
    # Ensure it starts with a letter or underscore
    if not re.match(r'^[a-zA-Z_]', sanitized):
        sanitized = f"field_{sanitized}"
    
    # Limit length (most databases have limits)
    if len(sanitized) > 63:  # PostgreSQL limit
        sanitized = sanitized[:63]
    
    # Convert to lowercase for consistency
    return sanitized.lower()


def flatten_nested_dict(data: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    Flatten nested dictionary structures for simpler database storage.
    
    Args:
        data: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for nested keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        new_key = sanitize_field_name(new_key)
        
        if isinstance(v, dict):
            items.extend(flatten_nested_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert lists to JSON strings for storage
            items.append((new_key, json.dumps(v)))
        else:
            items.append((new_key, v))
    
    return dict(items)


def prepare_records_for_db(records: List[Dict[str, Any]], flatten: bool = True) -> List[Dict[str, Any]]:
    """
    Prepare records for database insertion by sanitizing and optionally flattening.
    
    Args:
        records: List of record dictionaries
        flatten: Whether to flatten nested structures
        
    Returns:
        List of prepared record dictionaries
    """
    prepared_records = []
    
    for record in records:
        if flatten:
            # Flatten nested structures
            flattened = flatten_nested_dict(record)
            prepared_records.append(flattened)
        else:
            # Just sanitize field names
            sanitized = {}
            for key, value in record.items():
                clean_key = sanitize_field_name(key)
                # Convert complex types to JSON strings
                if isinstance(value, (dict, list)):
                    sanitized[clean_key] = json.dumps(value)
                else:
                    sanitized[clean_key] = value
            prepared_records.append(sanitized)
    
    return prepared_records
