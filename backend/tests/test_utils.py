"""
Test utilities for SQLite compatibility
"""
from sqlalchemy import TypeDecorator, String
from sqlalchemy.dialects.postgresql import ARRAY
import json


class JSONList(TypeDecorator):
    """Convert PostgreSQL ARRAY to JSON string for SQLite compatibility"""
    impl = String
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'sqlite':
            return dialect.type_descriptor(String)
        else:
            return dialect.type_descriptor(ARRAY(String))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'sqlite':
            return json.dumps(value) if isinstance(value, list) else value
        return value
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'sqlite':
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except (TypeError, ValueError):
                    return value
        return value

