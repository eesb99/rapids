# Configuration Guide

## Overview
RAPIDS uses a JSON configuration file to manage settings for API access, output formats, and storage systems.

## Configuration File
Location: `config/arxiv_config.json`

```json
{
    "api": {
        "base_url": "http://export.arxiv.org/api/query",
        "batch_size": 100,
        "rate_limit": {
            "requests_per_second": 1
        }
    },
    "categories": [
        "cs.AI",
        "cs.LG",
        "cs.CL",
        "cs.CV",
        "cs.NE",
        "stat.ML"
    ],
    "output": {
        "base_dir": "output/arxiv_papers",
        "formats": ["json", "csv", "txt"]
    },
    "redis": {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "cache_ttl": 86400
    }
}
```

## Configuration Sections

### API Settings
```json
"api": {
    "base_url": "http://export.arxiv.org/api/query",
    "batch_size": 100,
    "rate_limit": {
        "requests_per_second": 1
    }
}
```
- `base_url`: arXiv API endpoint
- `batch_size`: Papers per request
- `rate_limit`: API request throttling

### Categories
```json
"categories": [
    "cs.AI",
    "cs.LG",
    "cs.CL",
    "cs.CV",
    "cs.NE",
    "stat.ML"
]
```
- List of arXiv categories to fetch
- Used as primary categories in summaries
- Cross-listed papers are tracked but grouped by primary category

### Output Settings
```json
"output": {
    "base_dir": "output/arxiv_papers",
    "formats": ["json", "csv", "txt"]
}
```
- `base_dir`: Base directory for outputs (relative to project root)
- `formats`: Output file formats to generate

### Redis Cache Configuration
```json
"redis": {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "cache_ttl": 86400
}
```
- `host`: Redis server host
- `port`: Redis server port
- `db`: Redis database number
- `cache_ttl`: Cache time-to-live in seconds

## Output Structure

### Directory Layout
```
output/arxiv_papers/
└── YYYY-MM-DD/
    ├── fetch_summary.txt    # Daily fetch summary
    ├── fetch_summary.md     # Markdown summary
    ├── cs.AI_papers.json    # Papers by category
    ├── cs.AI_papers.csv
    ├── cs.AI_papers.txt
    └── ... (other categories)
```

### Summary Files
1. `fetch_summary.txt`:
   - Plain text summary
   - Total papers count
   - Category breakdown
   - Latest papers list

2. `fetch_summary.md`:
   - Markdown formatted
   - Better for sharing/viewing
   - Same content as TXT

### Paper Files
For each category (e.g., cs.AI):
1. `cs.AI_papers.json`:
   - Complete paper data
   - Machine-readable format
   - Includes all metadata

2. `cs.AI_papers.csv`:
   - Tabular format
   - Good for analysis
   - Key fields only

3. `cs.AI_papers.txt`:
   - Human-readable format
   - Formatted for easy reading
   - Complete paper details

## SQLite Database

### Database File
- Location: `arxiv_papers.db`
- Contains all fetched papers
- Enables full-text search
- Preserves complete metadata

### Schema
```sql
CREATE TABLE papers (
    id TEXT PRIMARY KEY,
    data TEXT,  -- JSON data
    title TEXT,
    abstract TEXT,
    authors TEXT,
    categories TEXT,
    published TEXT
);
```

### Search Capabilities
- Full-text search on:
  - Title
  - Abstract
  - Authors
- Filter by:
  - Date range
  - Categories
  - Author names

## Redis Cache

### Purpose
- Cache API responses
- Reduce API calls
- Improve performance

### Cache Keys
Format: `arxiv:{category}:{date}`
Example: `arxiv:cs.AI:2024-12-30`

### Cache Values
- JSON string of papers
- TTL: 24 hours (configurable)
- Automatically cleaned up

## Best Practices

### Categories
1. Keep category list focused
2. Primary categories first
3. Monitor cross-listings
4. Update as needed

### Output Management
1. Use relative paths
2. Regular backups
3. Clean old files
4. Check summaries

### Cache Settings
1. Adjust TTL as needed
2. Monitor memory usage
3. Use force flag when needed
4. Regular maintenance

### API Settings
1. Respect rate limits
2. Adjust batch size
3. Monitor errors
4. Log responses

## Troubleshooting

### Common Issues
1. Redis connection:
   - Check host/port
   - Verify service running
   - Test connection

2. Output errors:
   - Check permissions
   - Verify paths
   - Monitor disk space

3. API issues:
   - Check rate limits
   - Verify connection
   - Monitor responses

## Updates and Maintenance

### Regular Tasks
1. Update categories
2. Clean old files
3. Backup database
4. Check logs

### Version Control
1. Track config changes
2. Document updates
3. Test changes
4. Backup configs
