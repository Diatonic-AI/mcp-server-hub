import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Tuple
from urllib.parse import urlparse
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR

from .data_transformer import DatabaseType, DataTransformer

logger = logging.getLogger(__name__)


class DatabaseConnection(ABC):
    """Abstract base class for database connections."""
    
    def __init__(self, connection_string: str, connection_timeout: int = 30):
        self.connection_string = connection_string
        self.connection_timeout = connection_timeout
        self.database_type = self._determine_database_type(connection_string)
        self.transformer = DataTransformer(self.database_type)
        self._connection = None
    
    def _determine_database_type(self, connection_string: str) -> DatabaseType:
        """Determine database type from connection string."""
        parsed = urlparse(connection_string)
        scheme = parsed.scheme.lower()
        
        if scheme.startswith('postgresql') or scheme.startswith('postgres'):
            return DatabaseType.POSTGRESQL
        elif scheme.startswith('mysql'):
            return DatabaseType.MYSQL
        elif scheme.startswith('sqlite'):
            return DatabaseType.SQLITE
        elif scheme.startswith('mongodb'):
            return DatabaseType.MONGODB
        elif scheme.startswith('redis'):
            return DatabaseType.REDIS
        else:
            raise ValueError(f"Unsupported database scheme: {scheme}")
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish database connection."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if connection is alive."""
        pass
    
    @abstractmethod
    async def create_table_or_collection(self, name: str, schema: Dict[str, str]) -> None:
        """Create table or collection with given schema."""
        pass
    
    @abstractmethod
    async def insert_records(self, table_name: str, records: List[Dict[str, Any]], 
                           batch_size: int = 100) -> int:
        """Insert records into database."""
        pass
    
    @abstractmethod
    async def get_schema(self, table_name: str) -> Optional[Dict[str, str]]:
        """Get schema for table/collection."""
        pass
    
    @abstractmethod
    async def table_exists(self, table_name: str) -> bool:
        """Check if table/collection exists."""
        pass


class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL database connection handler."""
    
    async def connect(self) -> None:
        """Establish PostgreSQL connection using asyncpg."""
        try:
            import asyncpg
            self._connection = await asyncio.wait_for(
                asyncpg.connect(self.connection_string),
                timeout=self.connection_timeout
            )
        except Exception as e:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to connect to PostgreSQL: {str(e)}"
            ))
    
    async def disconnect(self) -> None:
        """Close PostgreSQL connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
    
    async def test_connection(self) -> bool:
        """Test PostgreSQL connection."""
        if not self._connection:
            return False
        try:
            await self._connection.fetchval("SELECT 1")
            return True
        except Exception:
            return False
    
    async def create_table_or_collection(self, name: str, schema: Dict[str, str]) -> None:
        """Create PostgreSQL table."""
        create_sql = self.transformer.get_create_table_sql(name, schema)
        try:
            await self._connection.execute(create_sql)
        except Exception as e:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to create table {name}: {str(e)}"
            ))
    
    async def insert_records(self, table_name: str, records: List[Dict[str, Any]], 
                           batch_size: int = 100) -> int:
        """Insert records into PostgreSQL table."""
        if not records:
            return 0
        
        inserted_count = 0
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            # Get column names from first record
            columns = list(batch[0].keys())
            placeholders = ', '.join([f'${j+1}' for j in range(len(columns))])
            column_names = ', '.join(columns)
            
            sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
            
            try:
                # Execute batch insert
                batch_values = [[record.get(col) for col in columns] for record in batch]
                await self._connection.executemany(sql, batch_values)
                inserted_count += len(batch)
            except Exception as e:
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Failed to insert batch into {table_name}: {str(e)}"
                ))
        
        return inserted_count
    
    async def get_schema(self, table_name: str) -> Optional[Dict[str, str]]:
        """Get PostgreSQL table schema."""
        sql = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = $1
        ORDER BY ordinal_position
        """
        try:
            rows = await self._connection.fetch(sql, table_name)
            if not rows:
                return None
            return {row['column_name']: row['data_type'] for row in rows}
        except Exception:
            return None
    
    async def table_exists(self, table_name: str) -> bool:
        """Check if PostgreSQL table exists."""
        sql = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = $1
        )
        """
        try:
            result = await self._connection.fetchval(sql, table_name)
            return bool(result)
        except Exception:
            return False


