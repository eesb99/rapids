# Installation Guide

## Prerequisites
- Python 3.10 or higher
- Redis server
- Conda (recommended for environment management)
- OpenRouter API key

## Step-by-Step Installation

### 1. Clone the Repository
```bash
git clone https://github.com/eesb99/rapids.git
cd rapids
```

### 2. Set Up Python Environment
```bash
# Create and activate conda environment
conda env create -f environment.yml
conda activate rapids
```

### 3. Configure API Keys
1. Get OpenRouter API key:
   - Sign up at [OpenRouter](https://openrouter.ai/)
   - Navigate to API Keys section
   - Create a new API key

2. Set up environment variables:
```bash
# Create .env file
echo "OPENROUTER_API_KEY=your-api-key-here" > .env
```

### 4. Redis Installation and Setup

#### Windows
1. Download Redis for Windows:
   - Visit [Redis Downloads](https://github.com/microsoftarchive/redis/releases)
   - Download the latest MSI installer
   - Run the installer

2. Start Redis Service:
   ```bash
   # Start Redis service
   redis-server

   # Verify Redis is running
   redis-cli ping
   # Should respond with "PONG"
   ```

#### Linux
```bash
# For Ubuntu/Debian
sudo apt-get update
sudo apt-get install redis-server

# Start Redis service
sudo systemctl start redis-server

# Enable Redis on startup
sudo systemctl enable redis-server
```

#### MacOS
```bash
# Using Homebrew
brew install redis

# Start Redis service
brew services start redis
```

### 5. Verify Installation

1. Check Python version:
```bash
python --version  # Should be 3.10 or higher
```

2. Verify Redis connection:
```bash
redis-cli ping  # Should return "PONG"
```

3. Test OpenRouter API:
```bash
# Run a test analysis
python src/main.py test-api
```

### 6. Common Issues

1. Python Version Mismatch
```bash
# If using wrong Python version
conda activate rapids
python --version
```

2. Redis Connection Error
```bash
# Check Redis service status on Windows
sc query Redis

# On Linux/MacOS
systemctl status redis-server
```

3. API Key Issues
```bash
# Verify .env file
cat .env

# Test API key
python src/main.py verify-api
```

## Next Steps

1. Review the [Configuration Guide](configuration.md)
2. Try examples in the [Usage Guide](usage.md)
3. Set up your preferred categories in `config/arxiv_config.json`
