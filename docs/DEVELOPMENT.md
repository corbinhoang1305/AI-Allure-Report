# Development Guide

## Development Environment Setup

### Backend Development

#### 1. Setup Python Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Setup Database

```bash
# Start only database services
cd infrastructure/docker-compose
docker-compose up -d postgres redis minio

# Run migrations
cd ../../backend/shared
alembic upgrade head
```

#### 3. Run Individual Services

```bash
# Auth Service
cd backend/services/auth-service
uvicorn app.main:app --reload --port 8001

# Report Aggregator
cd backend/services/report-aggregator
uvicorn app.main:app --reload --port 8002

# AI Analysis Service
cd backend/services/ai-analysis-service
uvicorn app.main:app --reload --port 8003

# Analytics Service
cd backend/services/analytics-service
uvicorn app.main:app --reload --port 8004
```

### Frontend Development

#### 1. Setup Node Environment

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

#### 2. Hot Reload

The Next.js development server supports hot reload. Changes to files will automatically reflect in the browser.

## Project Structure

```
ai-allure-portal/
├── backend/
│   ├── services/          # Microservices
│   │   ├── auth-service/
│   │   ├── report-aggregator/
│   │   ├── ai-analysis-service/
│   │   └── analytics-service/
│   └── shared/            # Shared code
│       ├── config.py
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│       └── utils.py
├── frontend/
│   ├── app/               # Next.js 14 app directory
│   ├── components/        # React components
│   └── lib/               # Utilities
└── infrastructure/
    └── docker-compose/    # Docker configs
```

## Coding Standards

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions and classes
- Use async/await for I/O operations

```python
async def get_test_results(
    test_id: UUID,
    db: AsyncSession
) -> List[TestResult]:
    """
    Retrieve test results by test ID.
    
    Args:
        test_id: UUID of the test
        db: Database session
        
    Returns:
        List of test results
    """
    # Implementation
```

### TypeScript (Frontend)

- Use TypeScript for all files
- Define interfaces for data structures
- Use functional components with hooks
- Follow React best practices

```typescript
interface TestResult {
  id: string;
  name: string;
  status: 'passed' | 'failed';
  duration: number;
}

export function TestList({ results }: { results: TestResult[] }) {
  // Component implementation
}
```

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=services --cov-report=html

# Run specific service tests
pytest services/auth-service/tests/
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run E2E tests
npm run test:e2e
```

## Database Migrations

### Creating a New Migration

```bash
cd backend/shared

# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Migration Best Practices

1. Always review auto-generated migrations
2. Test migrations on development data
3. Write both upgrade and downgrade functions
4. Keep migrations small and focused

## API Development

### Adding a New Endpoint

1. **Define Schema** (in `shared/schemas.py`):

```python
class NewFeatureRequest(BaseModel):
    name: str
    value: int

class NewFeatureResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
```

2. **Create Model** (in `shared/models.py`):

```python
class NewFeature(Base):
    __tablename__ = "new_features"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

3. **Implement Endpoint**:

```python
@app.post("/features", response_model=NewFeatureResponse)
async def create_feature(
    data: NewFeatureRequest,
    db: AsyncSession = Depends(get_db)
):
    feature = NewFeature(**data.dict())
    db.add(feature)
    await db.commit()
    return feature
```

## Debugging

### Backend Debugging

```python
# Add to code for debugging
from shared.utils import logger

logger.debug(f"Processing test: {test_name}")
logger.info(f"Analysis completed: {result}")
logger.error(f"Error occurred: {str(e)}")
```

### Frontend Debugging

```typescript
// Use React DevTools
// Add console logs for debugging
console.log('Test data:', testResults);

// Use browser debugger
debugger;
```

## Performance Optimization

### Backend

1. Use database indexes for frequently queried fields
2. Implement caching with Redis
3. Use async operations for I/O
4. Batch process large datasets

### Frontend

1. Use React.memo for expensive components
2. Implement lazy loading for routes
3. Optimize images and assets
4. Use server-side rendering when appropriate

## Git Workflow

### Branch Naming

- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `hotfix/critical-fix` - Critical production fixes
- `refactor/area-name` - Code refactoring

### Commit Messages

Follow conventional commits:

```
feat: add flaky test detection API
fix: resolve database connection timeout
docs: update API documentation
refactor: simplify authentication logic
test: add unit tests for RCA analyzer
```

### Pull Request Process

1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation
4. Create PR with description
5. Request review
6. Address feedback
7. Merge after approval

## Common Development Tasks

### Adding a New AI Analyzer

1. Create analyzer class in `ai-analysis-service/app/analyzers/`
2. Implement analysis logic
3. Add endpoint in `ai-analysis-service/app/main.py`
4. Update frontend to call new endpoint
5. Add tests

### Adding a New Dashboard Widget

1. Create component in `frontend/components/dashboard/`
2. Add to dashboard page
3. Connect to API
4. Style with Tailwind CSS

## Environment Variables

### Backend

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key
```

### Frontend

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Useful Commands

```bash
# Format Python code
black backend/

# Lint Python code
pylint backend/services/

# Format TypeScript code
cd frontend && npm run format

# Lint TypeScript code
cd frontend && npm run lint

# Build for production
cd frontend && npm run build

# Run database backup
docker exec qualify-postgres pg_dump -U qualify qualify_db > backup.sql
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [React Query Documentation](https://tanstack.com/query/)

