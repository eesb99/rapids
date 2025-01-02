# Usage Guide

## Overview
This guide covers the daily usage of RAPIDS. Make sure you've completed the [Installation Guide](installation.md) and [Configuration Guide](configuration.md) first.

## Basic Commands

### Fetch Papers
```bash
# Fetch papers for a specific date
python src/main.py fetch --date 2024-12-30

# Force fetch (bypass cache)
python src/main.py fetch --date 2024-12-30 --force

# Fetch with custom batch size
python src/main.py fetch --date 2024-12-30 --batch-size 50
```
For configuration options, see [API Settings](configuration.md#api-settings).

After each fetch, RAPIDS automatically generates:
1. A text summary (`fetch_summary.txt`)
2. A markdown summary (`fetch_summary.md`)

The summary includes:
- Total papers in main categories
- Total papers overall
- Papers by category
- Latest papers (up to 5 per category)
- Cross-listed categories for each paper

### Search Papers
```bash
# Search by keyword
python src/main.py search "machine learning"

# Search with date range
python src/main.py search "deep learning" --start-date 2024-01-01 --end-date 2024-12-31
```
Search uses the SQLite database. See [SQLite Database](configuration.md#sqlite-database) for details.

## Storage Systems

### Redis Cache
- Purpose: Quick access to recent queries
- Location: In-memory + disk persistence
- Management:
  ```bash
  # Force fresh fetch (bypass cache)
  python src/main.py fetch --date 2024-12-30 --force
  
  # Clear Redis cache
  redis-cli FLUSHDB
  ```
- Configuration: See [Redis Configuration](configuration.md#redis-cache-configuration)

### SQLite Database
- Purpose: Permanent paper storage
- Location: `arxiv_papers.db`
- Features:
  - Full-text search
  - Date range queries
  - Category filtering
- See [Configuration Guide](configuration.md#sqlite-database) for details

## Output Structure

### Directory Organization
```
output/arxiv_papers/
└── 2024-12-30/
    ├── fetch_summary.txt    # Daily summary in text format
    ├── fetch_summary.md     # Daily summary in markdown
    ├── cs.AI_papers.json    # Papers by category
    ├── cs.AI_papers.csv
    ├── cs.AI_papers.txt
    └── ... (other categories)
```
Configure output directory in [Output Settings](configuration.md#output-settings).

### Summary Format
1. Text Summary (`fetch_summary.txt`):
   ```
   === Fetch Summary ===
   
   Date: 2024-12-30
   Total Papers in Main Categories: 120
   Total Papers Overall: 150
   
   By Main Category:
     cs.AI: 30 papers
     cs.LG: 25 papers
     ...
   
   Latest Papers (up to 5 per category):
   cs.AI:
     - Paper Title
       Authors: Author1, Author2, Author3
       All Categories: cs.AI, cs.LG, stat.ML
   ```

2. Markdown Summary (`fetch_summary.md`):
   - Same information as text summary
   - Better formatting for GitHub/markdown viewers
   - Hierarchical headers for better navigation

### File Formats
1. JSON Format (for programmatic use)
   ```json
   [
     {
       "id": "paper_id",
       "title": "Paper Title",
       "authors": ["Author 1", "Author 2"],
       "abstract": "Paper abstract...",
       "categories": ["cs.AI", "cs.LG"],
       "published": "2024-12-30T00:00:00",
       "pdf_url": "https://arxiv.org/pdf/..."
     }
   ]
   ```

2. CSV Format (for spreadsheet analysis)
   - Columns: id, title, authors, abstract, categories, published, pdf_url
   - Easy to import into Excel, Python pandas, etc.

3. TXT Format (for reading)
   ```
   Title: Paper Title
   Authors: Author 1, Author 2
   Categories: cs.AI, cs.LG
   Published: 2024-12-30T00:00:00
   PDF: https://arxiv.org/pdf/...
   Abstract:
   Paper abstract...
   ----------------------------------------
   ```

## Best Practices

1. Regular Fetching
   - Set up daily fetches for latest papers
   - Use consistent date format (YYYY-MM-DD)
   - Check summary reports for cross-listed papers
   - See [API Settings](configuration.md#api-settings) for rate limits

2. Cache Management
   - Use `--force` when needed
   - Monitor Redis memory usage
   - See [Redis Configuration](configuration.md#redis-cache-configuration)

3. Output Management
   - Review daily summaries
   - Use appropriate format for your needs:
     - CSV for data analysis
     - TXT for reading
     - JSON for programming
     - MD for sharing
   - See [Output Settings](configuration.md#output-settings)

4. Search Effectively
   - Use specific keywords
   - Combine with date ranges
   - Check multiple categories
   - See [SQLite Database](configuration.md#sqlite-database)

## Troubleshooting

1. Redis Issues
   - Check Redis server is running
   - Verify connection settings
   - See [Installation Guide](installation.md#3-redis-installation-and-setup)

2. Output Issues
   - Check directory permissions
   - Verify configuration
   - See [Configuration Guide](configuration.md#output-settings)

## Next Steps
1. Check the [Configuration Guide](configuration.md) for customization
2. Review [Installation Guide](installation.md) for setup changes
3. Start with examples from [Quick Start](../README.md#quick-start)
