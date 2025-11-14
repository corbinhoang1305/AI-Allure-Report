"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


# ==================== Enums ====================

class TestStatusEnum(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    BROKEN = "broken"
    SKIPPED = "skipped"
    UNKNOWN = "unknown"


class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class AnalysisTypeEnum(str, Enum):
    ROOT_CAUSE = "root_cause"
    FLAKY_DETECTION = "flaky_detection"
    VISUAL_ANALYSIS = "visual_analysis"
    PREDICTIVE = "predictive"
    BUG_TRIAGE = "bug_triage"


# ==================== User Schemas ====================

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRoleEnum = UserRoleEnum.DEVELOPER


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRoleEnum] = None


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


# ==================== Project Schemas ====================

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    repository_url: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    repository_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ProjectResponse(ProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)


# ==================== Test Suite Schemas ====================

class TestSuiteBase(BaseModel):
    name: str
    path: Optional[str] = None
    description: Optional[str] = None


class TestSuiteCreate(TestSuiteBase):
    project_id: UUID


class TestSuiteResponse(TestSuiteBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== Test Run Schemas ====================

class TestRunBase(BaseModel):
    suite_id: UUID
    run_id: str
    status: TestStatusEnum
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    environment: Optional[str] = None
    build_number: Optional[str] = None
    branch: Optional[str] = None


class TestRunCreate(TestRunBase):
    metadata: Optional[Dict[str, Any]] = None


class TestRunResponse(TestRunBase):
    id: UUID
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== Test Result Schemas ====================

class TestResultBase(BaseModel):
    test_name: str
    full_name: Optional[str] = None
    status: TestStatusEnum
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None
    error_trace: Optional[str] = None
    description: Optional[str] = None


class TestResultCreate(TestResultBase):
    run_id: UUID
    labels: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    history_id: Optional[str] = None
    retry_count: int = 0


class TestResultResponse(TestResultBase):
    id: UUID
    run_id: UUID
    labels: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    history_id: Optional[str] = None
    retry_count: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TestResultWithAnalysis(TestResultResponse):
    ai_analyses: List["AIAnalysisResponse"] = []


# ==================== AI Analysis Schemas ====================

class AIAnalysisBase(BaseModel):
    analysis_type: AnalysisTypeEnum
    result: Dict[str, Any]
    confidence: Optional[float] = None


class AIAnalysisCreate(AIAnalysisBase):
    test_result_id: UUID
    prompt_used: Optional[str] = None
    model_used: Optional[str] = None
    similar_issues: Optional[List[Dict[str, Any]]] = None


class AIAnalysisResponse(AIAnalysisBase):
    id: UUID
    test_result_id: UUID
    model_used: Optional[str] = None
    similar_issues: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== Dashboard Schemas ====================

class ProjectStats(BaseModel):
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    pass_rate: float
    avg_duration_ms: int
    total_runs: int


class DashboardResponse(BaseModel):
    overall_health: Dict[str, Any]
    pass_rate: float
    recent_trends: List[Dict[str, Any]]
    flaky_tests: List[Dict[str, Any]]
    ai_insights: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]


class TrendDataPoint(BaseModel):
    timestamp: datetime
    pass_rate: float
    total_tests: int
    failed_tests: int
    duration_ms: int


class HistoricalTrend(BaseModel):
    period: str  # "24h", "7d", "30d"
    data_points: List[TrendDataPoint]


# ==================== Flaky Test Schemas ====================

class FlakyTestBase(BaseModel):
    test_name: str
    history_id: str
    flakiness_score: float


class FlakyTestResponse(FlakyTestBase):
    id: UUID
    project_id: UUID
    total_runs: int
    passed_runs: int
    failed_runs: int
    first_detected: datetime
    last_detected: datetime
    is_active: bool
    failure_patterns: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)


# ==================== Natural Language Query ====================

class NLQueryRequest(BaseModel):
    query: str
    project_id: Optional[UUID] = None
    context: Optional[Dict[str, Any]] = None


class NLQueryResponse(BaseModel):
    query: str
    answer: str
    data: Optional[Dict[str, Any]] = None
    confidence: float
    sources: List[str] = []


# ==================== Pagination ====================

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== Allure Report Upload ====================

class AllureReportUpload(BaseModel):
    project_id: UUID
    suite_id: UUID
    environment: Optional[str] = "default"
    build_number: Optional[str] = None
    branch: Optional[str] = "main"


class AllureReportUploadResponse(BaseModel):
    run_id: UUID
    message: str
    tests_processed: int
    tests_failed: int
    tests_passed: int

