def _extract_data_type(column_type: str) -> str:
    """Convert SQL column type to simplified data type category."""
    column_type = column_type.upper()
    if column_type in ['VARCHAR', 'TEXT', 'STRING'] or column_type.startswith('ENUM'):
        return "string"
    if column_type in ['BIGINT', 'INTEGER', 'INT', 'SMALLINT', 'TINYINT']:
        return "integer"
    if column_type in ['DOUBLE', 'FLOAT', 'REAL', 'DECIMAL', 'NUMERIC']:
        return "float"
    if column_type in ['DATE', 'TIMESTAMP', 'DATETIME', 'TIME']:
        return "datetime"
    return "unknown"

def _auto_detect_datetime(conn, table_name: str, col_name: str) -> str:
    """Auto-detect if string column contains datetime values"""
    try:
        # Sample non-null values
        sample_sql = f"""
        SELECT {col_name} 
        FROM {table_name} 
        WHERE {col_name} IS NOT NULL 
        LIMIT 20
        """
        samples = [row[0] for row in conn.execute(sample_sql).fetchall()]
        
        if not samples or len(samples) < 3:
            return None
        
        # Quick pattern check first - avoid obvious non-dates
        import re
        datetime_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',           # 2023-01-15
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}', # 2023-01-15 14:30
            r'^\d{2}/\d{2}/\d{4}$',           # 01/15/2023
            r'^\d{8}$',                       # 20230115
        ]
        
        pattern_matches = 0
        for sample in samples[:10]:  # Check first 10 samples
            sample_str = str(sample).strip()
            if any(re.match(pattern, sample_str) for pattern in datetime_patterns):
                pattern_matches += 1
        
        # If less than 70% match datetime patterns, skip
        if pattern_matches / min(len(samples), 10) < 0.7:
            return None
        
        # Test if values can actually be parsed as datetime
        parseable_count = 0
        for sample in samples:
            try:
                # Try DuckDB's datetime parsing
                result = conn.execute(f"SELECT TRY_CAST('{sample}' AS TIMESTAMP)").fetchone()[0]
                if result is not None:
                    parseable_count += 1
            except:
                continue
        
        # Require 90%+ to be parseable as datetime (more conservative)
        if parseable_count / len(samples) >= 0.9:
            return "datetime"
        
        return None
    except:
        return None

def sql_table_profile(conn, table_name: str) -> dict:
    """Generate dataset-level data quality profile using SQL."""
    # Get table dimensions
    rows = conn.execute(f"SELECT COUNT(1) FROM {table_name}").fetchone()[0]
    
    # Get column count
    columns = len(conn.execute(f"DESCRIBE {table_name}").fetchall())
    
    # Get column names for duplicate detection
    col_names = [col[0] for col in conn.execute(f"DESCRIBE {table_name}").fetchall()]
    col_list = ", ".join(col_names)
    
    # Count duplicates using all columns
    dup_count_sql = f"""
    SELECT COUNT(*) - COUNT(DISTINCT ({col_list})) as duplicates
    FROM {table_name}
    """
    duplicates = conn.execute(dup_count_sql).fetchone()[0]
    
    # Get duplicate evidences
    evidences = {}
    if duplicates > 0:
        dup_rows_sql = f"""
        SELECT {col_list}, COUNT(*) as dup_count
        FROM {table_name}
        GROUP BY {col_list}
        HAVING COUNT(*) > 1
        """
        dup_rows = conn.execute(dup_rows_sql).fetchall()
        
        for i, row in enumerate(dup_rows):
            evidences[i] = dict(zip(col_names + ['dup_count'], row))
    
    return {
        "rows": rows,
        "columns": columns,
        "duplicates": duplicates,
        "evidences": evidences
    }

