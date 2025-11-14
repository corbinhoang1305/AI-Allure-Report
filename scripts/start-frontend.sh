#!/bin/bash

echo "==================================="
echo "Starting QUALIFY.AI Frontend"
echo "==================================="
echo ""

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "🚀 Starting Next.js development server..."
npm run dev

