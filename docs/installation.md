# Installation Guide

## Prerequisites
- Python 3.8 or higher
- Redis server
- Conda (recommended for environment management)

## Step-by-Step Installation

### 1. Clone the Repository
```bash
git clone [your-repository-url]
cd rapids
```

### 2. Set Up Python Environment
```bash
# Create and activate conda environment
conda env create -f environment.yml
conda activate rapids
```

### 3. Redis Installation and Setup

#### Windows
1. Download Redis for Windows:
   - Visit [Redis Downloads](https://github.com/microsoftarchive/redis/releases)
   - Download the latest MSI installer
   - Run the installer

2. Add Redis to PATH:
   - Open System Properties (Win + R, type `sysdm.cpl`)
   - Click "Environment Variables"
   - Under "System Variables", find and select "Path"
   - Click "Edit" and add the Redis installation directory (typically `C:\Program Files\Redis`)
   - Click "OK" to save

3. Verify Redis Installation:
   ```bash
   redis-cli ping
   # Should respond with "PONG"
   ```

#### Linux/MacOS
```bash
# For Ubuntu/Debian
sudo apt-get install redis-server

# For MacOS
brew install redis
```

### 4. Start Redis Server
```bash
# Windows (if not running as service)
redis-server

# Linux/MacOS
sudo service redis start  # or
brew services start redis
```

### 5. Configure Redis
After installation, see the [Configuration Guide](configuration.md#redis-cache-configuration) for:
- Setting up Redis connection
- Configuring cache settings
- Optimizing performance

### 6. Verify Installation
```bash
# Test Python environment
python src/main.py --help

# Test Redis connection
redis-cli ping
```

## Next Steps
1. Configure your system using the [Configuration Guide](configuration.md)
2. Learn how to use the system in the [Usage Guide](usage.md)
3. Start fetching papers with commands from the [Quick Start Guide](../README.md#quick-start)
