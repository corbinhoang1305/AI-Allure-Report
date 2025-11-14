# QUALIFY.AI - Architecture Overview

## System Architecture

QUALIFY.AI is built using a microservices architecture pattern, with each service responsible for a specific domain of functionality.

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│                  Next.js 14 + TypeScript                     │
│              Tailwind CSS + shadcn/ui + Recharts            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
│                    Nginx / Kong                              │
│               Load Balancing + Routing                       │
└────────┬────────┬────────┬────────┬──────────────────────────┘
         │        │        │        │
    ┌────▼────┐ ┌▼────┐ ┌▼────┐ ┌▼─────────┐
    │  Auth   │ │Rep. │ │ AI  │ │Analytics │
    │ Service │ │Aggr.│ │Svc  │ │ Service  │
    └────┬────┘ └┬────┘ └┬────┘ └┬─────────┘
         │       │       │       │
         └───────┴───────┴───────┘
                     │
        ┌────────────┴────────────┐
        │                         │
   ┌────▼─────┐            ┌─────▼─────┐
   │PostgreSQL│            │   Redis   │
   │          │            │   Cache   │
   └──────────┘            └───────────┘
        │
   ┌────▼─────┐
   │  MinIO   │
   │ S3 Store │
   └──────────┘
```

## Core Services

### 1. Auth Service (Port 8001)
**Responsibility:** User authentication and authorization

**Technologies:**
- FastAPI
- JWT tokens
- PostgreSQL
- bcrypt for password hashing

**Key Features:**
- User registration and login
- JWT token generation and validation
- Role-based access control (RBAC)
- Token refresh mechanism

**Endpoints:**
- `POST /register` - User registration
- `POST /token` - Login and get access token
- `POST /refresh` - Refresh access token
- `GET /me` - Get current user info
- `GET /users` - List users (admin only)

### 2. Report Aggregator Service (Port 8002)
**Responsibility:** Parse, aggregate, and store Allure test reports

**Technologies:**
- FastAPI
- SQLAlchemy (async)
- MinIO for file storage
- Custom Allure parser

**Key Features:**
- Parse Allure JSON/XML reports
- Extract test results, attachments, metadata
- Store historical test data
- Support ZIP file uploads
- Project and test suite management

**Endpoints:**
- `POST /projects` - Create project
- `GET /projects` - List projects
- `POST /suites` - Create test suite
- `POST /upload` - Upload Allure report
- `GET /runs/{run_id}/results` - Get test results
- `GET /tests/{history_id}/history` - Get test history

### 3. AI Analysis Service (Port 8003)
**Responsibility:** AI-powered test analysis and insights

**Technologies:**
- FastAPI
- OpenAI GPT-4
- LangChain
- OpenCV (for visual analysis)
- scikit-learn (for predictions)

**Key Features:**
- **Root Cause Analysis (RCA):** Analyze failure patterns
- **Flaky Test Detection:** Identify unstable tests
- **Visual Analysis:** Compare UI screenshots
- **Natural Language Queries:** Ask questions about test data
- **Predictive Analytics:** Forecast failure trends

**Endpoints:**
- `POST /analyze/rca` - Perform root cause analysis
- `POST /analyze/flaky` - Detect flaky tests
- `POST /analyze/visual` - Visual comparison
- `POST /query/nl` - Natural language query

### 4. Analytics Service (Port 8004)
**Responsibility:** Metrics, trends, and dashboard data

**Technologies:**
- FastAPI
- SQLAlchemy
- PostgreSQL + TimescaleDB (optional)
- Aggregation queries

**Key Features:**
- Overall quality health metrics
- Historical trend analysis
- Project statistics
- Failure analysis
- Performance metrics

**Endpoints:**
- `GET /dashboard` - Main dashboard data
- `GET /projects/{id}/stats` - Project statistics
- `GET /projects/{id}/trends` - Historical trends
- `GET /tests/{id}/metrics` - Test metrics
- `GET /projects/{id}/failures` - Failure analysis

## Data Layer

### PostgreSQL Database

**Schema Structure:**

```sql
users
├── id (UUID)
├── email
├── username
├── hashed_password
├── role (enum: admin, developer, viewer)
└── is_active