class SQLiteConnection(DatabaseConnection):
    """SQLite database connection handler."""
    
    async def connect(self) -> None:
        """Establish SQLite connection using aiosqlite."""
        try:
            import aiosqlite
            # Extract database path from connection string
            parsed = urlparse(self.connection_string)
            db_path = parsed.path or parsed.netloc
            self._connection = await aiosqlite.connect(db_path)
        except Exception as e:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to connect to SQLite: {str(e)}"
            ))
    
    async def disconnect(self) -> None:
        """Close SQLite connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
    
    async def test_connection(self) -> bool:
        """Test SQLite connection."""
        if not self._connection:
            return False
        try:
            await self._connection.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    async def create_table_or_collection(self, name: str, schema: Dict[str, str]) -> None:
        """Create SQLite table."""
        create_sql = self.transformer.get_create_table_sql(name, schema)
        try:
            await self._connection.execute(create_sql)
            await self._connection.commit()
        except Exception as e:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to create table {name}: {str(e)}"
            ))
    
    async def insert_records(self, table_name: str, records: List[Dict[str, Any]], 
                           batch_size: int = 100) -> int:
        """Insert records into SQLite table."""
        if not records:
            return 0
        
        inserted_count = 0
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            # Get column names from first record
            columns = list(batch[0].keys())
            placeholders = ', '.join(['?' for _ in columns])
            column_names = ', '.join(columns)
            
            sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
            
            try:
                # Execute batch insert
                batch_values = [[record.get(col) for col in columns] for record in batch]
                await self._connection.executemany(sql, batch_values)
                await self._connection.commit()
                inserted_count += len(batch)
            except Exception as e:
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Failed to insert batch into {table_name}: {str(e)}"
                ))
        
        return inserted_count
    
    async def get_schema(self, table_name: str) -> Optional[Dict[str, str]]:
        """Get SQLite table schema."""
        sql = f"PRAGMA table_info({table_name})"
        try:
            cursor = await self._connection.execute(sql)
            rows = await cursor.fetchall()
            if not rows:
                return None
            return {row[1]: row[2] for row in rows}  # name, type columns
        except Exception:
            return None
    
    async def table_exists(self, table_name: str) -> bool:
        """Check if SQLite table exists."""
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        try:
            cursor = await self._connection.execute(sql, (table_name,))
            result = await cursor.fetchone()
            return result is not None
        except Exception:
            return False


class MongoDBConnection(DatabaseConnection):
    """MongoDB database connection handler."""
    
    async def connect(self) -> None:
        """Establish MongoDB connection using motor."""
        try:
            import motor.motor_asyncio
            self._client = motor.motor_asyncio.AsyncIOMotorClient(
                self.connection_string,
                serverSelectionTimeoutMS=self.connection_timeout * 1000
            )
            # Test connection
            await self._client.admin.command('ping')
            
            # Extract database name from connection string
            parsed = urlparse(self.connection_string)
            db_name = parsed.path.lstrip('/') if parsed.path else 'default'
            self._connection = self._client[db_name]
        except Exception as e:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to connect to MongoDB: {str(e)}"
            ))
    
    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if hasattr(self, '_client') and self._client:
            self._client.close()
            self._client = None
            self._connection = None
    
    async def test_connection(self) -> bool:
        """Test MongoDB connection."""
        if not self._connection:
            return False
        try:
            await self._client.admin.command('ping')
            return True
        except Exception:
            return False
    
    async def create_table_or_collection(self, name: str, schema: Dict[str, str]) -> None:
        """Create MongoDB collection."""
        try:
            # MongoDB creates collections automatically, but we can create it explicitly
            collection = self._connection[name]
            await collection.create_index("_id")  # Ensure default index exists
        except Exception as e:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to create collection {name}: {str(e)}"
            ))
    
    async def insert_records(self, table_name: str, records: List[Dict[str, Any]], 
                           batch_size: int = 100) -> int:
        """Insert records into MongoDB collection."""
        if not records:
            return 0
        
        collection = self._connection[table_name]
        inserted_count = 0
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            try:
                result = await collection.insert_many(batch)
                inserted_count += len(result.inserted_ids)
            except Exception as e:
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Failed to insert batch into {table_name}: {str(e)}"
                ))
        
        return inserted_count
    
    async def get_schema(self, table_name: str) -> Optional[Dict[str, str]]:
        """Get MongoDB collection schema by sampling documents."""
        try:
            collection = self._connection[table_name]
            # Sample a few documents to infer schema
            pipeline = [{"$sample": {"size": 100}}, {"$limit": 10}]
            documents = await collection.aggregate(pipeline).to_list(length=10)
            
            if not documents:
                return None
            
            # Infer schema from sample documents
            schema = {}
            for doc in documents:
                for key, value in doc.items():
                    if key not in schema:
                        schema[key] = self.transformer.infer_field_type(value)
            
            return schema
        except Exception:
            return None
    
    async def table_exists(self, table_name: str) -> bool:
        """Check if MongoDB collection exists."""
        try:
            collections = await self._connection.list_collection_names()
            return table_name in collections
        except Exception:
            return False


class RedisConnection(DatabaseConnection):
    """Redis database connection handler."""
    
    async def connect(self) -> None:
        """Establish Redis connection."""
        try:
            import redis.asyncio as redis
            parsed = urlparse(self.connection_string)
            
            self._connection = redis.from_url(
                self.connection_string,
                socket_timeout=self.connection_timeout,
                socket_connect_timeout=self.connection_timeout,
                decode_responses=True
            )
            # Test connection
            await self._connection.ping()
        except Exception as e:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to connect to Redis: {str(e)}"
            ))
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._connection:
            await self._connection.aclose()
            self._connection = None
    
    async def test_connection(self) -> bool:
        """Test Redis connection."""
        if not self._connection:
            return False
        try:
            await self._connection.ping()
            return True
        except Exception:
            return False
    
    async def create_table_or_collection(self, name: str, schema: Dict[str, str]) -> None:
        """Create Redis key namespace (no-op, Redis is schemaless)."""
        # Redis doesn't require explicit table creation
        pass
    
    async def insert_records(self, table_name: str, records: List[Dict[str, Any]], 
                           batch_size: int = 100) -> int:
        """Insert records into Redis as hashes."""
        if not records:
            return 0
        
        inserted_count = 0
        
        for i, record in enumerate(records):
            try:
                # Use table_name as key prefix
                key = f"{table_name}:{i}"
                
                # Transform values for Redis storage
                redis_record = {}
                for k, v in record.items():
                    redis_record[k] = self.transformer.transform_value(v)
                
                # Store as hash
                await self._connection.hset(key, mapping=redis_record)
                inserted_count += 1
            except Exception as e:
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Failed to insert record {i} into {table_name}: {str(e)}"
                ))
        
        return inserted_count
    
    async def get_schema(self, table_name: str) -> Optional[Dict[str, str]]:
        """Get Redis key pattern schema by sampling."""
        try:
            # Get a few sample keys to infer schema
            pattern = f"{table_name}:*"
            keys = await self._connection.keys(pattern)
            
            if not keys:
                return None
            
            # Sample first key to get field structure
            sample_key = keys[0]
            fields = await self._connection.hgetall(sample_key)
            
            # All values in Redis are strings, but we can infer original types
            schema = {}
            for field_name, value in fields.items():
                schema[field_name] = 'string'  # Redis stores everything as strings
            
            return schema
        except Exception:
            return None
    
    async def table_exists(self, table_name: str) -> bool:
        """Check if Redis key pattern exists."""
        try:
            pattern = f"{table_name}:*"
            keys = await self._connection.keys(pattern)
            return len(keys) > 0
        except Exception:
            return False


class MySQLConnection(DatabaseConnection):
    """MySQL database connection handler."""
    
    async def connect(self) -> None:
        """Establish MySQL connection."""
        try:
            import aiomysql
            parsed = urlparse(self.connection_string)
            
            self._connection = await aiomysql.connect(
                host=parsed.hostname,
                port=parsed.port or 3306,
                user=parsed.username,
                password=parsed.password,
                db=parsed.path.lstrip('/') if parsed.path else 'mysql',
                connect_timeout=self.connection_timeout,
                autocommit=True
            )
        except Exception as e:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to connect to MySQL: {str(e)}"
            ))
    
    async def disconnect(self) -> None:
        """Close MySQL connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    async def test_connection(self) -> bool:
        """Test MySQL connection."""
        if not self._connection:
            return False
        try:
            cursor = await self._connection.cursor()
            await cursor.execute("SELECT 1")
            await cursor.close()
            return True
        except Exception:
            return False
    
    async def create_table_or_collection(self, name: str, schema: Dict[str, str]) -> None:
        """Create MySQL table."""
        create_sql = self.transformer.get_create_table_sql(name, schema)
        try:
            cursor = await self._connection.cursor()
            await cursor.execute(create_sql)
            await cursor.close()
        except Exception as e:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to create table {name}: {str(e)}"
            ))
    
    async def insert_records(self, table_name: str, records: List[Dict[str, Any]], 
                           batch_size: int = 100) -> int:
        """Insert records into MySQL table."""
        if not records:
            return 0
        
        inserted_count = 0
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            # Get column names from first record
            columns = list(batch[0].keys())
            placeholders = ', '.join(['%s' for _ in columns])
            column_names = ', '.join(columns)
            
            sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
            
            try:
                cursor = await self._connection.cursor()
                batch_values = [[record.get(col) for col in columns] for record in batch]
                await cursor.executemany(sql, batch_values)
                inserted_count += cursor.rowcount
                await cursor.close()
            except Exception as e:
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Failed to insert batch into {table_name}: {str(e)}"
                ))
        
        return inserted_count
    
    async def get_schema(self, table_name: str) -> Optional[Dict[str, str]]:
        """Get MySQL table schema."""
        sql = """
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
        """
        try:
            cursor = await self._connection.cursor()
            await cursor.execute(sql, (table_name,))
            rows = await cursor.fetchall()
            await cursor.close()
            
            if not rows:
                return None
            return {row[0]: row[1] for row in rows}
        except Exception:
            return None
    
    async def table_exists(self, table_name: str) -> bool:
        """Check if MySQL table exists."""
        sql = """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME = %s
        """
        try:
            cursor = await self._connection.cursor()
            await cursor.execute(sql, (table_name,))
            result = await cursor.fetchone()
            await cursor.close()
            return result is not None
        except Exception:
            return False


