import json
import uuid
import logging
from datetime import datetime, date, time
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union, Tuple, Type
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    SQLITE = "sqlite"
    REDIS = "redis"
    MYSQL = "mysql"


@dataclass
class FieldMapping:
    """Mapping configuration for database field transformation."""
    source_name: str
    target_name: str
    target_type: str
    is_required: bool = False
    default_value: Optional[Any] = None
    transform_func: Optional[str] = None  # Name of transformation function


class DataTransformer:
    """Handles data transformation for database compatibility."""
    
    def __init__(self, database_type: DatabaseType):
        self.database_type = database_type
        self.type_mappings = self._get_type_mappings()
    
    def _get_type_mappings(self) -> Dict[str, str]:
        """Get type mappings for the specific database type."""
        mappings = {
            DatabaseType.POSTGRESQL: {
                'str': 'TEXT',
                'int': 'INTEGER',
                'float': 'REAL',
                'bool': 'BOOLEAN',
                'datetime': 'TIMESTAMP',
                'date': 'DATE',
                'time': 'TIME',
                'uuid': 'UUID',
                'json': 'JSONB',
                'list': 'JSONB',
                'dict': 'JSONB',
                'decimal': 'NUMERIC',
                'bytes': 'BYTEA'
            },
            DatabaseType.MYSQL: {
                'str': 'TEXT',
                'int': 'INT',
                'float': 'DOUBLE',
                'bool': 'BOOLEAN',
                'datetime': 'DATETIME',
                'date': 'DATE',
                'time': 'TIME',
                'uuid': 'CHAR(36)',
                'json': 'JSON',
                'list': 'JSON',
                'dict': 'JSON',
                'decimal': 'DECIMAL(10,2)',
                'bytes': 'BLOB'
            },
            DatabaseType.SQLITE: {
                'str': 'TEXT',
                'int': 'INTEGER',
                'float': 'REAL',
                'bool': 'INTEGER',  # SQLite doesn't have boolean
                'datetime': 'TEXT',  # ISO format
                'date': 'TEXT',
                'time': 'TEXT',
                'uuid': 'TEXT',
                'json': 'TEXT',
                'list': 'TEXT',
                'dict': 'TEXT',
                'decimal': 'REAL',
                'bytes': 'BLOB'
            },
            DatabaseType.MONGODB: {
                # MongoDB is schema-less, but we track types for validation
                'str': 'string',
                'int': 'int',
                'float': 'double',
                'bool': 'bool',
                'datetime': 'date',
                'date': 'date',
                'time': 'string',
                'uuid': 'string',
                'json': 'object',
                'list': 'array',
                'dict': 'object',
                'decimal': 'decimal',
                'bytes': 'binData'
            },
            DatabaseType.REDIS: {
                # Redis is key-value, everything is stored as strings or hash fields
                'str': 'string',
                'int': 'string',
                'float': 'string',
                'bool': 'string',
                'datetime': 'string',
                'date': 'string',
                'time': 'string',
                'uuid': 'string',
                'json': 'string',
                'list': 'string',
                'dict': 'hash',
                'decimal': 'string',
                'bytes': 'string'
            }
        }
        return mappings.get(self.database_type, mappings[DatabaseType.POSTGRESQL])
    
    def infer_field_type(self, value: Any) -> str:
        """Infer the database field type from a Python value."""
        if value is None:
            return self.type_mappings.get('str', 'TEXT')  # Default to string
        
        python_type = type(value).__name__
        
        # Handle special cases
        if isinstance(value, str):
            # Check if it's a UUID string
            if self._is_uuid_string(value):
                return self.type_mappings.get('uuid', 'TEXT')
            # Check if it's a datetime string
            if self._is_datetime_string(value):
                return self.type_mappings.get('datetime', 'TEXT')
            return self.type_mappings.get('str', 'TEXT')
        elif isinstance(value, (dict, list)):
            return self.type_mappings.get('json', 'TEXT')
        elif isinstance(value, datetime):
            return self.type_mappings.get('datetime', 'TEXT')
        elif isinstance(value, date):
            return self.type_mappings.get('date', 'TEXT')
        elif isinstance(value, time):
            return self.type_mappings.get('time', 'TEXT')
        elif isinstance(value, Decimal):
            return self.type_mappings.get('decimal', 'REAL')
        elif isinstance(value, bytes):
            return self.type_mappings.get('bytes', 'TEXT')
        else:
            return self.type_mappings.get(python_type, 'TEXT')
    
    def _is_uuid_string(self, value: str) -> bool:
        """Check if a string is a valid UUID."""
        try:
            uuid.UUID(value)
            return True
        except (ValueError, AttributeError):
            return False
    
    def _is_datetime_string(self, value: str) -> bool:
        """Check if a string is a valid ISO datetime."""
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
            return True
        except (ValueError, AttributeError):
            return False
    
    def transform_value(self, value: Any, target_type: str = None) -> Any:
        """Transform a value for database compatibility."""
        if value is None:
            return None
        
        # If no target type specified, infer it
        if target_type is None:
            target_type = self.infer_field_type(value)
        
        # Database-specific transformations
        if self.database_type == DatabaseType.SQLITE:
            return self._transform_for_sqlite(value, target_type)
        elif self.database_type == DatabaseType.REDIS:
            return self._transform_for_redis(value, target_type)
        elif self.database_type == DatabaseType.MONGODB:
            return self._transform_for_mongodb(value, target_type)
        else:
            # PostgreSQL, MySQL (more standard SQL)
            return self._transform_for_sql(value, target_type)
    
    def _transform_for_sqlite(self, value: Any, target_type: str) -> Any:
        """Transform value for SQLite compatibility."""
        if isinstance(value, bool):
            return 1 if value else 0
        elif isinstance(value, (datetime, date, time)):
            return value.isoformat()
        elif isinstance(value, (dict, list)):
            return json.dumps(value)
        elif isinstance(value, uuid.UUID):
            return str(value)
        elif isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, bytes):
            return value  # SQLite handles BLOB natively
        return value
    
    def _transform_for_redis(self, value: Any, target_type: str) -> Any:
        """Transform value for Redis compatibility."""
        if isinstance(value, dict):
            # For Redis hash fields, return dict as-is
            if target_type == 'hash':
                return {str(k): str(v) for k, v in value.items()}
            else:
                return json.dumps(value)
        elif isinstance(value, (list, tuple)):
            return json.dumps(value)
        elif isinstance(value, (datetime, date, time)):
            return value.isoformat()
        elif isinstance(value, uuid.UUID):
            return str(value)
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, bytes):
            return value.hex()  # Convert to hex string
        else:
            return str(value)
    
    def _transform_for_mongodb(self, value: Any, target_type: str) -> Any:
        """Transform value for MongoDB compatibility."""
        if isinstance(value, (dict, list)):
            return value  # MongoDB handles these natively
        elif isinstance(value, uuid.UUID):
            return str(value)  # Store as string
        elif isinstance(value, (datetime, date)):
            return value  # MongoDB handles datetime natively
        elif isinstance(value, time):
            return value.isoformat()  # Time as string
        elif isinstance(value, Decimal):
            return float(value)  # Convert to float
        elif isinstance(value, bytes):
            return value  # MongoDB handles binary data
        return value
    
    def _transform_for_sql(self, value: Any, target_type: str) -> Any:
        """Transform value for standard SQL databases (PostgreSQL, MySQL)."""
        if isinstance(value, (dict, list)):
            if self.database_type == DatabaseType.POSTGRESQL:
                return json.dumps(value)  # Will be stored as JSONB
            else:
                return json.dumps(value)  # MySQL JSON
        elif isinstance(value, uuid.UUID):
            return str(value)
        elif isinstance(value, Decimal):
            return value  # SQL databases handle Decimal
        elif isinstance(value, (datetime, date, time)):
            return value  # SQL databases handle these natively
        return value
    
    def generate_uuid(self, uuid_version: int = 4) -> str:
        """Generate a UUID string."""
        if uuid_version == 1:
            return str(uuid.uuid1())
        elif uuid_version == 4:
            return str(uuid.uuid4())
        else:
            raise ValueError(f"Unsupported UUID version: {uuid_version}")
    
    def add_uuid_fields(self, record: Dict[str, Any], uuid_fields: List[str]) -> Dict[str, Any]:
        """Add UUID fields to a record."""
        updated_record = record.copy()
        for field_name in uuid_fields:
            if field_name not in updated_record or updated_record[field_name] is None:
                updated_record[field_name] = self.generate_uuid()
        return updated_record
    
    def add_timestamps(self, record: Dict[str, Any], 
                      created_field: str = "created_at",
                      updated_field: str = "updated_at") -> Dict[str, Any]:
        """Add timestamp fields to a record."""
        updated_record = record.copy()
        current_time = datetime.utcnow()
        
        if created_field and created_field not in updated_record:
            updated_record[created_field] = current_time
        
        if updated_field:
            updated_record[updated_field] = current_time
        
        return updated_record
    
    def transform_records(self, records: List[Dict[str, Any]], 
                         uuid_fields: Optional[List[str]] = None,
                         add_timestamps: bool = True,
                         field_mappings: Optional[List[FieldMapping]] = None) -> List[Dict[str, Any]]:
        """Transform a list of records for database insertion."""
        transformed_records = []
        
        for record in records:
            # Start with original record
            transformed_record = record.copy()
            
            # Apply field mappings if provided
            if field_mappings:
                transformed_record = self._apply_field_mappings(transformed_record, field_mappings)
            
            # Add UUID fields
            if uuid_fields:
                transformed_record = self.add_uuid_fields(transformed_record, uuid_fields)
            
            # Add timestamps
            if add_timestamps:
                transformed_record = self.add_timestamps(transformed_record)
            
            # Transform all values for database compatibility
            final_record = {}
            for key, value in transformed_record.items():
                transformed_value = self.transform_value(value)
                final_record[key] = transformed_value
            
            transformed_records.append(final_record)
        
        return transformed_records
    
    def _apply_field_mappings(self, record: Dict[str, Any], 
                             field_mappings: List[FieldMapping]) -> Dict[str, Any]:
        """Apply field mappings to transform record structure."""
        mapped_record = {}
        
        # Create lookup for mappings
        mapping_lookup = {mapping.source_name: mapping for mapping in field_mappings}
        
        for key, value in record.items():
            if key in mapping_lookup:
                mapping = mapping_lookup[key]
                # Apply transformation function if specified
                if mapping.transform_func:
                    value = self._apply_transform_function(value, mapping.transform_func)
                mapped_record[mapping.target_name] = value
            else:
                # Keep original field if no mapping specified
                mapped_record[key] = value
        
        # Add default values for required fields not present
        for mapping in field_mappings:
            if (mapping.is_required and 
                mapping.target_name not in mapped_record and 
                mapping.default_value is not None):
                mapped_record[mapping.target_name] = mapping.default_value
        
        return mapped_record
    
    def _apply_transform_function(self, value: Any, func_name: str) -> Any:
        """Apply a named transformation function to a value."""
        transform_functions = {
            'upper': lambda x: str(x).upper() if x is not None else None,
            'lower': lambda x: str(x).lower() if x is not None else None,
            'strip': lambda x: str(x).strip() if x is not None else None,
            'int': lambda x: int(x) if x is not None else None,
            'float': lambda x: float(x) if x is not None else None,
            'bool': lambda x: bool(x) if x is not None else None,
            'str': lambda x: str(x) if x is not None else None,
            'json_parse': lambda x: json.loads(x) if isinstance(x, str) else x,
            'json_stringify': lambda x: json.dumps(x) if not isinstance(x, str) else x,
        }
        
        if func_name in transform_functions:
            try:
                return transform_functions[func_name](value)
            except (ValueError, TypeError, json.JSONDecodeError) as e:
                logger.warning(f"Transform function '{func_name}' failed for value {value}: {e}")
                return value
        else:
            logger.warning(f"Unknown transform function: {func_name}")
            return value
    
    def infer_schema(self, records: List[Dict[str, Any]]) -> Dict[str, str]:
        """Infer database schema from a list of records."""
        if not records:
            return {}
        
        schema = {}
        
        # Analyze all records to determine field types
        for record in records:
            for field_name, value in record.items():
                field_type = self.infer_field_type(value)
                
                if field_name in schema:
                    # If we've seen this field before, ensure compatibility
                    existing_type = schema[field_name]
                    if existing_type != field_type:
                        # Handle type conflicts - default to more general type
                        if existing_type == 'INTEGER' and field_type == 'REAL':
                            schema[field_name] = field_type  # REAL is more general
                        elif existing_type == 'REAL' and field_type == 'INTEGER':
                            pass  # Keep REAL
                        else:
                            schema[field_name] = self.type_mappings.get('str', 'TEXT')  # Default to string
                else:
                    schema[field_name] = field_type
        
        return schema
    
    def get_create_table_sql(self, table_name: str, schema: Dict[str, str], 
                            primary_key: Optional[str] = None) -> str:
        """Generate CREATE TABLE SQL for relational databases."""
        if self.database_type in [DatabaseType.MONGODB, DatabaseType.REDIS]:
            raise ValueError(f"SQL not applicable for {self.database_type.value}")
        
        columns = []
        for field_name, field_type in schema.items():
            column_def = f"{field_name} {field_type}"
            if field_name == primary_key:
                column_def += " PRIMARY KEY"
            columns.append(column_def)
        
        # Add auto-incrementing ID if no primary key specified
        if not primary_key and 'id' not in schema:
            if self.database_type == DatabaseType.POSTGRESQL:
                columns.insert(0, "id SERIAL PRIMARY KEY")
            elif self.database_type == DatabaseType.MYSQL:
                columns.insert(0, "id INT AUTO_INCREMENT PRIMARY KEY")
            elif self.database_type == DatabaseType.SQLITE:
                columns.insert(0, "id INTEGER PRIMARY KEY AUTOINCREMENT")
        
        columns_sql = ",\n    ".join(columns)
        return f"CREATE TABLE IF NOT EXISTS {table_name} (\n    {columns_sql}\n)"