projects
├── id (UUID)
├── name
├── description
├── repository_url
└── metadata (JSONB)

test_suites
├── id (UUID)
├── project_id (FK)
├── name
└── path

test_runs
├── id (UUID)
├── suite_id (FK)
├── run_id
├── status
├── started_at
├── finished_at
├── environment
├── build_number
└── metadata (JSONB)

test_results
├── id (UUID)
├── run_id (FK)
├── test_name
├── status
├── duration_ms
├── error_message
├── error_trace
├── labels (JSONB)
├── parameters (JSONB)
├── attachments (JSONB)
└── history_id (for tracking)

ai_analyses
├── id (UUID)
├── test_result_id (FK)
├── analysis_type (enum)
├── result (JSONB)
├── confidence
└── model_used

flaky_tests
├── id (UUID)
├── project_id (FK)
├── test_name
├── history_id
├── total_runs
├── passed_runs
├── failed_runs
├── flakiness_score
└── failure_patterns (JSONB)
```

### Redis Cache

**Usage:**
- Session storage
- Rate limiting
- Temporary data caching
- WebSocket state (future)

### MinIO Object Storage

**Storage Structure:**
```
allure-reports/
├── screenshots/
│   ├── {test_id}/{timestamp}.png
├── logs/
│   ├── {test_id}/{timestamp}.log
├── videos/
│   ├── {test_id}/{timestamp}.mp4
└── reports/
    ├── {project_id}/{run_id}/
```

## Frontend Architecture

### Technology Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS + shadcn/ui
- **Charts:** Recharts + D3.js
- **State Management:** Zustand
- **Data Fetching:** React Query
- **HTTP Client:** Axios

### Component Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home (redirects to dashboard)
│   ├── dashboard/
│   │   └── page.tsx            # Main dashboard
│   ├── projects/
│   │   ├── page.tsx            # Projects list
│   │   └── [id]/page.tsx       # Project details
│   ├── flaky-tests/
│   └── rca/
├── components/
│   ├── ui/                     # Base UI components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── ...
│   ├── layout/
│   │   └── Sidebar.tsx         # Navigation sidebar
│   └── dashboard/
│       ├── QualityHealthCircle.tsx
│       ├── TrendChart.tsx
│       ├── AIInsightsPanel.tsx
│       ├── ProjectGrid.tsx
│       └── RecentTestRuns.tsx
└── lib/
    ├── api-client.ts           # API client
    └── utils.ts                # Utility functions
```

### Data Flow

```
User Action
    ↓
React Component
    ↓
React Query (useQuery/useMutation)
    ↓
API Client (axios)
    ↓
API Gateway (Nginx)
    ↓
Backend Service
    ↓
Database/Cache
    ↓
Response
    ↓
React Query Cache
    ↓
UI Update
```

## AI/ML Pipeline

### Root Cause Analysis Flow

```
1. Test Failure Detected
   ↓
2. Extract Context
   - Error message
   - Stack trace
   - Historical failures
   ↓
3. Build AI Prompt
   - Test information
   - Error details
   - Historical patterns
   ↓
4. OpenAI API Call
   - Model: GPT-4
   - Temperature: 0.7
   ↓
5. Parse Response
   - Root cause
   - Confidence score
   - Recommendations
   ↓
6. Store Analysis
   - Save to database
   - Link to test result
   ↓
7. Display to User
```

### Flaky Test Detection Algorithm

