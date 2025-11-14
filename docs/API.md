# API Documentation

## Base URL

- **Development:** `http://localhost:8000`
- **Production:** `https://api.qualify.ai`

## Authentication

All API requests (except `/register` and `/token`) require authentication using JWT tokens.

### Headers

```
Authorization: Bearer {access_token}
Content-Type: application/json
```

## API Endpoints

### Authentication

#### Register User

```http
POST /api/auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword123",
  "full_name": "John Doe",
  "role": "developer"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "developer",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Login

```http
POST /api/auth/token
```

**Request Body (Form Data):**
```
username=johndoe
password=securepassword123
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Projects

#### Create Project

```http
POST /api/reports/projects
```

**Request Body:**
```json
{
  "name": "My Test Project",
  "description": "E2E tests for web app",
  "repository_url": "https://github.com/org/repo"
}
```

**Response:** `201 Created`

#### List Projects

```http
GET /api/reports/projects
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "My Test Project",
    "description": "E2E tests for web app",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Test Reports

#### Upload Allure Report

```http
POST /api/reports/upload
```

**Request (Multipart Form Data):**
```
file: allure-results.zip
project_id: uuid
suite_id: uuid
environment: staging
build_number: 123
branch: main
```

**Response:** `200 OK`
```json
{
  "run_id": "uuid",
  "message": "Report processed successfully",
  "tests_processed": 150,
  "tests_failed": 12,
  "tests_passed": 138
}
```

#### Get Test History

```http
GET /api/reports/tests/{history_id}/history?limit=50
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "test_name": "test_login",
    "status": "passed",
    "duration_ms": 1234,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### AI Analysis

#### Root Cause Analysis

```http
POST /api/ai/analyze/rca
```

**Request Body:**
```json
{
  "test_result_id": "uuid"
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "test_result_id": "uuid",
  "analysis_type": "root_cause",
  "result": {
    "root_cause": "Database connection timeout due to connection pool exhaustion",
    "confidence": 85,
    "category": "Infrastructure",
    "recommended_actions": [
      "Increase database connection pool size",
      "Add connection retry logic",
      "Monitor connection usage"
    ]
  },
  "confidence": 0.85,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Detect Flaky Tests

```http
POST /api/ai/analyze/flaky
```

**Request Body:**
```json
{
  "project_id": "uuid",
  "time_window_days": 30
}
```

**Response:** `200 OK`
```json
{
  "report": {
    "total_flaky_tests": 7,
    "average_flakiness_score": 0.35,
    "priority_breakdown": {
      "Critical": 2,
      "High": 3,
      "Medium": 2
    }
  },
  "flaky_tests": [
    {
      "test_name": "test_checkout",
      "flakiness_score": 0.45,
      "total_runs": 50,
      "priority": "Critical",
      "recommendation": "Critical: Test is highly unstable..."
    }
  ]
}
```

#### Natural Language Query

```http
POST /api/ai/query/nl
```

**Request Body:**
```json
{
  "query": "Show me all failed tests related to login in the last week",
  "project_id": "uuid"
}
```

**Response:** `200 OK`
```json
{
  "query": "Show me all failed tests related to login...",
  "answer": "Found 5 failed tests related to login in the past 7 days...",
  "data": {
    "tests": [...]
  },
  "confidence": 0.9,
  "sources": ["test_results", "ai_analyses"]
}
```

### Analytics

#### Dashboard Data

```http
GET /api/analytics/dashboard?project_id={uuid}
```

**Response:** `200 OK`
```json
{
  "overall_health": {
    "total_tests": 1000,
    "passed": 880,
    "failed": 120,
    "pass_rate": 88.0,
    "avg_duration_ms": 45000
  },
  "recent_trends": [
    {
      "date": "2024-01-01",
      "passed": 150,
      "failed": 10,
      "pass_rate": 93.8
    }
  ],
  "flaky_tests": [...],
  "projects": [...]
}
```

#### Project Statistics

```http
GET /api/analytics/projects/{project_id}/stats
```

**Response:** `200 OK`
```json
{
  "total_tests": 500,
  "passed_tests": 450,
  "failed_tests": 50,
  "skipped_tests": 0,
  "pass_rate": 90.0,
  "avg_duration_ms": 35000,
  "total_runs": 100
}
```

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized

```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden

```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found

```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

- **Rate Limit:** 60 requests per minute per user
- **Headers:**
  - `X-RateLimit-Limit: 60`
  - `X-RateLimit-Remaining: 45`
  - `X-RateLimit-Reset: 1640995200`

## Pagination

For endpoints that return lists:

```http
GET /api/endpoint?page=1&page_size=20
```

**Response:**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

## Webhooks (Future)

Subscribe to events:

- `test.run.completed`
- `test.failed`
- `flaky.test.detected`
- `analysis.completed`

## SDKs

### Python

```python
from qualify_ai import QualifyClient

client = QualifyClient(api_key="your-api-key")

# Upload report
result = client.reports.upload(
    file_path="allure-results.zip",
    project_id="uuid",
    suite_id="uuid"
)

# Get dashboard
dashboard = client.analytics.get_dashboard(project_id="uuid")
```

### JavaScript/TypeScript

```typescript
import { QualifyClient } from '@qualify-ai/sdk';

const client = new QualifyClient({ apiKey: 'your-api-key' });

// Upload report
const result = await client.reports.upload({
  file: fileBlob,
  projectId: 'uuid',
  suiteId: 'uuid',
});

// Get dashboard
const dashboard = await client.analytics.getDashboard({ projectId: 'uuid' });
```

## Interactive API Documentation

Visit the auto-generated Swagger/OpenAPI documentation:

- **Auth Service:** http://localhost:8001/docs
- **Report Aggregator:** http://localhost:8002/docs
- **AI Analysis:** http://localhost:8003/docs
- **Analytics:** http://localhost:8004/docs

