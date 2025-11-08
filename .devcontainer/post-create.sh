#!/bin/bash
set -e

echo "🏇 Setting up Racing Analysis environment..."

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -e ".[dev]"

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/{raw,processed,features,models,betfair_historic,qual_claims}
mkdir -p data/raw/{races,markets,weather,stewards,gear}
mkdir -p logs

# Initialize DuckDB database
echo "🗄️  Initializing database..."
python scripts/setup_db.py

# Create .env from template if it doesn't exist
if [ ! -f .env ]; then
    echo "🔐 Creating .env from template..."
    cp .env.example .env
fi

# Run tests to verify setup
echo "✅ Running initial tests..."
pytest tests/ -v || echo "⚠️  Some tests failed - this is expected on first setup"

echo "✨ Setup complete! Ready to build."
