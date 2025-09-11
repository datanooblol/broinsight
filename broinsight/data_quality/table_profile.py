import pandas as pd

def table_profile(df: pd.DataFrame):
    """Generate dataset-level data quality profile.
    
    Analyzes overall dataset characteristics including dimensions,
    duplicate detection, and provides evidence of data quality issues.
    
    Args:
        df (pd.DataFrame): DataFrame to profile.
        
    Returns:
        dict: Dictionary containing:
            - rows: Number of rows in the dataset
            - columns: Number of columns in the dataset
            - duplicates: Count of duplicate rows
            - evidences: Dictionary of actual duplicate rows (indexed by row number)
                        for manual inspection and validation
    """
    rows, columns = df.shape
    duplicated = df.duplicated()
    duplicates = int(duplicated.sum())
    evidences = df.loc[df.duplicated(keep=False),:].to_dict(orient="index")
    return {
        "rows": rows,
        "columns": columns,
        "duplicates": duplicates,
        "evidences": evidences
    }
