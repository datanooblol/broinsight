# Data Quality Profiling Specification

## Overview

BroInsight implements a two-tier data quality profiling system that analyzes datasets at both the **table level** (overall dataset characteristics) and **field level** (individual column analysis).

## Table-Level Profiling (`table_profile`)

### Purpose
Analyzes overall dataset structure and identifies duplicate records.

### Metrics
- **Dimensions**: Row and column counts
- **Duplicate Detection**: Complete row duplicates with evidence
- **Evidence Collection**: Actual duplicate rows for manual inspection

### Output Structure
```python
{
    "rows": int,           # Total number of rows
    "columns": int,        # Total number of columns  
    "duplicates": int,     # Count of duplicate rows
    "evidences": dict      # Actual duplicate rows indexed by row number
}
```

## Field-Level Profiling (`field_profile`)

### Purpose
Comprehensive analysis of each column including data types, completeness, uniqueness, and statistical measures.

### Data Type Classification
Simplifies pandas dtypes into 4 categories:
- `string`: object, category types
- `integer`: int64, int32, etc.
- `float`: float64, float32, etc.
- `unknown`: unrecognized types

### Core Quality Metrics

#### Completeness
- **missing_values**: Count of null/NaN values
- **missing_values_pct**: Percentage of missing data

#### Uniqueness  
- **unique_values**: Count of distinct values
- **unique_values_pct**: Ratio of unique to total values

#### Frequency Distribution
- **most_frequent**: Top N most common values with counts (default: top 5)

### Type-Specific Statistics

#### Numeric Data (integer/float)
- **Central Tendency**: min, max, mean, median
- **Dispersion**: std, var, iqr
- **Distribution Shape**: skew, kurt
- **Variability**: cv (coefficient of variation = std/mean)
- **Outlier Detection**: lower_bound, upper_bound (using 1.5×IQR rule)

#### String Data
- **Mode**: Most frequent value
- **Length Analysis**: avg_length, min_length, max_length
- **Quality Issues**: empty_count, whitespace_count
- **Diversity**: pattern_consistency (unique values / total values)

### Output Structure
```python
{
    "column_name": {
        "data_types": str,
        "missing_values": int,
        "missing_values_pct": float,
        "unique_values": int, 
        "unique_values_pct": float,
        "most_frequent": dict,
        "statistics": dict  # Type-specific metrics
    }
}
```

## Data Quality Assessment Logic

### Completeness Assessment
- High missing values (>20%) indicate potential data collection issues
- Missing value patterns can reveal systematic data problems

### Uniqueness Assessment  
- Low uniqueness in expected-unique fields (IDs) indicates duplicates
- High uniqueness in categorical fields may indicate data entry inconsistencies

### Distribution Assessment
- High coefficient of variation (cv > 1) indicates high relative variability
- Extreme skewness/kurtosis suggests outliers or data quality issues
- Values outside outlier bounds warrant investigation

### String Quality Assessment
- High empty/whitespace counts indicate data entry problems
- Low pattern consistency in structured fields (emails, IDs) suggests format issues
- Extreme length variations may indicate concatenated or truncated data

## Usage Pattern

```python
# Complete data quality assessment
table_stats = table_profile(df)
field_stats = field_profile(df, top_n=5)

# Combine for comprehensive view
dq_report = {
    "table_level": table_stats,
    "field_level": field_stats
}
```

This approach provides actionable insights for data cleaning, validation, and quality improvement decisions.