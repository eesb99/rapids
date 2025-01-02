# Configuration Guide

## Overview
RAPIDS uses JSON configuration files to manage settings for APIs, analysis, output formats, and storage systems.

## Main Configuration Files

### 1. ArXiv Configuration
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
        "stat.ML"
    ],
    "output": {
        "base_dir": "output/arxiv_papers",
        "formats": ["json", "csv", "txt", "markdown"]
    },
    "redis": {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "cache_ttl": 86400
    }
}
```

### 2. Analysis Configuration
Location: `config/analysis_config.json`

```json
{
    "openrouter": {
        "model": "deepseek/deepseek-chat",
        "max_context_tokens": 32000,
        "max_input_tokens": 8000,
        "max_output_tokens": 4000,
        "temperature": 0.3,
        "top_p": 0.8,
        "top_k": 40,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0,
        "stop_sequences": []
    },
    "fields": [
        "AI",
        "ML",
        "CV",
        "NLP",
        "Robotics"
    ],
    "audience_types": {
        "general": "General audience, minimal technical background",
        "expert": "Domain experts, technical audience"
    },
    "output_formats": {
        "json": true,
        "csv": true,
        "markdown": true
    }
}
```

## Configuration Sections

### 1. ArXiv API Settings
```json
"api": {
    "base_url": "http://export.arxiv.org/api/query",
    "batch_size": 100,
    "rate_limit": {
        "requests_per_second": 1
    }
}
```
- `base_url`: ArXiv API endpoint
- `batch_size`: Papers per request
- `rate_limit`: API rate limiting settings

### 2. Paper Categories
```json
"categories": [
    "cs.AI",
    "cs.LG",
    "cs.CL",
    "cs.CV",
    "stat.ML"
]
```
- List of ArXiv categories to monitor
- See [ArXiv categories](https://arxiv.org/category_taxonomy) for all options

### 3. Output Settings
```json
"output": {
    "base_dir": "output/arxiv_papers",
    "formats": ["json", "csv", "txt", "markdown"]
}
```
- `base_dir`: Output directory for paper data
- `formats`: Enabled output formats

### 4. Redis Cache
```json
"redis": {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "cache_ttl": 86400
}
```
- `host`: Redis server address
- `port`: Redis server port
- `db`: Redis database number
- `cache_ttl`: Cache lifetime in seconds

### 5. OpenRouter Analysis
```json
"openrouter": {
    "model": "deepseek/deepseek-chat",
    "max_context_tokens": 32000,
    "max_input_tokens": 8000,
    "max_output_tokens": 4000,
    "temperature": 0.3,
    "top_p": 0.8,
    "top_k": 40,
    "presence_penalty": 0.0,
    "frequency_penalty": 0.0,
    "stop_sequences": []
}
```
- `model`: Language model to use
- `max_context_tokens`: Maximum context window
- `max_input_tokens`: Maximum input size
- `max_output_tokens`: Maximum response size
- `temperature`: Response creativity (0.0-1.0)
- `top_p`: Nucleus sampling parameter
- `top_k`: Number of tokens to consider for sampling
- `presence_penalty`: Token repetition penalty
- `frequency_penalty`: Word repetition penalty
- `stop_sequences`: List of strings where generation should stop

### 6. Analysis Fields
```json
"fields": [
    "AI",
    "ML",
    "CV",
    "NLP",
    "Robotics"
]
```
- Available research fields for analysis
- Used for field-specific insights

### 7. Audience Types
```json
"audience_types": {
    "general": "General audience, minimal technical background",
    "expert": "Domain experts, technical audience"
}
```
- Target audience levels for analysis
- Affects technical depth of analysis

## Environment Variables

Create a `.env` file in the project root:
```plaintext
# Required
OPENROUTER_API_KEY=your-api-key-here

# Optional
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-password  # if using authentication
```

## Advanced Configuration

### Custom Analysis Prompts
Location: `config/prompt_config.json`

```json
{
    "prompt_template": "Your custom prompt template",
    "example_output": [...],
    "field_examples": [...],
    "audience_types": {...}
}
```

### Batch Processing
```json
"batch": {
    "size": 10,
    "delay": 5,
    "max_retries": 3
}
```
- `size`: Papers per batch
- `delay`: Seconds between batches
- `max_retries`: Retry attempts on failure

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

## OpenRouter Parameters

The OpenRouter configuration supports several parameters to control the AI model's behavior:

1. `temperature` (default: 0.3)
   - Controls randomness in responses
   - Range: 0.0-2.0
   - Lower values (0.1-0.4): More focused, deterministic responses
   - Higher values (0.7-2.0): More creative, diverse responses

2. `top_p` (default: 0.8)
   - Nucleus sampling parameter
   - Range: 0.0-1.0
   - Controls diversity of token selection
   - Higher values allow more diverse outputs

3. `top_k` (default: 40)
   - Number of tokens to consider for sampling
   - Lower values: More focused responses
   - Higher values: More diverse responses

4. `presence_penalty` (default: 0.0)
   - Range: -2.0 to 2.0
   - Positive values discourage token repetition
   - Negative values allow more repetition

5. `frequency_penalty` (default: 0.0)
   - Range: -2.0 to 2.0
   - Positive values reduce word repetition
   - Negative values allow more repetition

6. `stop_sequences` (default: [])
   - List of strings where generation should stop
   - Example: ["END", "STOP", "\n\n"]
   - Useful for controlling output format
