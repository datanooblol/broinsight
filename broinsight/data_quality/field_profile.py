import pandas as pd

def _extract_data_type(x):
    """Convert pandas dtype to simplified data type category.
    
    Args:
        x (str): Pandas dtype as string (e.g., 'object', 'int64', 'float32').
        
    Returns:
        str: Simplified data type ('string', 'integer', 'float', 'datetime', or 'unknown').
    """
    if x=="object":
        return "string"
    if x=="category":
        return "string"
    if x.startswith("int"):
        return "integer"
    if x.startswith("float"):
        return "float"
    if x.startswith("datetime") or x.startswith("timestamp"):
        return "datetime"
    else:
        return "unknown"

def _extract_numeric_statistics(series: pd.Series):
    """Calculate comprehensive statistics for numeric data.
    
    Computes descriptive statistics including central tendency, dispersion,
    distribution shape, and outlier detection bounds.
    
    Args:
        series (pd.Series): Numeric pandas Series.
        
    Returns:
        dict: Dictionary containing:
            - min/max: Range values
            - mean/median: Central tendency measures
            - std/var: Dispersion measures
            - skew/kurt: Distribution shape measures
            - iqr: Interquartile range
            - cv: Coefficient of variation (std/mean) - measures relative variability,
                  where values closer to 0 indicate low variability and values > 1
                  indicate high variability relative to the mean
            - lower_bound/upper_bound: Outlier detection bounds using 1.5*IQR rule
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    proxy = pd.Series({
        "min": series.min(),
        "max": series.max(),
        "mean": series.mean(),
        "median": series.median(),
        "std": series.std(),
        "var": series.var(),
        "skew": series.skew(),
        "kurt": series.kurtosis(),
        "iqr": iqr,
        "cv": series.std() / series.mean(),
        "lower_bound": q1 - 1.5 * iqr,
        "upper_bound": q3 + 1.5 * iqr
    })
    return proxy.round(2).to_dict()


def _extract_string_statistics(series: pd.Series):
    """Calculate statistics specific to string/text data.
    
    Args:
        series (pd.Series): String pandas Series.
        
    Returns:
        dict: Dictionary containing:
            - mode: Most frequent value
            - avg_length/min_length/max_length: String length statistics
            - empty_count: Number of empty strings
            - whitespace_count: Number of whitespace-only strings
            - pattern_consistency: Ratio of unique values to total (diversity measure)
    """
    lengths = series.str.len()
    proxy = pd.Series({
        "avg_length": lengths.mean(),
        "min_length": lengths.min(),
        "max_length": lengths.max(),
        "empty_count": (series == "").sum(),
        "whitespace_count": series.str.isspace().sum(),
        "pattern_consistency": series.nunique() / len(series)
    })
    proxy = proxy.round(2).to_dict()
    proxy = {"mode": series.mode().values[0], **proxy}
    return proxy


def _extract_datetime_statistics(series: pd.Series):
    """Calculate statistics specific to datetime data.
    
    Args:
        series (pd.Series): Datetime pandas Series.
        
    Returns:
        dict: Dictionary containing datetime-specific statistics.
    """
    try:
        date_range_days = (series.max() - series.min()).days if series.max() and series.min() else 0
        proxy = pd.Series({
            "min_date": str(series.min()),
            "max_date": str(series.max()),
            "date_range_days": date_range_days,
            "unique_days": series.dt.date.nunique(),
            "unique_months": series.dt.to_period('M').nunique(),
            "unique_years": series.dt.year.nunique()
        })
        return proxy.to_dict()
    except:
        return {}

def _extract_statistics(series: pd.Series, dtype: str):
    """Extract appropriate statistics based on data type.
    
    Args:
        series (pd.Series): Data series to analyze.
        dtype (str): Data type category ('string', 'integer', 'float', 'datetime', etc.).
        
    Returns:
        dict: Statistics dictionary appropriate for the data type.
    """
    if dtype=="string":
        return _extract_string_statistics(series)
    if dtype in ["integer", "float"]:
        return _extract_numeric_statistics(series)
    if dtype == "datetime":
        return _extract_datetime_statistics(series)
    else:
        return {}

def _extract_most_frequent(series: pd.Series, top_n: int = 5):
    """Get the most frequent values and their counts.
    
    Args:
        series (pd.Series): Data series to analyze.
        top_n (int, optional): Number of top frequent values to return. Defaults to 5.
        
    Returns:
        dict: Dictionary mapping values to their occurrence counts.
    """
    return series.value_counts().head(top_n).to_dict()

def field_profile(df: pd.DataFrame, top_n: int = 5):
    """Generate comprehensive data quality profile for each field in a DataFrame.
    
    Creates detailed statistics and quality metrics for every column, including
    data types, missing values, uniqueness, frequency distributions, and
    type-specific statistical measures.
    
    Args:
        df (pd.DataFrame): DataFrame to profile.
        top_n (int, optional): Number of most frequent values to include. Defaults to 5.
        
    Returns:
        dict: Nested dictionary with field names as keys, each containing:
            - data_types: Simplified data type category
            - missing_values: Count of null/NaN values
            - missing_values_pct: Percentage of missing values
            - unique_values: Count of distinct values
            - unique_values_pct: Percentage of unique values
            - most_frequent: Top N most frequent values with counts
            - statistics: Type-specific statistical measures
    """
    features = df.columns.tolist()
    data = pd.DataFrame({
        "data_types": df.dtypes.astype(str),
        "missing_values": df.isnull().sum(),
        "missing_values_pct": df.isnull().sum() / df.shape[0],
        "unique_values": df.nunique(),
        "unique_values_pct": df.nunique() / df.shape[0],
        "most_frequent": [_extract_most_frequent(df[feat], top_n=top_n) for feat in features]
    }, index=features)
    data["data_types"] = data["data_types"].apply(_extract_data_type)
    data["statistics"] = [_extract_statistics(series=df[feat], dtype=data.loc[feat, "data_types"]) for feat in features] 
    return data.round(2).to_dict(orient="index")