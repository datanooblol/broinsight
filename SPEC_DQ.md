# Data Quality Module Specification

## Overview
The Data Quality (DQ) module provides comprehensive programmatic analysis of pandas DataFrames, generating detailed field-level and table-level quality metrics for data profiling and assessment.

## Architecture
**Current Implementation:**
```
User DataFrame Input → Field Profiling → Table Profiling → Structured Quality Metrics
```

**Core Components:**
1. **Field Profiling**: Detailed statistics and quality metrics per column
2. **Table Profiling**: Dataset-level analysis including duplicates and dimensions

## Core Objectives
- **Profile**: Generate comprehensive field-level statistics and quality metrics
- **Analyze**: Detect missing values, duplicates, and data distribution patterns
- **Classify**: Automatically categorize data types and extract appropriate statistics
- **Structure**: Provide machine-readable quality results for further analysis
- **Evidence**: Collect actual examples of data quality issues for inspection

## Current Implementation Features

### Field Profiling (`field_profile`)
**Data Type Detection:**
- Automatic classification: string, integer, float, unknown
- Maps pandas dtypes to simplified categories

**Missing Value Analysis:**
- Count and percentage of null/NaN values per field
- Identifies completeness issues

**Uniqueness Metrics:**
- Count and percentage of unique values
- Frequency distribution of most common values (configurable top N)

**Statistical Analysis:**
- **Numeric Fields**: min/max, mean/median, std/var, skewness/kurtosis, IQR, coefficient of variation (CV), outlier bounds
- **String Fields**: mode, length statistics, empty/whitespace counts, pattern consistency

### Table Profiling (`table_profile`)
**Dataset Dimensions:**
- Row and column counts

**Duplicate Detection:**
- Count of exact duplicate rows
- Evidence collection: actual duplicate records with indices for inspection

## API Interface

### Field Profiling
```python
from broinsight.data_quality import field_profile
import pandas as pd

df = pd.read_csv('data.csv')
field_stats = field_profile(df, top_n=5)
```

### Table Profiling
```python
from broinsight.data_quality import table_profile

table_stats = table_profile(df)
```

### Output Structure

**Field Profile Output:**
```python
{
    'field_name': {
        'data_types': str,           # 'string', 'integer', 'float', 'unknown'
        'missing_values': int,       # Count of null values
        'missing_values_pct': float, # Percentage missing (0.0-1.0)
        'unique_values': int,        # Count of unique values
        'unique_values_pct': float,  # Uniqueness ratio (0.0-1.0)
        'most_frequent': dict,       # Top N values with counts
        'statistics': dict           # Type-specific statistics
    }
}
```

**Numeric Statistics:**
```python
{
    'min': float, 'max': float, 'mean': float, 'median': float,
    'std': float, 'var': float, 'skew': float, 'kurt': float,
    'iqr': float, 'cv': float,  # Coefficient of variation (std/mean)
    'lower_bound': float, 'upper_bound': float  # Outlier detection bounds
}
```

**String Statistics:**
```python
{
    'mode': str, 'avg_length': float, 'min_length': float, 'max_length': float,
    'empty_count': float, 'whitespace_count': float, 'pattern_consistency': float
}
```

**Table Profile Output:**
```python
{
    'rows': int,
    'columns': int,
    'duplicates': int,
    'evidences': dict  # Actual duplicate rows indexed by row number
}
```

## Key Metrics Explained

### Coefficient of Variation (CV)
**Formula:** `CV = standard_deviation / mean`

**Interpretation:**
- Values closer to 0 = low variability (consistent data)
- Values > 1 = high variability relative to the mean (inconsistent data)
- Useful for comparing variability across different scales of measurement

### Outlier Detection Bounds
**Formula:** 
- `lower_bound = Q1 - 1.5 * IQR`
- `upper_bound = Q3 + 1.5 * IQR`

**Usage:** Values outside these bounds are considered potential outliers

### Pattern Consistency (Strings)
**Formula:** `unique_values / total_values`

**Interpretation:**
- Low values (< 0.1) = highly repetitive data (e.g., categories)
- High values (> 0.8) = mostly unique data (e.g., names, IDs)

## Integration with BroInsight

### Current Status
- **Standalone Module**: Can be imported and used independently
- **Programmatic Analysis**: Fast, deterministic quality assessment
- **Structured Output**: Machine-readable results ready for LLM interpretation

### Future Integration Opportunities
- **Conversational Interface**: "What's the quality of my data?"
- **Automatic Profiling**: Run quality checks during data ingestion
- **Quality Scoring**: Implement composite quality scores and grades
- **Issue Detection**: Automated flagging of quality problems with thresholds

## Technical Implementation

### Dependencies
- **pandas**: Core DataFrame operations and statistical functions
- **No external dependencies**: Pure pandas implementation for maximum compatibility

### Performance Characteristics
- **Fast Analysis**: Leverages pandas' optimized operations
- **Memory Efficient**: Processes data in-place without creating large intermediate objects
- **Deterministic**: Consistent results across runs for same input data

### Data Type Handling
- **Automatic Detection**: Maps pandas dtypes to simplified categories
- **Type-Specific Statistics**: Different metrics for numeric vs. string data
- **Graceful Handling**: Unknown types return empty statistics dict

### Current Limitations
- **No Quality Scoring**: Individual metrics provided, but no composite scores
- **No Threshold-Based Flagging**: Raw metrics without automatic issue detection
- **Limited String Analysis**: Basic length and pattern metrics only
- **No Temporal Analysis**: Date/time fields not specifically handled

## Future Enhancements

### Planned Features
1. **Missing Correlation Analysis**: Identify patterns in missing data across fields
2. **Quality Scoring System**: Composite scores with configurable weights
3. **Automated Issue Detection**: Threshold-based flagging of quality problems
4. **Enhanced String Analysis**: Pattern detection for emails, phone numbers, etc.
5. **Temporal Analysis**: Specific handling for date/time fields
6. **Business Rule Validation**: Custom validation rules and constraints

## Example Usage

```python
import pandas as pd
from broinsight.data_quality import field_profile, table_profile

# Load your data
df = pd.read_csv('customer_data.csv')

# Get comprehensive field analysis
field_analysis = field_profile(df, top_n=5)

# Check specific field quality
print(f"Email completeness: {(1 - field_analysis['email']['missing_values_pct']) * 100:.1f}%")
print(f"Customer ID uniqueness: {field_analysis['customer_id']['unique_values_pct'] * 100:.1f}%")

# Get table-level insights
table_analysis = table_profile(df)
print(f"Dataset has {table_analysis['duplicates']} duplicate records")

# Inspect duplicate evidence
if table_analysis['duplicates'] > 0:
    print("Duplicate records:")
    for idx, record in table_analysis['evidences'].items():
        print(f"Row {idx}: {record}")
```