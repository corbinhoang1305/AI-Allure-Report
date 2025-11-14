#!/bin/bash

echo "==================================="
echo "Starting QUALIFY.AI Backend Services"
echo "==================================="
echo ""

cd infrastructure/docker-compose

echo "🚀 Starting all backend services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ Backend services started!"
echo ""
echo "Service URLs:"
echo "  - Auth Service: http://localhost:8001"
echo "  - Report Aggregator: http://localhost:8002"
echo "  - AI Analysis: http://localhost:8003"
echo "  - Analytics: http://localhost:8004"
echo "  - API Gateway: http://localhost:8000"
echo "  - MinIO Console: http://localhost:9001 (admin/minioadmin123)"
echo ""
echo "To view logs: docker-compose logs -f [service-name]"
echo "To stop services: docker-compose down"
echo ""

