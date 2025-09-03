import yaml
from pathlib import Path

class MetadataLoader:
    def __init__(self, metadata_dir="metadata"):
        self.metadata_dir = Path(metadata_dir)
    
    def load_all_metadata(self):
        """Load all YAML metadata files from the directory"""
        metadata_files = {}
        for yaml_file in self.metadata_dir.glob("*.yaml"):
            with open(yaml_file, 'r') as f:
                metadata_files[yaml_file.stem] = yaml.safe_load(f)
        return metadata_files
    
    def construct_prompt_context(self, selected_tables=None):
        """Construct formatted context for LLM prompts"""
        all_metadata = self.load_all_metadata()
        
        # Use selected tables or all tables
        tables_to_use = selected_tables or list(all_metadata.keys())
        
        context_parts = []
        for table_name in tables_to_use:
            if table_name in all_metadata:
                metadata = all_metadata[table_name]
                context_parts.append(self._format_table_metadata(metadata))
        
        return "\n\n".join(context_parts)
    
    def get_metadata_dict(self):
        """Get metadata as dictionary with table names as keys"""
        all_metadata = self.load_all_metadata()
        return {metadata['table_name']: metadata for metadata in all_metadata.values()}
    
    def get_summary_prompt(self):
        """Create short summary with table names and descriptions only"""
        metadata_dict = self.get_metadata_dict()
        return "\n".join([f"Table: {table} - Description: {data['description']}" for table, data in metadata_dict.items()])
    
    def _format_table_metadata(self, metadata):
        """Format single table metadata for prompt"""
        lines = [
            f"TABLE: {metadata['table_name']}",
            f"DESCRIPTION: {metadata['description']}",
            "FIELDS:"
        ]
        
        for field_name, field_info in metadata['fields'].items():
            field_line = f"  - {field_name} ({field_info['data_type']})"
            if field_info['description']:
                field_line += f": {field_info['description']}"
            
            # Add unique values for categorical fields
            if 'unique_values' in field_info:
                values = list(field_info['unique_values'].keys())[:5]  # Show first 5
                field_line += f" [Values: {', '.join(map(str, values))}]"
            
            lines.append(field_line)
        
        return "\n".join(lines)