# Simple EDA Module Specification

## Overview
The Simple EDA module provides exploratory data analysis using pure SQL queries, making it accessible to users with no analytics background while delivering comprehensive insights.

## Core Objectives
- **Explore**: Automatically discover patterns and insights in data using SQL
- **Summarize**: Provide statistical summaries in business-friendly terms
- **Suggest**: Recommend follow-up questions and deeper analysis paths
- **Guide**: Help users understand what their data can tell them

## Analysis Categories

### 1. Descriptive Statistics
**Numeric Columns:**
- Count, min, max, mean, median
- Standard deviation and variance
- Quartiles (25th, 50th, 75th percentiles)
- Range and interquartile range

**Text/Categorical Columns:**
- Unique value counts
- Most/least frequent values
- Category distribution
- Text length statistics

**Date/Time Columns:**
- Date range (earliest to latest)
- Temporal distribution patterns
- Gaps in time series
- Seasonal patterns (if applicable)

### 2. Distribution Analysis
- **Value Frequency**: Top 10 most common values per column
- **Null Distribution**: Missing value patterns across columns
- **Cardinality Analysis**: High/low cardinality detection
- **Skewness Indicators**: Heavily skewed distributions (via SQL percentiles)

### 3. Relationship Discovery
- **Cross-Tabulation**: Relationships between categorical variables
- **Grouping Analysis**: Aggregations by key dimensions
- **Trend Detection**: Time-based patterns using SQL window functions
- **Correlation Proxies**: SQL-based correlation indicators

### 4. Data Profiling
- **Column Profiling**: Comprehensive statistics per column
- **Table Profiling**: Row counts, table relationships
- **Data Types**: Actual vs. expected data type usage
- **Pattern Recognition**: Common patterns in text fields

## SQL-Based Techniques

### Statistical Functions
```sql
-- Comprehensive numeric analysis
SELECT 
    COUNT(*) as total_count,
    COUNT(column_name) as non_null_count,
    MIN(column_name) as minimum,
    MAX(column_name) as maximum,
    AVG(column_name) as mean,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY column_name) as median,
    STDDEV(column_name) as std_deviation
FROM table_name;
```

### Distribution Analysis
```sql
-- Value frequency analysis
SELECT 
    column_name,
    COUNT(*) as frequency,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM table_name 
GROUP BY column_name 
ORDER BY frequency DESC 
LIMIT 10;
```

### Temporal Patterns
```sql
-- Time-based aggregations
SELECT 
    DATE_TRUNC('month', date_column) as month,
    COUNT(*) as record_count,
    AVG(numeric_column) as avg_value
FROM table_name 
GROUP BY DATE_TRUNC('month', date_column)
ORDER BY month;
```

## User Experience

### Input Triggers
- "Explore my data"
- "Show me basic statistics"
- "What patterns are in my data?"
- "Summarize my dataset"
- "Give me an overview of [table_name]"
- "What can you tell me about my data?"

### Guided Question Lists
When users provide question lists, the module will:
1. **Parse Questions**: Extract analytical intent from each question
2. **Generate SQL**: Create appropriate queries for each question
3. **Execute Analysis**: Run queries and collect results
4. **Synthesize Insights**: Combine results into coherent narrative
5. **Suggest Follow-ups**: Recommend additional questions based on findings

### Output Format

#### 1. Executive Summary
- Dataset overview (tables, columns, rows)
- Key characteristics and patterns
- Most interesting findings
- Data quality highlights

#### 2. Statistical Profile
**Per Table:**
- Row count and completeness
- Column breakdown by data type
- Key statistics for numeric columns
- Top categories for text columns

**Per Column:**
- Data type and sample values
- Completeness percentage
- Statistical summary (if numeric)
- Distribution characteristics

#### 3. Pattern Discovery
- **Trends**: Time-based patterns if dates present
- **Relationships**: Cross-tabulations between key variables
- **Outliers**: Extreme values detected via SQL
- **Segments**: Natural groupings in the data

#### 4. Business Insights
- **What it means**: Translate statistics into business language
- **Key takeaways**: Most important findings
- **Opportunities**: Potential areas for deeper analysis
- **Recommendations**: Suggested next steps

## Question Processing Engine

### Question Categories
1. **Descriptive**: "What's the average...?", "How many...?"
2. **Comparative**: "Which is higher...?", "Compare..."
3. **Temporal**: "What's the trend...?", "How has it changed...?"
4. **Segmentation**: "Break down by...", "Group by..."
5. **Ranking**: "Top 10...", "Lowest performing..."

### SQL Generation Strategy
- **Template Matching**: Map question types to SQL templates
- **Parameter Extraction**: Identify columns, filters, aggregations
- **Query Optimization**: Ensure efficient execution
- **Result Formatting**: Structure output for interpretation

## Business-Friendly Explanations

### Statistical Translation
- **Mean**: "On average, customers spend $X"
- **Median**: "Half of all orders are above $X"
- **Standard Deviation**: "Most values fall within $X of the average"
- **Percentiles**: "75% of customers are younger than X years"

### Pattern Interpretation
- **Seasonality**: "Sales peak in December and dip in February"
- **Correlation**: "Higher prices tend to coincide with lower quantities"
- **Distribution**: "Most customers make small purchases, with few large buyers"
- **Trends**: "Revenue has grown 15% over the past year"

## Limitations & Boundaries

### What SQL Can Handle
- Aggregations and grouping
- Basic statistical functions
- Percentiles and rankings
- Simple pattern detection
- Cross-tabulations
- Time-based analysis

### What Requires Advanced EDA
- Complex statistical tests
- Correlation matrices
- Outlier detection algorithms
- Normality testing
- Regression analysis
- Machine learning insights

## Success Metrics
- **Coverage**: Percentage of user questions answerable with SQL
- **Accuracy**: Correctness of generated insights
- **Comprehension**: User understanding of results
- **Engagement**: Follow-up question generation
- **Efficiency**: Time to generate comprehensive analysis

## Integration Points
- **Routing**: Triggered when users request basic data exploration
- **Metadata**: Leverages table schemas for appropriate analysis
- **Query Engine**: Uses existing SQL execution infrastructure
- **Question Processing**: Handles both single questions and question lists
- **Insight Generation**: Produces business-friendly explanations