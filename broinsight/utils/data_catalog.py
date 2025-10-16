import duckdb
import pandas as pd
from typing import Dict, List, Optional, Union
from broinsight.data_quality.sql_profile import sql_table_profile, sql_field_profile
# from broinsight.data_quality.criteria import assess_data_quality
# from broinsight.data_quality.create_profile import format_profile
from broinsight.utils.data_spec import Metadata, TableSpec, create_field_specs_from_profile, create_data_quality_assessment
from broinsight.experiment.bedrock import AWSConfig

class DataCatalog:
    def __init__(self, aws_configs:Optional[AWSConfig]=None):
        self._conn = duckdb.connect()
        self._tables = {}
        self._relationships = []  # Store table relationships
        if aws_configs:
            self._setup_s3(**self._validate_config(aws_configs))

    def _validate_config(self, aws_configs):
        """Validate and convert AWSConfig to dictionary"""
        if isinstance(aws_configs, AWSConfig):
            return aws_configs.model_dump()
        elif isinstance(aws_configs, dict):
            # Validate dict has required fields
            AWSConfig(**aws_configs)  # This will raise ValidationError if invalid
            return aws_configs
        else:
            raise TypeError("aws_configs must be AWSConfig instance or dict")

    def _setup_s3(self, aws_access_key_id=None, aws_secret_access_key=None, region_name='ap-southeast-1', aws_session_token=None):
        """Setup S3 connection using your existing logic"""

        self._conn.execute("INSTALL httpfs")
        self._conn.execute("LOAD httpfs")
        
        if aws_access_key_id and aws_secret_access_key:
            secret_sql = f"""
            CREATE OR REPLACE SECRET s3_secret (
                TYPE s3,
                PROVIDER config,
                KEY_ID '{aws_access_key_id}',
                SECRET '{aws_secret_access_key}',
                REGION '{region_name}'"""
            if aws_session_token:
                secret_sql += f",\n                SESSION_TOKEN '{aws_session_token}'"
            secret_sql += "\n            )"
            self._conn.execute(secret_sql)
        else:
            self._conn.execute("""
            CREATE OR REPLACE SECRET s3_secret (
                TYPE s3,
                PROVIDER credential_chain
            )""")
    
    def create_table(self, name: str, source, table_description: str = '', metadata=None):
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
            'table_description': table_description,
            'metadata': metadata
        }
    
    def register(self, name: str, source, table_description: str = '', metadata=None):
        self.create_table(name, source, table_description, metadata)
        
    def query(self, sql: str):
        return self._conn.execute(sql).df()
    
    def list_tables(self) -> List[str]:
        return list(self._tables.keys())
    
    def profile_tables(self, tables: List[str]):
        """Generate complete Metadata objects for specified tables"""
        
        for table_name in tables:
            if table_name not in self._tables:
                raise ValueError(f"Table '{table_name}' not found")
            
            # Get raw profiles
            table_profile = sql_table_profile(self._conn, table_name)
            field_profile = sql_field_profile(self._conn, table_name)
            
            # Create Metadata object
            metadata = Metadata(
                table_name=table_name,
                table_description=self._tables[table_name].get('table_description', ''),
                table_spec=TableSpec(**table_profile),
                field_spec=create_field_specs_from_profile(field_profile),
                data_quality=create_data_quality_assessment(field_profile)
            )
            
            # Store in registry
            self._tables[table_name]['metadata'] = metadata
    
    def add_field_descriptions(self, table_name: str, field_descriptions):
        """Add field descriptions to a profiled table"""
        if table_name not in self._tables:
            raise ValueError(f"Table '{table_name}' not found")
        
        metadata = self._tables[table_name]['metadata']
        if metadata is None:
            raise ValueError(f"Table '{table_name}' not profiled. Run profile_tables() first.")
        
        # Use the existing method from Metadata class
        metadata.add_field_descriptions(field_descriptions)
    
    def to_dq_profile(self, table_name: str) -> str:
        """Format metadata as PROFILE for data quality assessment"""
        if table_name not in self._tables:
            raise ValueError(f"Table '{table_name}' not found")
        
        metadata = self._tables[table_name]['metadata']
        if metadata is None:
            raise ValueError(f"Table '{table_name}' not profiled. Run profile_tables() first.")
        
        if metadata.data_quality is None:
            raise ValueError(f"No data quality assessment found for '{table_name}'")
        
        # Dataset overview
        profile = f"""DATASET: {metadata.table_name}
DESCRIPTION: {metadata.table_description}
ROWS: {metadata.table_spec.rows:,}
COLUMNS: {metadata.table_spec.columns}
DUPLICATES: {metadata.table_spec.duplicates:,}
OVERALL QUALITY: {metadata.data_quality.overall_quality.upper()}
TOTAL ISSUES: {metadata.data_quality.total_issues}

"""
        
        # Field profiles
        profile += "FIELD PROFILES:\n"
        for field in metadata.field_spec:
            profile += f"\n{field.field_name} ({field.data_type}):\n"
            profile += f"  Missing: {field.missing_values:,} ({field.missing_values_pct:.1f}%)\n"
            profile += f"  Unique: {field.unique_values:,} ({field.unique_values_pct:.1f}%)\n"
            if field.description:
                profile += f"  Description: {field.description}\n"
        
        # Quality issues by severity
        critical_issues = []
        moderate_issues = []
        minor_issues = []
        
        for assessment in metadata.data_quality.field_assessments:
            for issue in assessment.issues:
                issue_text = f"{assessment.field_name}: {issue.description}"
                if issue.severity == "critical":
                    critical_issues.append(issue_text)
                elif issue.severity == "moderate":
                    moderate_issues.append(issue_text)
                else:
                    minor_issues.append(issue_text)
        
        if critical_issues:
            profile += "\nCRITICAL ISSUES:\n"
            for issue in critical_issues:
                profile += f"- {issue}\n"
        
        if moderate_issues:
            profile += "\nMODERATE ISSUES:\n"
            for issue in moderate_issues:
                profile += f"- {issue}\n"
        
        if minor_issues:
            profile += "\nMINOR ISSUES:\n"
            for issue in minor_issues:
                profile += f"- {issue}\n"
        
        return profile
    
    def get_metadata(self, table_name: str):
        """Get metadata object for a table"""
        if table_name not in self._tables:
            raise ValueError(f"Table '{table_name}' not found")
        return self._tables[table_name].get('metadata')
    
    def to_guide_metadata(self, table_names: Union[str, List[str]]) -> str:
        """Format metadata for question guidance - handles single or multiple tables"""
        if isinstance(table_names, str):
            table_names = [table_names]
        
        # Validate all tables exist and are profiled
        for table_name in table_names:
            if table_name not in self._tables:
                raise ValueError(f"Table '{table_name}' not found")
            metadata = self._tables[table_name]['metadata']
            if metadata is None:
                raise ValueError(f"Table '{table_name}' not profiled. Run profile_tables() first.")
        
        # Format metadata
        result = "METADATA:\n\n"
        
        for table_name in table_names:
            metadata = self._tables[table_name]['metadata']
            result += f"Table: {metadata.table_name}"
            if metadata.table_description:
                result += f" ({metadata.table_description})"
            result += "\nFields:\n"
            
            for field in metadata.field_spec:
                result += f"- {field.field_name} ({field.data_type})"
                if field.description:
                    result += f": {field.description}"
                result += "\n"
                
                # Add statistics for context
                if field.data_type in ['float', 'integer'] and field.statistics:
                    stats = field.statistics
                    if 'min' in stats and 'max' in stats:
                        result += f"  Range: {stats['min']} - {stats['max']}"
                        if 'mean' in stats:
                            result += f", Average: {stats['mean']:.2f}"
                        result += "\n"
                elif field.data_type == 'string' and field.most_frequent:
                    # Show top values for categorical fields
                    top_values = list(field.most_frequent.items())[:3]
                    values_str = ", ".join([f"{k} ({v})" for k, v in top_values])
                    result += f"  Values: {values_str}\n"
            
            result += "\n"
        
        return result.strip()
    
    def add_relationship(self, 
                       foreign_table: str, 
                       foreign_key: str, 
                       primary_table: str, 
                       primary_key: str):
        """
        Connect two tables for SQL joins.
        
        Args:
            foreign_table: Table that has the foreign key (child table)
            foreign_key: Column in foreign_table that references primary_table
            primary_table: Table being referenced (parent table)  
            primary_key: Column in primary_table (usually the primary key)
        
        Example:
            # Connect orders to customers
            catalog.add_relationship("orders", "customer_id", "customers", "customer_id")
        """
        # Validate tables exist
        if foreign_table not in self._tables:
            raise ValueError(f"Foreign table '{foreign_table}' not found")
        if primary_table not in self._tables:
            raise ValueError(f"Primary table '{primary_table}' not found")
        
        self._relationships.append((foreign_table, foreign_key, primary_table, primary_key))
    
    def get_table_relationships(self, table_name: str) -> List[tuple]:
        """Get all relationships for a specific table"""
        return [r for r in self._relationships if r[0] == table_name]
    
    def to_sql_metadata(self, table_names: Union[str, List[str]]) -> str:
        """Format metadata for SQL generation - handles single or multiple tables"""
        if isinstance(table_names, str):
            table_names = [table_names]
        
        # Validate all tables exist and are profiled
        for table_name in table_names:
            if table_name not in self._tables:
                raise ValueError(f"Table '{table_name}' not found")
            metadata = self._tables[table_name]['metadata']
            if metadata is None:
                raise ValueError(f"Table '{table_name}' not profiled. Run profile_tables() first.")
        
        # Format metadata
        result = "METADATAS:\n\n"
        
        for table_name in table_names:
            metadata = self._tables[table_name]['metadata']
            result += f"Table: {metadata.table_name}\n"
            
            # Add relationships if any
            relationships = self.get_table_relationships(table_name)
            if relationships:
                result += "Relationships:\n"
                for rel in relationships:
                    result += f"  {rel[1]} -> {rel[2]}.{rel[3]}\n"
            
            result += "Columns:\n"
            for field in metadata.field_spec:
                # Column name and type
                result += f"- {field.field_name} ({field.data_type})"
                
                # Add description if available
                if field.description:
                    result += f": {field.description}"
                
                # Add nullability info
                if field.missing_values_pct == 0:
                    result += ", NOT NULL"
                elif field.missing_values_pct > 0:
                    result += f", {field.missing_values_pct:.1f}% NULL"
                
                result += "\n"
                
                # Add value examples and ranges
                if field.data_type in ['float', 'integer'] and field.statistics:
                    stats = field.statistics
                    if 'min' in stats and 'max' in stats:
                        result += f"  Range: {stats['min']} - {stats['max']}"
                        if 'mean' in stats:
                            result += f", Average: {stats['mean']:.2f}"
                        result += "\n"
                elif field.data_type == 'string' and field.most_frequent:
                    # Show example values for categorical fields
                    top_values = list(field.most_frequent.keys())[:3]
                    values_str = '", "'.join(map(str, top_values))
                    result += f"  Examples: \"{values_str}\"\n"
            
            result += "\n"
        
        return result.strip()