def sql_field_profile(conn, table_name: str, top_n: int = 5) -> dict:
    """Generate comprehensive data quality profile for each field using SQL."""
    # Get schema
    schema = conn.execute(f"DESCRIBE {table_name}").fetchall()
    total_rows = conn.execute(f"SELECT COUNT(1) FROM {table_name}").fetchone()[0]
    
    results = {}
    
    for col_info in schema:
        col_name = col_info[0]
        col_type = _extract_data_type(col_info[1])
        
        # Auto-detect datetime in string columns
        if col_type == "string":
            detected_type = _auto_detect_datetime(conn, table_name, col_name)
            if detected_type:
                col_type = detected_type
        
        try:
            # Basic metrics for all columns
            basic_sql = f"""
            SELECT 
                COUNT(1) - COUNT({col_name}) as missing_values,
                COUNT(DISTINCT {col_name}) as unique_values
            FROM {table_name}
            """
            basic_metrics = conn.execute(basic_sql).fetchone()
            
            # Most frequent values
            freq_sql = f"""
            SELECT {col_name} as value, COUNT(1) as frequency
            FROM {table_name} 
            WHERE {col_name} IS NOT NULL
            GROUP BY {col_name}
            ORDER BY COUNT(1) DESC
            LIMIT {top_n}
            """
            freq_data = conn.execute(freq_sql).fetchall()
            most_frequent = {row[0]: row[1] for row in freq_data}
            
            # Type-specific statistics
            statistics = {}
            if col_type in ["integer", "float"]:
                stats_sql = f"""
                SELECT 
                    MIN({col_name}) as min_val,
                    MAX({col_name}) as max_val,
                    AVG({col_name}) as mean_val,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY {col_name}) as median_val,
                    STDDEV({col_name}) as std_val,
                    VARIANCE({col_name}) as var_val,
                    SKEWNESS({col_name}) as skew_val,
                    KURTOSIS({col_name}) as kurt_val,
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY {col_name}) as q1,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY {col_name}) as q3
                FROM {table_name}
                WHERE {col_name} IS NOT NULL
                """
                stats = conn.execute(stats_sql).fetchone()
                if stats and stats[0] is not None:
                    iqr = stats[9] - stats[8]  # q3 - q1
                    cv = stats[4] / stats[2] if stats[2] != 0 else 0  # std / mean
                    statistics = {
                        "min": round(stats[0], 2),
                        "max": round(stats[1], 2),
                        "mean": round(stats[2], 2),
                        "median": round(stats[3], 2),
                        "std": round(stats[4], 2),
                        "var": round(stats[5], 2),
                        "skew": round(stats[6], 2),
                        "kurt": round(stats[7], 2),
                        "iqr": round(iqr, 2),
                        "cv": round(cv, 2),
                        "lower_bound": round(stats[8] - 1.5 * iqr, 2),
                        "upper_bound": round(stats[9] + 1.5 * iqr, 2)
                    }
            
            elif col_type == "string":
                string_sql = f"""
                SELECT 
                    AVG(LENGTH({col_name})) as avg_length,
                    MIN(LENGTH({col_name})) as min_length,
                    MAX(LENGTH({col_name})) as max_length,
                    SUM(CASE WHEN {col_name} = '' THEN 1 ELSE 0 END) as empty_count,
                    SUM(CASE WHEN TRIM({col_name}) = '' AND {col_name} != '' THEN 1 ELSE 0 END) as whitespace_count
                FROM {table_name}
                WHERE {col_name} IS NOT NULL
                """
                string_stats = conn.execute(string_sql).fetchone()
                
                # Get mode (most frequent value)
                mode_val = list(most_frequent.keys())[0] if most_frequent else ""
                
                if string_stats:
                    pattern_consistency = basic_metrics[1] / total_rows if total_rows > 0 else 0
                    statistics = {
                        "mode": mode_val,
                        "avg_length": round(string_stats[0], 2) if string_stats[0] else 0,
                        "min_length": string_stats[1] if string_stats[1] else 0,
                        "max_length": string_stats[2] if string_stats[2] else 0,
                        "empty_count": string_stats[3] if string_stats[3] else 0,
                        "whitespace_count": string_stats[4] if string_stats[4] else 0,
                        "pattern_consistency": round(pattern_consistency, 2)
                    }
            
            elif col_type == "datetime":
                datetime_sql = f"""
                SELECT 
                    MIN(TRY_CAST({col_name} AS TIMESTAMP)) as min_date,
                    MAX(TRY_CAST({col_name} AS TIMESTAMP)) as max_date,
                    COUNT(DISTINCT DATE_TRUNC('day', TRY_CAST({col_name} AS TIMESTAMP))) as unique_days,
                    COUNT(DISTINCT DATE_TRUNC('month', TRY_CAST({col_name} AS TIMESTAMP))) as unique_months,
                    COUNT(DISTINCT DATE_TRUNC('year', TRY_CAST({col_name} AS TIMESTAMP))) as unique_years
                FROM {table_name}
                WHERE {col_name} IS NOT NULL
                """
                datetime_stats = conn.execute(datetime_sql).fetchone()
                
                if datetime_stats and datetime_stats[0]:
                    date_range_days = (datetime_stats[1] - datetime_stats[0]).days if datetime_stats[0] and datetime_stats[1] else 0
                    statistics = {
                        "min_date": str(datetime_stats[0]),
                        "max_date": str(datetime_stats[1]),
                        "date_range_days": date_range_days,
                        "unique_days": datetime_stats[2] if datetime_stats[2] else 0,
                        "unique_months": datetime_stats[3] if datetime_stats[3] else 0,
                        "unique_years": datetime_stats[4] if datetime_stats[4] else 0
                    }
            
            # Compile results
            results[col_name] = {
                "data_type": col_type,
                "missing_values": basic_metrics[0],
                "missing_values_pct": round(basic_metrics[0] / total_rows, 2) if total_rows > 0 else 0,
                "unique_values": basic_metrics[1],
                "unique_values_pct": round(basic_metrics[1] / total_rows, 2) if total_rows > 0 else 0,
                "most_frequent": most_frequent,
                "statistics": statistics
            }
            
        except Exception as e:
            # Field-level error handling - mark problematic field but continue
            results[col_name] = {
                "data_type": col_type,
                "error": f"Profiling failed: {str(e)}",
                "missing_values": 0,
                "missing_values_pct": 0.0,
                "unique_values": 0,
                "unique_values_pct": 0.0,
                "most_frequent": {},
                "statistics": {}
            }
    
    return results