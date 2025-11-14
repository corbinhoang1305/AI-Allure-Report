# QUALIFY.AI - Quick Start Guide

This guide will help you get QUALIFY.AI up and running in just a few minutes.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (20.10+) and **Docker Compose** (1.29+)
- **Node.js** (18+) and **npm** (9+)
- **Python** (3.11+) - for local development
- **OpenAI API Key** - Required for AI features

## Quick Start (Using Docker)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-allure-portal
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use your preferred editor
```

**Important:** Update the following in `.env`:
- `OPENAI_API_KEY` - Your OpenAI API key
- `SECRET_KEY` - Generate a secure random string (min 32 characters)

### 3. Run Setup Script

```bash
chmod +x scripts/*.sh
./scripts/setup.sh
```

### 4. Start Backend Services

```bash
./scripts/start-backend.sh
```

This will start:
- PostgreSQL database
- Redis cache
- MinIO object storage
- Auth service
- Report aggregator service
- AI analysis service
- Analytics service
- Nginx API gateway

### 5. Start Frontend

In a new terminal:

```bash
./scripts/start-frontend.sh
```

### 6. Access the Application

Open your browser and navigate to:

**Frontend:** http://localhost:3000

**API Documentation:**
- Auth Service: http://localhost:8001/docs
- Report Aggregator: http://localhost:8002/docs
- AI Analysis: http://localhost:8003/docs
- Analytics: http://localhost:8004/docs

**MinIO Console:** http://localhost:9001
- Username: `minioadmin`
- Password: `minioadmin123`

## First Steps

### 1. Create an Account

Navigate to http://localhost:3000 and register a new account.

### 2. Create Your First Project

1. Click on "Projects" in the sidebar
2. Click "New Project"
3. Fill in project details:
   - Name: e.g., "My Test Project"
   - Description: Optional
   - Repository URL: Optional

### 3. Upload Your First Allure Report

```bash
# Using curl
curl -X POST http://localhost:8000/api/reports/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/allure-results.zip" \
  -F "project_id=YOUR_PROJECT_ID" \
  -F "suite_id=YOUR_SUITE_ID"
```

Or use the web interface:
1. Go to "Projects" → Select your project
2. Click "Upload Report"
3. Select your Allure results ZIP file
4. Submit

### 4. Explore AI Features

Once you have test results uploaded:

1. **Root Cause Analysis:** Navigate to a failed test and click "Analyze with AI"
2. **Flaky Test Detection:** Go to "Flaky Tests (AI)" to see detected flaky tests
3. **Natural Language Query:** Use the AI chat box on the dashboard to ask questions like:
   - "Show me all failed tests in the last week"
   - "Why did test_login fail?"
   - "What's the trend for the payment module?"

## Troubleshooting

### Services won't start

```bash
# Check service logs
cd infrastructure/docker-compose
docker-compose logs [service-name]

# Common issues:
# - Port already in use: Change ports in docker-compose.yml
# - Database connection: Ensure postgres is healthy
```

### Frontend can't connect to backend

1. Check if backend services are running:
   ```bash
   docker-compose ps
   ```

2. Verify API_BASE_URL in `frontend/.env.local`:
   ```
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

### AI features not working

1. Verify OpenAI API key is set in `.env`
2. Check AI service logs:
   ```bash
   docker-compose logs ai-analysis
   ```

## Stopping Services

```bash
# Stop all services
./scripts/stop-all.sh

# Or manually
cd infrastructure/docker-compose
docker-compose down

# To remove volumes (WARNING: This deletes all data)
docker-compose down -v
```

## Next Steps

- Read the [Architecture Documentation](./architecture/overview.md)
- Learn about [API Integration](./api/README.md)
- Explore [AI Features](./features/ai-capabilities.md)
- Check [Deployment Guide](./deployment.md) for production setup

## Getting Help

- Documentation: `/docs`
- Issues: GitHub Issues
- Community: Discord/Slack (if available)

---

**Happy Testing! 🚀**

