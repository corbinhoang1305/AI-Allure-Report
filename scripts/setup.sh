#!/bin/bash

echo "==================================="
echo "QUALIFY.AI - Setup Script"
echo "==================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please update .env file with your configuration (especially OPENAI_API_KEY)"
    echo ""
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/shared/migrations/versions
mkdir -p ml-models/models
mkdir -p ml-models/notebooks
mkdir -p ml-models/datasets
echo "✅ Directories created"
echo ""

# Build and start services
echo "🐳 Building and starting Docker containers..."
cd infrastructure/docker-compose
docker-compose up -d postgres redis minio

echo "⏳ Waiting for databases to be ready..."
sleep 10

# Run database migrations
echo "🔄 Running database migrations..."
cd ../../backend
# Uncomment when you have alembic setup
# alembic upgrade head

echo ""
echo "✅ Setup completed!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your OpenAI API key"
echo "2. Start backend services: cd infrastructure/docker-compose && docker-compose up -d"
echo "3. Start frontend: cd frontend && npm install && npm run dev"
echo ""
echo "Access points:"
echo "  - Frontend: http://localhost:3000"
echo "  - API Gateway: http://localhost:8000"
echo "  - MinIO Console: http://localhost:9001"
echo "  - PostgreSQL: localhost:5432"
echo ""

