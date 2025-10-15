import duckdb
import pandas as pd
from typing import Dict, List, Optional, Union
from broinsight.data_quality.sql_profile import sql_table_profile, sql_field_profile
from broinsight.data_quality.criteria import assess_data_quality
from broinsight.data_quality.create_profile import format_profile


class DataQualityFormatter:
    """Formats data quality profiles for LLM consumption"""
    
    @staticmethod
    def format_for_llm(table_profile: Dict, field_profile: Dict) -> str:
        """Format profiles into LLM-ready string"""
        # Assess data quality
        dq_summary = assess_data_quality(field_profile)
        
        # Create combined profile structure
        profile = {
            'dataset_summary': table_profile,
            'fields': {
                k: {
                    'profile': v, 
                    'quality': dq_summary[k]['summary']
                } for k, v in field_profile.items()
            }
        }
        
        # Format for LLM
        return format_profile(profile)

class DataCatalog:
    def __init__(self, s3_config=None):
        self._conn = duckdb.connect()
        self._tables = {}
        if s3_config:
            self._setup_s3(**s3_config)
    
    def _setup_s3(self, key_id=None, secret=None, region='ap-southeast-1', session_token=None, endpoint=None):
        """Setup S3 connection using your existing logic"""
        self._conn.execute("INSTALL httpfs")
        self._conn.execute("LOAD httpfs")
        
        if key_id and secret:
            secret_sql = f"""
            CREATE OR REPLACE SECRET s3_secret (
                TYPE s3,
                PROVIDER config,
                KEY_ID '{key_id}',
                SECRET '{secret}',
                REGION '{region}'"""
            if session_token:
                secret_sql += f",\n                SESSION_TOKEN '{session_token}'"
            if endpoint:
                secret_sql += f",\n                ENDPOINT '{endpoint}'"
            secret_sql += "\n            )"
            self._conn.execute(secret_sql)
        else:
            self._conn.execute("""
            CREATE OR REPLACE SECRET s3_secret (
                TYPE s3,
                PROVIDER credential_chain
            )""")
    
    def create_table(self, name: str, source, metadata=None):
        """Universal table creation method"""
        if isinstance(source, pd.DataFrame):
            # Pandas DataFrame
            self._conn.register(name, source)
            source_type = 'pandas'
            source_path = None
        
        elif isinstance(source, str):
            # File path (local or S3)
            if source.startswith('s3://'):
                if source.endswith('.parquet'):
                    self._conn.execute(f"CREATE TABLE {name} AS SELECT * FROM read_parquet('{source}')")
                    source_type = 's3_parquet'
                else:
                    self._conn.execute(f"CREATE TABLE {name} AS SELECT * FROM read_csv_auto('{source}')")
                    source_type = 's3_csv'
            else:
                # Local file
                self._conn.execute(f"CREATE TABLE {name} AS SELECT * FROM read_csv_auto('{source}')")
                source_type = 'local_csv'
            source_path = source
        
        else:
            raise ValueError(f"Unsupported source type: {type(source)}")
        
        self._tables[name] = {
            'type': source_type, 
            'path': source_path, 
            'metadata': metadata
        }
    
    def query(self, sql: str):
        return self._conn.execute(sql).df()
    
    def list_tables(self) -> List[str]:
        return list(self._tables.keys())
    
    def get_table_profile(self, table_name: str) -> Dict:
        """Get table-level data quality profile"""
        if table_name not in self._tables:
            raise ValueError(f"Table '{table_name}' not found")
        return sql_table_profile(self._conn, table_name)
    
    def get_field_profile(self, table_name: str, top_n: int = 5) -> Dict:
        """Get field-level data quality profile"""
        if table_name not in self._tables:
            raise ValueError(f"Table '{table_name}' not found")
        return sql_field_profile(self._conn, table_name, top_n)
    
    def get_all_profiles(self) -> Dict:
        """Get comprehensive profiles for all tables"""
        profiles = {}
        for table_name in self.list_tables():
            profiles[table_name] = {
                'table_profile': self.get_table_profile(table_name),
                'field_profile': self.get_field_profile(table_name)
            }
        return profiles
    
    def get_metadata(self, table_name: str) -> Optional[Dict]:
        """Get metadata for a specific table"""
        if table_name not in self._tables:
            raise ValueError(f"Table '{table_name}' not found")
        return self._tables[table_name].get('metadata')
    
    def get_formatted_profile(self, table_name: str) -> str:
        """Get LLM-ready formatted profile for a table"""
        if table_name not in self._tables:
            raise ValueError(f"Table '{table_name}' not found")
        
        table_profile = self.get_table_profile(table_name)
        field_profile = self.get_field_profile(table_name)
        
        return DataQualityFormatter.format_for_llm(table_profile, field_profile)
    
    @classmethod
    def from_pandas(cls, dataframes: Dict[str, pd.DataFrame], s3_config=None):
        """Factory method to create DataCatalog from pandas DataFrames"""
        catalog = cls(s3_config=s3_config)
        for name, df in dataframes.items():
            catalog.create_table(name, df)
        return catalog
