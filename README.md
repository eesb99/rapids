# RAPIDS (Research Article Processing In Daily Summaries)

RAPIDS is a powerful tool designed to fetch, process, and analyze research articles from arXiv, with a focus on AI, ML, and Computer Science papers. It provides efficient caching, searching, and multiple output formats for research paper management.

## Features

- Daily paper fetching from arXiv with rate limiting
- Multiple output formats (JSON, CSV, TXT)
- Automatic fetch summaries with paper statistics
- Redis caching for improved performance
- SQLite-based historical search
- Configurable categories and settings
- Batch processing capabilities

## Repository

The source code is available at: https://github.com/eesb99/rapids.git

## Quick Start

1. Install Redis (see [Installation Guide](docs/installation.md))
2. Set up Python environment:
```bash
conda env create -f environment.yml
conda activate rapids
```

3. Fetch papers:
```bash
python src/main.py fetch --date 2024-12-30
```

This will:
- Download papers from configured categories
- Save in JSON, CSV, and TXT formats
- Generate a summary report (TXT and MD)
- Cache results in Redis
- Store in SQLite for searching

4. Search papers:
```bash
python src/main.py search "machine learning"
```

## Documentation

Detailed documentation is available in the `docs` directory:

- [Installation Guide](docs/installation.md) - Complete setup instructions
- [Configuration Guide](docs/configuration.md) - Configuration options and storage details
- [Usage Guide](docs/usage.md) - Commands and best practices

## Storage System

RAPIDS uses a three-tier storage system:

1. **Redis Cache** (Temporary)
   - Quick access to recent queries
   - Reduces API calls to arXiv
   - Configurable in `config/arxiv_config.json`

2. **SQLite Database** (Permanent)
   - Stores all fetched papers
   - Enables complex searches
   - Located at `arxiv_papers.db`

3. **File Outputs** (Organized)
   - JSON for programmatic use
   - CSV for spreadsheet analysis
   - TXT for human reading
   - Summary reports (TXT and MD)
   - Organized by date and category

## Output Structure

```
output/arxiv_papers/
└── YYYY-MM-DD/
    ├── fetch_summary.txt    # Daily fetch summary
    ├── fetch_summary.md     # Formatted markdown summary
    ├── cs.AI_papers.json    # Papers by category
    ├── cs.AI_papers.csv
    ├── cs.AI_papers.txt
    └── ... (other categories)
```

## Basic Usage

### Fetch Papers
```bash
# Fetch papers for today
python src/main.py fetch

# Fetch specific date
python src/main.py fetch --date 2024-12-30

# Force fetch (bypass cache)
python src/main.py fetch --date 2024-12-30 --force
```

### Search Papers
```bash
# Basic search
python src/main.py search "deep learning"

# Search with date range
python src/main.py search "AI" --start-date 2024-01-01 --end-date 2024-12-31
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
