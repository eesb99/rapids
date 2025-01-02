# OpenRouter Research Paper Analyzer

A Python client for analyzing research papers using OpenRouter's deepseek-chat model.

## Setup

1. Create conda environment:
```bash
conda env create -f environment.yml
```

2. Activate environment:
```bash
conda activate openrouter_env
```

3. Create a `.env` file with your OpenRouter API key:
```
OPENROUTER_API_KEY=your_api_key_here
```

## Usage

```python
from openrouter_client import OpenRouterClient

# Initialize client
client = OpenRouterClient()

# Get paper recommendations
recommendations = client.analyze_papers(
    field="reinforcement learning",
    audience="expert"
)

# Process recommendations
for paper in recommendations:
    print(f"Title: {paper.title}")
    print(f"Authors: {paper.authors}")
    # ...
```

## Testing

Run tests using pytest:
```bash
pytest test_openrouter_client.py
```

## Features

- Paper recommendations based on novelty and impact
- Customizable field/topic targeting
- Audience-specific recommendations (general/expert/practitioner)
- Structured output with paper details
- Error handling and validation
- Type hints and documentation
