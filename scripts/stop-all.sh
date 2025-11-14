#!/bin/bash

echo "==================================="
echo "Stopping QUALIFY.AI Services"
echo "==================================="
echo ""

cd infrastructure/docker-compose

echo "🛑 Stopping all services..."
docker-compose down

echo ""
echo "✅ All services stopped"
echo ""

