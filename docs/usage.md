# Usage Guide

## Overview
This guide covers the daily usage of RAPIDS. Make sure you've completed the [Installation Guide](installation.md) and [Configuration Guide](configuration.md) first.

## Basic Commands

### 1. Fetch Papers
```bash
# Fetch today's papers
python src/main.py fetch

# Fetch specific date
python src/main.py fetch --date 2024-12-30

# Force fetch (bypass cache)
python src/main.py fetch --date 2024-12-30 --force

# Fetch with custom categories
python src/main.py fetch --date 2024-12-30 --categories "cs.AI,cs.LG"
```

### 2. Analyze Papers
```bash
# Analyze today's papers
python src/main.py analyze

# Analyze specific date
python src/main.py analyze --date 2024-12-30 --field "AI" --audience "general"

# Custom analysis settings
python src/main.py analyze \
    --date 2024-12-30 \
    --field "AI" \
    --audience "expert" \
    --categories "cs.AI,cs.LG" \
    --output-format "json"

# Batch analysis with delay
python src/main.py analyze --batch-size 10 --delay 5
```

### 3. Search Papers
```bash
# Basic search
python src/main.py search "machine learning"

# Advanced search
python src/main.py search "deep learning" \
    --start-date 2024-01-01 \
    --end-date 2024-12-31 \
    --categories "cs.AI,cs.LG" \
    --analyzed-only
```

## Output Files

### 1. Paper Data
```
output/arxiv_papers/YYYY-MM-DD/
├── cs.AI_papers.json     # Raw paper data
├── cs.AI_papers.csv      # Spreadsheet format
└── cs.AI_papers.txt      # Human readable
```

### 2. Analysis Results
```
output/arxiv_papers/YYYY-MM-DD/
├── analysis_all_general.json    # Full analysis results
├── analysis_summary.md          # Daily summary
└── analysis_stats.json          # Analysis statistics
```

## Storage Systems

### 1. Redis Cache
```bash
# Clear cache
python src/main.py cache clear

# View cache stats
python src/main.py cache stats

# Refresh cache
python src/main.py cache refresh --date 2024-12-30
```

### 2. SQLite Database
```bash
# Compact database
python src/main.py db compact

# Export database
python src/main.py db export --format csv

# Verify database
python src/main.py db verify
```

## Advanced Usage

### 1. Custom Analysis
```bash
# Use custom prompt
python src/main.py analyze \
    --date 2024-12-30 \
    --prompt-file "custom_prompt.txt"

# Custom output format
python src/main.py analyze \
    --date 2024-12-30 \
    --output-template "custom_template.json"
```

### 2. Batch Processing
```bash
# Process date range
python src/main.py analyze-batch \
    --start-date 2024-12-01 \
    --end-date 2024-12-31 \
    --field "AI"

# With error handling
python src/main.py analyze-batch \
    --start-date 2024-12-01 \
    --end-date 2024-12-31 \
    --max-retries 3 \
    --continue-on-error
```

### 3. Export Options
```bash
# Export as CSV
python src/main.py analyze \
    --date 2024-12-30 \
    --output csv \
    --output-file "analysis_results.csv"

# Export as Markdown
python src/main.py analyze \
    --date 2024-12-30 \
    --output markdown \
    --output-file "analysis_report.md"
```

## Error Handling

### 1. API Issues
```bash
# Test API connection
python src/main.py test-api

# Verify API key
python src/main.py verify-api

# Check API limits
python src/main.py api-status
```

### 2. Debug Mode
```bash
# Run with debug logging
python src/main.py analyze --debug

# Save debug log
python src/main.py analyze --debug --log-file "debug.log"
```

### 3. Recovery Options
```bash
# Retry failed analyses
python src/main.py retry-failed --date 2024-12-30

# Export failed items
python src/main.py export-failed --format json
```

## Performance Tips

1. **Batch Processing**
   - Use appropriate batch sizes
   - Add delays between batches
   - Monitor memory usage

2. **Cache Management**
   - Enable Redis caching
   - Set reasonable TTL
   - Clear cache periodically

3. **Database Optimization**
   - Compact regularly
   - Index frequently searched fields
   - Export large datasets

## Next Steps

1. Check the [Configuration Guide](configuration.md) for customization
2. Review [API Documentation](api.md) for integration
3. Join our [Community](https://github.com/eesb99/rapids/discussions)
