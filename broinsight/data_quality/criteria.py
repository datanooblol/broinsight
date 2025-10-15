def assess_field_quality(field_name: str, field_data: dict) -> dict:
    """Assess data quality issues for a single field based on profiling data.
    
    Args:
        field_name (str): Name of the field being assessed.
        field_data (dict): Field profile data from field_profile function.
        
    Returns:
        dict: Assessment summary with issues categorized by severity.
    """
    issues = []
    data_type = field_data["data_types"]
    stats = field_data.get("statistics", {})
    
    # Missing values check (three-tier system)
    missing_pct = field_data["missing_values_pct"]
    if missing_pct > 0.2:
        issues.append({
            "type": "high_missing_values",
            "severity": "critical",
            "description": f"{missing_pct:.1%} missing values"
        })
    elif missing_pct > 0.05:
        issues.append({
            "type": "moderate_missing_values", 
            "severity": "moderate",
            "description": f"{missing_pct:.1%} missing values"
        })
    elif missing_pct > 0.01:
        issues.append({
            "type": "low_missing_values",
            "severity": "minor",
            "description": f"{missing_pct:.1%} missing values"
        })
    
    # Numeric data checks
    if data_type in ["integer", "float"]:
        skew = abs(stats.get("skew", 0))
        if skew > 2.0:
            issues.append({
                "type": "high_skewness",
                "severity": "moderate", 
                "description": f"Highly skewed distribution (skew: {skew:.2f})"
            })
        elif skew > 1.0:
            issues.append({
                "type": "moderate_skewness",
                "severity": "minor",
                "description": f"Moderately skewed distribution (skew: {skew:.2f})"
            })
    
    # String data checks
    elif data_type == "string":
        # Low cardinality check
        if field_data["unique_values"] < 2:
            issues.append({
                "type": "low_cardinality",
                "severity": "critical",
                "description": f"Only {field_data['unique_values']} unique value(s)"
            })
        
        # Empty/whitespace checks
        empty_count = stats.get("empty_count", 0)
        whitespace_count = stats.get("whitespace_count", 0)
        
        if empty_count > 0:
            issues.append({
                "type": "empty_strings",
                "severity": "moderate",
                "description": f"{empty_count} empty string values"
            })
        
        if whitespace_count > 0:
            issues.append({
                "type": "whitespace_strings", 
                "severity": "moderate",
                "description": f"{whitespace_count} whitespace-only values"
            })
    
    # Determine overall quality
    severities = [issue["severity"] for issue in issues]
    if "critical" in severities:
        quality = "poor"
    elif "moderate" in severities:
        quality = "fair"
    else:
        quality = "good"
    
    return {
        "quality": quality,
        "issues": issues,
        "issue_count": len(issues)
    }


def assess_data_quality(profile_data: dict) -> dict:
    """Assess data quality for all fields in a dataset profile.
    
    Args:
        profile_data (dict): Output from field_profile function.
        
    Returns:
        dict: Quality assessment for each field with format {"field": {"summary": dict}}.
    """
    result = {}
    
    for field_name, field_data in profile_data.items():
        result[field_name] = {
            "summary": assess_field_quality(field_name, field_data)
        }
    
    return result