#!/bin/bash

# Deployment script for Autonomous Product Factory

set -e

echo "🏭 Deploying Autonomous Product Factory..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "   Copy .env.example to .env and configure your API keys"
    exit 1
fi

# Load environment variables
source .env

# Check required environment variables
required_vars=("OPENAI_API_KEY" "GITHUB_TOKEN")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var is not set in .env"
        exit 1
    fi
done

echo "✅ Environment variables validated"

# Create necessary directories
mkdir -p data logs

echo "✅ Directories created"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

echo "✅ Dependencies installed"

# Initialize database
echo "🗄️  Initializing database..."
python -c "from database.models import init_db; init_db()"

echo "✅ Database initialized"

# Run tests (if they exist)
if [ -d "tests" ] && [ -n "$(ls -A tests/*.py 2>/dev/null)" ]; then
    echo "🧪 Running tests..."
    python -m pytest tests/ -v || echo "⚠️  Some tests failed, but continuing..."
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🚀 To start the dashboard:"
echo "   streamlit run dashboard/app.py"
echo ""
echo "🤖 To start the automated scheduler:"
echo "   python orchestration/scheduler.py"
echo ""