class DatabaseManager:
    """Factory and manager for database connections."""
    
    CONNECTION_CLASSES = {
        DatabaseType.POSTGRESQL: PostgreSQLConnection,
        DatabaseType.SQLITE: SQLiteConnection,
        DatabaseType.MONGODB: MongoDBConnection,
        DatabaseType.REDIS: RedisConnection,
        DatabaseType.MYSQL: MySQLConnection,
    }
    
    @classmethod
    def create_connection(cls, connection_string: str, 
                         connection_timeout: int = 30) -> DatabaseConnection:
        """Create appropriate database connection based on connection string."""
        # Determine database type from connection string
        parsed = urlparse(connection_string)
        scheme = parsed.scheme.lower()
        
        if scheme.startswith('postgresql') or scheme.startswith('postgres'):
            db_type = DatabaseType.POSTGRESQL
        elif scheme.startswith('mysql'):
            db_type = DatabaseType.MYSQL
        elif scheme.startswith('sqlite'):
            db_type = DatabaseType.SQLITE
        elif scheme.startswith('mongodb'):
            db_type = DatabaseType.MONGODB
        elif scheme.startswith('redis'):
            db_type = DatabaseType.REDIS
        else:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Unsupported database scheme: {scheme}"
            ))
        
        connection_class = cls.CONNECTION_CLASSES.get(db_type)
        if not connection_class:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"No connection handler for database type: {db_type.value}"
            ))
        
        return connection_class(connection_string, connection_timeout)
