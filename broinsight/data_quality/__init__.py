"""Data quality profiling and analysis module.

This module provides comprehensive data quality assessment tools for pandas DataFrames,
including field-level profiling, table-level analysis, and statistical summaries.

Key Features:
    - Field profiling with type-specific statistics
    - Missing value analysis
    - Duplicate detection with evidence collection
    - Frequency distributions and uniqueness metrics
    - Outlier detection bounds
    - String pattern analysis

Example:
    >>> from broinsight.data_quality import field_profile, table_profile
    >>> import pandas as pd
    >>> 
    >>> df = pd.read_csv('data.csv')
    >>> field_stats = field_profile(df)
    >>> table_stats = table_profile(df)
"""

from .field_profile import field_profile
from .table_profile import table_profile

__all__ = ['field_profile', 'table_profile']