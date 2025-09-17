#!/bin/bash

# Memory-Man Installation Script
set -e

echo "🧠 Installing Memory-Man..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.10+ required, found $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements-core.txt

# Test the installation
echo "🧪 Testing installation..."
python test_server.py

# Create data directory
mkdir -p data

echo ""
echo "🎉 Memory-Man installed successfully!"
echo ""
echo "Next steps:"
echo "1. Configure Claude Code (see integration_guide.md)"
echo "2. Add to your Claude Code MCP configuration:"
echo ""
echo "   ~/.claude/mcp_servers.json:"
echo "   {"
echo "     \"mcpServers\": {"
echo "       \"memory-man\": {"
echo "         \"command\": \"python\","
echo "         \"args\": [\"-m\", \"memory_man\"],"
echo "         \"env\": {"
echo "           \"PYTHONPATH\": \"$(pwd)/src\""
echo "         }"
echo "       }"
echo "     }"
echo "   }"
echo ""
echo "3. Restart Claude Code"
echo "4. Start storing memories!"
echo ""
echo "📖 Read README.md and integration_guide.md for more details."