```python
def detect_flaky(test_history):
    """
    Flakiness Score Calculation:
    
    score = (minority_status_count / total_runs) * confidence_factor
    
    Where:
    - minority_status_count = min(passed_runs, failed_runs)
    - confidence_factor = min(total_runs / 10, 1.0)
    
    Threshold: 0.2 (20% flakiness)
    """
    
    # Pattern detection:
    # 1. Alternating pass/fail
    # 2. Environment-specific failures
    # 3. Time-based patterns
    # 4. Consecutive failures
```

### Visual Analysis Process

```
1. Receive Screenshots
   - Baseline (passing test)
   - Current (failed test)
   ↓
2. Image Preprocessing
   - Resize to same dimensions
   - Convert to grayscale
   ↓
3. Similarity Calculation
   - PSNR (Peak Signal-to-Noise Ratio)
   - Normalize to 0-1 score
   ↓
4. Difference Detection
   - Absolute difference
   - Threshold to binary
   - Find contours
   ↓
5. Analysis
   - Categorize differences (small/medium/large)
   - Calculate coverage percentage
   - Determine severity
   ↓
6. Generate Diff Image
   - Highlight differences in red
   - Create visual report
```

## Security

### Authentication Flow

```
1. User Login
   ↓
2. Validate Credentials
   ↓
3. Generate JWT Tokens
   - Access Token (30 min)
   - Refresh Token (7 days)
   ↓
4. Return Tokens
   ↓
5. Client Stores Tokens
   ↓
6. Include in Requests
   - Header: Authorization: Bearer {token}
   ↓
7. Token Validation
   - Verify signature
   - Check expiration
   - Extract user info
```

### Security Measures

- **Password Hashing:** bcrypt with salt
- **JWT Tokens:** HS256 algorithm
- **HTTPS:** TLS 1.3 in production
- **Rate Limiting:** Per-IP and per-user limits
- **CORS:** Configured allowed origins
- **SQL Injection:** Parameterized queries
- **XSS Protection:** Content Security Policy
- **API Keys:** Encrypted in database

## Scalability

### Horizontal Scaling

Each microservice can be scaled independently:

```yaml
# Kubernetes example
replicas:
  auth-service: 2
  report-aggregator: 4
  ai-analysis: 3
  analytics: 2
```

### Caching Strategy

```
Level 1: Browser Cache
  ↓
Level 2: CDN (static assets)
  ↓
Level 3: Redis (API responses)
  ↓
Level 4: Database Query Cache
```

### Performance Targets

- Dashboard load: < 2 seconds
- API response: < 500ms (p95)
- AI analysis: < 30 seconds
- Concurrent users: 100+
- Tests per project: 10,000+

## Deployment

### Docker Compose (Development)

```bash
docker-compose up -d
```

### Kubernetes (Production)

```
Frontend (3 replicas)
   ↓
Ingress Controller
   ↓
Services (auto-scaling)
   ↓
PostgreSQL (StatefulSet)
Redis (StatefulSet)
MinIO (StatefulSet)
```

### CI/CD Pipeline

```
1. Code Push
   ↓
2. Run Tests
   ↓
3. Build Docker Images
   ↓
4. Push to Registry
   ↓
5. Deploy to Staging
   ↓
6. Integration Tests
   ↓
7. Deploy to Production
```

## Monitoring & Observability

### Metrics

- **Application Metrics:** Prometheus
- **Logs:** ELK Stack (Elasticsearch, Logstash, Kibana)
- **Traces:** Jaeger (distributed tracing)
- **Dashboards:** Grafana

### Health Checks

Each service exposes:
- `GET /health` - Basic health check
- `GET /metrics` - Prometheus metrics

## Future Enhancements

1. **Real-time Updates:** WebSocket integration
2. **Advanced ML Models:** Custom trained models
3. **Plugin System:** External integrations
4. **Multi-tenancy:** Organization support
5. **Advanced Analytics:** Predictive failure models
6. **CI/CD Integration:** Jenkins, GitLab CI, GitHub Actions plugins

