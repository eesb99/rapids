# RAPIDS Examples

## Configuration Examples

### OpenRouter Configuration

Here are some example configurations for different use cases:

1. Default Configuration (Balanced)
```python
client = OpenRouterClient(
    temperature=0.3,        # Focused responses
    top_p=0.8,             # Allow some diversity
    top_k=40,              # Moderate token pool
    presence_penalty=0.0,   # No repetition penalty
    frequency_penalty=0.0   # No frequency penalty
)
```

2. Creative Analysis
```python
client = OpenRouterClient(
    temperature=0.8,        # More creative
    top_p=0.9,             # Higher diversity
    top_k=100,             # Larger token pool
    presence_penalty=0.2,   # Slight repetition penalty
    frequency_penalty=0.2   # Slight frequency penalty
)
```

3. Focused Analysis
```python
client = OpenRouterClient(
    temperature=0.2,        # Very focused
    top_p=0.5,             # Limited diversity
    top_k=20,              # Small token pool
    presence_penalty=0.0,   # No repetition penalty
    frequency_penalty=0.0   # No frequency penalty
)
```

4. Technical Writing
```python
client = OpenRouterClient(
    temperature=0.3,
    top_p=0.8,
    top_k=40,
    presence_penalty=0.1,   # Slight penalty to avoid repetition
    frequency_penalty=0.1,  # Slight penalty for word variety
    stop_sequences=["\n\n", "END"]  # Stop at paragraph breaks
)
```

## Usage Examples

### 1. Fetch and Analyze Papers
```python
# Fetch papers from arXiv
python src/main.py fetch --date 2024-01-02

# Analyze papers with default settings
python src/main.py analyze --date 2024-01-02

# Analyze with custom OpenRouter settings
python src/main.py analyze --date 2024-01-02 --temperature 0.3 --top-p 0.8
```

### 2. Search Historical Papers
```python
# Search by keyword
python src/main.py search "transformer architecture" --start-date 2024-01-01

# Search by category
python src/main.py search --category cs.AI --start-date 2024-01-01
```
