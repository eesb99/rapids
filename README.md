# RAPIDS (Research Article Processing In Daily Summaries)

RAPIDS is a powerful tool designed to fetch, process, and analyze research articles from arXiv, with a focus on AI, ML, and Computer Science papers. It leverages advanced language models to provide insightful analysis and summaries of research papers.

## Features

- **Paper Collection**
  - Daily paper fetching from arXiv with rate limiting
  - Support for multiple categories (AI, ML, CV, NLP, etc.)
  - Efficient caching using Redis
  - SQLite-based historical search

- **Analysis Capabilities**
  - AI-powered paper analysis using OpenRouter API
  - Extraction of key contributions and significance
  - Field-specific relevance assessment
  - Citation generation

- **Output Formats**
  - Structured JSON output
  - CSV for spreadsheet analysis
  - Human-readable TXT summaries
  - Markdown reports
  - Daily analysis statistics

## Prerequisites

- Python 3.10 or higher
- Redis server (for caching)
- OpenRouter API key (for AI analysis)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/eesb99/rapids.git
cd rapids
```

2. Create and activate conda environment:
```bash
conda env create -f environment.yml
conda activate rapids
```

3. Set up environment variables:
```bash
# Create .env file with your API keys
echo "OPENROUTER_API_KEY=your-api-key-here" > .env
```

## Configuration

1. **API Keys**: Set your OpenRouter API key in `.env`:
```plaintext
OPENROUTER_API_KEY=your-api-key-here
```

2. **ArXiv Categories**: Configure paper categories in `config/arxiv_config.json`:
```json
{
  "categories": ["cs.AI", "cs.CL", "cs.CV", "cs.LG", "stat.ML"]
}
```

## Usage

### Fetch and Analyze Papers

1. Fetch today's papers:
```bash
python src/main.py fetch
```

2. Fetch papers for a specific date:
```bash
python src/main.py fetch --date 2024-12-30
```

3. Analyze papers:
```bash
python src/main.py analyze --date 2024-12-30 --field "AI" --audience "general"
```

### Output Structure

```
output/arxiv_papers/
└── YYYY-MM-DD/
    ├── analysis_all_general.json    # AI analysis results
    ├── cs.AI_papers.json           # Raw paper data by category
    ├── cs.AI_papers.csv            # Spreadsheet format
    ├── cs.AI_papers.txt            # Human readable
    └── analysis_summary.md         # Daily analysis report
```

## Paper Analysis

### Using the Command Line

1. Basic analysis of today's papers:
```bash
python src/main.py analyze
```

2. Analyze papers for a specific date:
```bash
python src/main.py analyze --date 2024-12-30 --field "AI" --audience "general"
```

3. Analyze with custom settings:
```bash
python src/main.py analyze \
    --date 2024-12-30 \
    --field "AI" \
    --audience "expert" \
    --categories "cs.AI,cs.LG" \
    --output-format "json"
```

### Using the Python API

```python
from openrouter import OpenRouterClient
from analyze_papers import PaperAnalyzer

# Initialize with your API key
client = OpenRouterClient(api_key="your-api-key")  # Or set via OPENROUTER_API_KEY env var

# Create analyzer
analyzer = PaperAnalyzer(client)

# Single paper analysis
result = analyzer.analyze_papers(
    content="paper abstract here",
    field="AI",
    audience="general"
)

# Batch analysis from file
with open('papers.json', 'r') as f:
    papers = json.load(f)
    
results = analyzer.analyze_papers(
    content=papers['abstracts'],
    field="AI",
    audience="expert"
)
```

### Analysis Output Format

The analysis generates a JSON file with this structure:
```json
{
  "metadata": {
    "date": "2024-12-27",
    "field": "AI",
    "audience": "general",
    "total_papers": 5,
    "successful_analyses": 5,
    "timestamp": "2024-12-27T10:00:00Z"
  },
  "papers": [
    {
      "title": "Paper Title",
      "authors": "Author1, Author2",
      "key_contributions": "Main innovations and contributions",
      "importance": "Impact and significance",
      "citation": "Formatted citation",
      "reason_chosen": "Field relevance",
      "category": "cs.AI"
    }
  ]
}
```

### Configuration Options

- **Field**: Research field for analysis (e.g., "AI", "ML", "CV")
- **Audience**: Target audience level ("general", "expert")
- **Categories**: ArXiv categories to analyze (e.g., "cs.AI", "cs.LG")
- **Output Format**: Output format ("json", "csv", "markdown")

### Common Issues and Solutions

1. **Missing API Key**
   ```bash
   # Set API key in .env file
   echo "OPENROUTER_API_KEY=your-api-key-here" > .env
   ```

2. **Rate Limiting**
   ```bash
   # Use batch mode with delays
   python src/main.py analyze --batch-size 10 --delay 5
   ```

3. **Parse Errors**
   ```bash
   # Run with debug logging
   python src/main.py analyze --debug
   ```

## Development

### Running Tests
```bash
pytest tests/ --cov=rapids
```

### Code Style
```bash
black .
```

## Project Structure

```
rapids/
├── config/                  # Configuration files
├── docs/                    # Documentation
├── openrouter/             # AI analysis components
├── src/                    # Core source code
├── tests/                  # Test suite
├── environment.yml         # Conda environment
├── setup.py               # Package setup
└── README.md              # This file
```

## Documentation

- [Installation Guide](docs/installation.md) - Detailed setup instructions
- [Configuration Guide](docs/configuration.md) - Configuration options
- [API Reference](docs/api.md) - API documentation
- [Development Guide](docs/development.md) - Contributing guidelines

## Dependencies

Key dependencies:
- arxiv: ArXiv API client
- openrouter-py: OpenRouter API client
- redis: Caching system
- pydantic: Data validation
- rich: Terminal formatting
- loguru: Logging system

See `environment.yml` for complete list.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
