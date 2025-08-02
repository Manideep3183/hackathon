#!/bin/bash

# Aura Development Runner
# This script helps you run the Aura application in development mode

set -e

echo "🚀 Aura Development Runner"
echo "=========================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📋 Please copy .env.example to .env and configure your API keys:"
    echo "   cp .env.example .env"
    echo "   # Edit .env with your actual API keys"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check requirements
echo "🔍 Checking requirements..."

if ! command_exists docker; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command_exists docker-compose; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ All requirements met!"

# Start PostgreSQL first
echo "🐘 Starting PostgreSQL..."
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until docker-compose exec postgres pg_isready -U postgres >/dev/null 2>&1; do
    sleep 1
done
echo "✅ PostgreSQL is ready!"

# Ask user what they want to run
echo ""
echo "What would you like to run?"
echo "1) Full stack (Backend + Frontend + Database) with Docker"
echo "2) Backend only (for frontend development)"
echo "3) Frontend only (assumes backend is running)"
echo "4) Stop all services"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🚀 Starting full stack with Docker..."
        docker-compose up -d
        echo ""
        echo "✅ All services started!"
        echo "🌐 Frontend: http://localhost:3000"
        echo "⚡ Backend API: http://localhost:8000"
        echo "📚 API Docs: http://localhost:8000/docs"
        echo ""
        echo "📋 To view logs: docker-compose logs -f"
        echo "🛑 To stop: docker-compose down"
        ;;
    2)
        echo "⚡ Starting backend only..."
        docker-compose up -d backend
        echo ""
        echo "✅ Backend started!"
        echo "⚡ Backend API: http://localhost:8000"
        echo "📚 API Docs: http://localhost:8000/docs"
        echo ""
        echo "📋 To view logs: docker-compose logs -f backend"
        ;;
    3)
        echo "🌐 Frontend development mode..."
        echo "📋 Make sure to:"
        echo "   1. cd frontend"
        echo "   2. npm install"
        echo "   3. npm run dev"
        echo ""
        echo "🌐 Frontend will be available at: http://localhost:3000"
        ;;
    4)
        echo "🛑 Stopping all services..."
        docker-compose down
        echo "✅ All services stopped!"
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac