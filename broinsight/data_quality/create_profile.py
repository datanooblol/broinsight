import pandas as pd
from .field_profile import field_profile
from .criteria import assess_data_quality
from .table_profile import table_profile


def create_profile(df: pd.DataFrame, top_n: int = 5) -> dict:
    """Create a comprehensive data profile combining table and field statistics with quality assessment.
    
    Args:
        df (pd.DataFrame): DataFrame to profile.
        top_n (int, optional): Number of most frequent values to include. Defaults to 5.
        
    Returns:
        dict: Combined profile with dataset summary and field details.
    """
    # Get table-level profile
    table_info = table_profile(df)
    
    # Get field profiles
    field_profiles = field_profile(df, top_n=top_n)
    
    # Get quality assessments
    quality_assessments = assess_data_quality(field_profiles)
    
    # Create dataset summary
    dataset_summary = {
        "rows": table_info["rows"],
        "columns": table_info["columns"],
        "duplicates": table_info["duplicates"]
    }
    
    # Add duplicate examples if they exist
    if table_info["duplicates"] > 0 and "evidences" in table_info:
        dataset_summary["duplicate_examples"] = table_info["evidences"]
    
    # Combine field profiles with quality assessments
    fields = {}
    for field_name in field_profiles.keys():
        fields[field_name] = {
            "profile": field_profiles[field_name],
            "quality": quality_assessments[field_name]["summary"]
        }
    
    return {
        "dataset_summary": dataset_summary,
        "fields": fields
    }


def format_profile(profile_dict: dict) -> str:
    """Format the profile dictionary into a readable string format.
    
    Args:
        profile_dict (dict): Profile dictionary from create_profile function.
        
    Returns:
        str: Formatted string representation of the profile.
    """
    lines = []
    
    # Dataset summary section
    dataset = profile_dict["dataset_summary"]
    lines.append("# Dataset Overview")
    lines.append(f"**Size:** {dataset['rows']} rows × {dataset['columns']} columns")
    
    if dataset["duplicates"] > 0:
        lines.append(f"**Duplicates:** {dataset['duplicates']} duplicate record(s) found")
        if "duplicate_examples" in dataset:
            example_rows = list(dataset["duplicate_examples"].keys())[:2]
            lines.append(f"**Examples:** Rows {', '.join(map(str, example_rows))} are identical")
    else:
        lines.append("**Duplicates:** No duplicate records found")
    
    lines.append("")
    lines.append("# Fields")
    
    # Field details section
    for field_name, field_data in profile_dict["fields"].items():
        lines.append(f"## {field_name}")
        
        # Profile section
        profile = field_data["profile"]
        lines.append(f"**Type:** {profile['data_types']}")
        lines.append(f"**Missing:** {profile['missing_values']} ({profile['missing_values_pct']:.1%})")
        lines.append(f"**Unique:** {profile['unique_values']} ({profile['unique_values_pct']:.1%})")
        
        # Quality section
        quality = field_data["quality"]
        lines.append(f"**Quality:** {quality['quality']}")
        
        if quality["issues"]:
            lines.append("**Issues:**")
            for issue in quality["issues"]:
                lines.append(f"  - {issue['description']} ({issue['severity']})")
        
        # Statistics (condensed)
        stats = profile.get("statistics", {})
        if stats:
            if profile["data_types"] in ["integer", "float"]:
                lines.append(f"**Stats:** min={stats.get('min')}, max={stats.get('max')}, mean={stats.get('mean')}, skew={stats.get('skew')}")
            else:
                lines.append(f"**Stats:** mode={stats.get('mode')}, avg_length={stats.get('avg_length')}")
        
        lines.append("")  # Empty line between fields
    
    return "\n".join(lines)