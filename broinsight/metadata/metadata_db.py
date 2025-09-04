import duckdb
import yaml
import json
import uuid
import pandas as pd
from pathlib import Path
from typing import Optional, List

class DuckConnector:
    def __init__(self, data_db_path=":memory:", metadata_db_path="metadata.db"):
        self.data_db_path = data_db_path
        self.metadata_db_path = metadata_db_path
        self.data_conn = duckdb.connect(data_db_path)
        self._registered_tables = {}  # Track registered DataFrames
        self._init_metadata_schema()
    
    def _execute_metadata(self, sql: str, params: list = None):
        """Execute SQL on metadata database with context manager"""
        with duckdb.connect(self.metadata_db_path) as conn:
            if params:
                result = conn.execute(sql, params)
            else:
                result = conn.execute(sql)
            
            # Fetch results before connection closes
            if sql.strip().upper().startswith('SELECT'):
                return result.fetchall()
            else:
                return result
    
    def _execute_data(self, sql: str, params: list = None):
        """Execute SQL on data database with context manager"""
        with duckdb.connect(self.data_db_path) as conn:
            if params:
                return conn.execute(sql, params)
            else:
                return conn.execute(sql)

    def _init_metadata_schema(self):
        """Create metadata table if not exists"""
        self._execute_metadata("""
            CREATE TABLE IF NOT EXISTS metadata_tables (
                table_id VARCHAR PRIMARY KEY,
                table_name VARCHAR UNIQUE,
                description TEXT,
                detail JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def execute_query(self, sql: str) -> pd.DataFrame:
        """Execute query on data connection and return DataFrame"""
        with duckdb.connect(self.data_db_path) as conn:
            # Re-register all tables that were registered before
            if hasattr(self, '_registered_tables'):
                for table_name, df in self._registered_tables.items():
                    conn.register(table_name, df)
            return conn.execute(sql).fetch_df()
    
    def register_dataframe(self, df: pd.DataFrame, table_name: str):
        """Register DataFrame as table in data connection"""
        # Keep track of registered tables for re-registration
        if not hasattr(self, '_registered_tables'):
            self._registered_tables = {}
        self._registered_tables[table_name] = df
        
        # Register in current connection
        self.data_conn.register(table_name, df)
    
    def register_metadata_from_yaml(self, yaml_dir: str):
        """Convert YAML metadata files to database records"""
        yaml_path = Path(yaml_dir)
        for yaml_file in yaml_path.glob("*.yaml"):
            with open(yaml_file, 'r') as f:
                metadata = yaml.safe_load(f)
            
            table_name = metadata['table_name']
            description = metadata['description']
            
            # Everything else goes to detail JSON
            detail = {
                'fields': metadata['fields']
            }
            
            # Check if table exists
            existing = self._execute_metadata(
                "SELECT table_id FROM metadata_tables WHERE table_name = ?", 
                [table_name]
            )
            
            if existing:
                # Update existing record
                self._execute_metadata("""
                    UPDATE metadata_tables 
                    SET description = ?, detail = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE table_name = ?
                """, [description, json.dumps(detail), table_name])
            else:
                # Insert new record
                table_id = str(uuid.uuid4())
                self._execute_metadata("""
                    INSERT INTO metadata_tables 
                    (table_id, table_name, description, detail)
                    VALUES (?, ?, ?, ?)
                """, [table_id, table_name, description, json.dumps(detail)])
    
    def get_metadata_summary(self) -> str:
        """Get summary of all tables - same interface as MetadataLoader"""
        result = self._execute_metadata("""
            SELECT table_name, description 
            FROM metadata_tables
        """)
        
        return "\n".join([f"Table: {row[0]} - Description: {row[1]}" for row in result])
    
    def get_metadata_context(self, selected_tables: Optional[List[str]] = None) -> str:
        """Get detailed metadata context - same interface as MetadataLoader"""
        if selected_tables:
            placeholders = ",".join(["?" for _ in selected_tables])
            query = f"""
                SELECT table_name, description, detail 
                FROM metadata_tables 
                WHERE table_name IN ({placeholders})
            """
            result = self._execute_metadata(query, selected_tables)
        else:
            result = self._execute_metadata("""
                SELECT table_name, description, detail 
                FROM metadata_tables
            """)
        
        # Format same as current MetadataLoader
        context_parts = []
        for row in result:
            table_name, description, detail_json = row
            detail = json.loads(detail_json)
            formatted = self._format_table_metadata(table_name, description, detail['fields'])
            context_parts.append(formatted)
        
        return "\n\n".join(context_parts)
    
    def construct_prompt_context(self, selected_tables: Optional[List[str]] = None) -> str:
        """Alias for get_metadata_context to match MetadataLoader interface"""
        return self.get_metadata_context(selected_tables)
    
    def get_summary_prompt(self) -> str:
        """Alias for get_metadata_summary to match MetadataLoader interface"""
        return self.get_metadata_summary()
    
    def _format_table_metadata(self, table_name: str, description: str, fields: dict) -> str:
        """Format single table metadata for prompt - same as MetadataLoader"""
        lines = [
            f"TABLE: {table_name}",
            f"DESCRIPTION: {description}",
            "FIELDS:"
        ]
        
        for field_name, field_info in fields.items():
            field_line = f"  - {field_name} ({field_info['data_type']})"
            if field_info.get('description'):
                field_line += f": {field_info['description']}"
            
            # Add unique values for categorical fields
            if 'unique_values' in field_info:
                values = list(field_info['unique_values'].keys())[:5]  # Show first 5
                field_line += f" [Values: {', '.join(map(str, values))}]"
            
            lines.append(field_line)
        
        return "\n".join(lines)
    
    def list_tables(self) -> List[str]:
        """List all registered metadata tables"""
        result = self._execute_metadata("SELECT table_name FROM metadata_tables")
        return [row[0] for row in result]
    
    def debug_info(self):
        """Debug information about the database"""
        print(f"Metadata DB path: {self._execute_metadata('PRAGMA database_list')}")
        print(f"Tables in metadata DB: {self._execute_metadata('SHOW TABLES')}")
        count_result = self._execute_metadata('SELECT COUNT(*) FROM metadata_tables')
        print(f"Row count: {count_result[0][0] if count_result else 0}")
        
        import os
        print(f"Current directory: {os.getcwd()}")
        print(f"metadata.db exists: {os.path.exists('metadata.db')}")
        if os.path.exists('metadata.db'):
            print(f"metadata.db size: {os.path.getsize('metadata.db')} bytes")
    
    def close(self):
        """Close data connection (metadata uses context manager)"""
        self.data_conn.close()