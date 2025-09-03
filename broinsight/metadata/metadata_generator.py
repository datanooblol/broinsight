import pandas as pd
import yaml
from pathlib import Path

class DataFrameMetadataGenerator:
    def __init__(self, output_dir="metadata"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def _map_dtype_to_db_type(self, dtype):
        dtype_str = str(dtype)
        
        if 'int' in dtype_str:
            return 'INTEGER'
        elif 'float' in dtype_str:
            return 'DECIMAL'
        elif 'object' in dtype_str:
            return 'VARCHAR'
        elif 'datetime' in dtype_str:
            return 'TIMESTAMP'
        elif 'bool' in dtype_str:
            return 'BOOLEAN'
        else:
            return 'TEXT'
    
    def generate_metadata(self, df: pd.DataFrame, table_name: str, description: str = ""):
        metadata = {
            "table_name": table_name,
            "description": description,
            # "row_count": len(df),
            "fields": {}
        }
        
        for col in df.columns:
            field_info = {
                "data_type": self._map_dtype_to_db_type(df[col].dtype),
                "description": "",
                "null_count": int(df[col].isnull().sum())
            }
            
            # Categorical fields - show unique values
            if df[col].dtype == 'object' or df[col].nunique() <= 20:
                field_info["unique_values"] = df[col].value_counts().to_dict()
            
            # Numerical fields - show min, mean, max
            elif pd.api.types.is_numeric_dtype(df[col]):
                field_info["statistics"] = {
                    "min": float(df[col].min()),
                    "mean": float(df[col].mean()),
                    "max": float(df[col].max())
                }
            
            metadata["fields"][col] = field_info
        
        # Write to YAML file
        output_file = self.output_dir / f"{table_name}.yaml"
        with open(output_file, 'w') as f:
            yaml.dump(metadata, f, default_flow_style=False, indent=2)
        
        return output_file