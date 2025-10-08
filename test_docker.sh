#!/bin/bash
# Test script for Docker setup
# This script validates the Docker configuration without requiring GPU

set -e

echo "🧪 Testing Docker configuration for docstrange..."
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi
echo "✅ Docker is installed: $(docker --version)"

# Validate Dockerfile syntax
echo ""
echo "📄 Validating Dockerfile syntax..."
if [ ! -f Dockerfile ]; then
    echo "❌ Dockerfile not found"
    exit 1
fi

# Check for required instructions
if ! grep -q "^FROM nvidia/cuda" Dockerfile; then
    echo "❌ Dockerfile missing CUDA base image"
    exit 1
fi

if ! grep -q "CMD.*docstrange.web_app" Dockerfile; then
    echo "❌ Dockerfile missing web_app start command"
    exit 1
fi
echo "✅ Dockerfile syntax looks good"

# Validate docker-compose.yml
echo ""
echo "📄 Validating docker-compose.yml..."
if [ ! -f docker-compose.yml ]; then
    echo "❌ docker-compose.yml not found"
    exit 1
fi

# Check for GPU configuration
if ! grep -q "nvidia" docker-compose.yml; then
    echo "❌ docker-compose.yml missing GPU configuration"
    exit 1
fi
echo "✅ docker-compose.yml looks good"

# Check .dockerignore
echo ""
echo "📄 Checking .dockerignore..."
if [ ! -f .dockerignore ]; then
    echo "⚠️  .dockerignore not found (optional but recommended)"
else
    echo "✅ .dockerignore exists"
fi

# Check documentation
echo ""
echo "📄 Checking documentation..."
if [ ! -f DOCKER.md ]; then
    echo "⚠️  DOCKER.md not found"
else
    echo "✅ DOCKER.md exists"
fi

# Check if project files exist
echo ""
echo "📄 Checking required project files..."
required_files=(
    "pyproject.toml"
    "docstrange/web_app.py"
    "docstrange/__init__.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file missing: $file"
        exit 1
    fi
done
echo "✅ All required project files exist"

# Summary
echo ""
echo "================================================"
echo "✅ All Docker configuration tests passed!"
echo "================================================"
echo ""
echo "To build and run the Docker container:"
echo ""
echo "  # Using docker-compose (recommended):"
echo "  docker-compose up -d"
echo ""
echo "  # Or using Docker CLI:"
echo "  docker build -t docstrange-web ."
echo "  docker run --gpus all -p 8000:8000 docstrange-web"
echo ""
echo "Note: GPU support requires:"
echo "  - NVIDIA Docker runtime installed"
echo "  - NVIDIA GPU with CUDA support"
echo "  - NVIDIA drivers 450.80.02 or later"
echo ""
echo "For more information, see DOCKER.md"
