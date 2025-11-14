"""
Shared database models
"""
from sqlalchemy import Column, String, DateTime, Integer, Float, JSON, ForeignKey, Text, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from .database import Base


class TestStatus(str, enum.Enum):
    """Test execution status"""
    PASSED = "passed"
    FAILED = "failed"
    BROKEN = "broken"
    SKIPPED = "skipped"
    UNKNOWN = "unknown"


class UserRole(str, enum.Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class AnalysisType(str, enum.Enum):
    """AI analysis types"""
    ROOT_CAUSE = "root_cause"
    FLAKY_DETECTION = "flaky_detection"
    VISUAL_ANALYSIS = "visual_analysis"
    PREDICTIVE = "predictive"
    BUG_TRIAGE = "bug_triage"


# ==================== User Management ====================

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.DEVELOPER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== Project & Test Structure ====================

class Project(Base):
    """Project/Application being tested"""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    repository_url = Column(String(500))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)
    
    # Relationships
    test_suites = relationship("TestSuite", back_populates="project", cascade="all, delete-orphan")
    

class TestSuite(Base):
    """Test suite within a project"""
    __tablename__ = "test_suites"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    path = Column(String(500))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="test_suites")
    test_runs = relationship("TestRun", back_populates="suite", cascade="all, delete-orphan")


class TestRun(Base):
    """Individual test run execution"""
    __tablename__ = "test_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    suite_id = Column(UUID(as_uuid=True), ForeignKey("test_suites.id"), nullable=False)
    run_id = Column(String(255), nullable=False, index=True)  # Allure run ID
    status = Column(Enum(TestStatus), nullable=False)
    started_at = Column(DateTime, nullable=False, index=True)
    finished_at = Column(DateTime)
    duration_ms = Column(Integer)
    environment = Column(String(100))  # dev, staging, prod
    build_number = Column(String(100))
    branch = Column(String(255))
    meta_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    suite = relationship("TestSuite", back_populates="test_runs")
    test_results = relationship("TestResult", back_populates="run", cascade="all, delete-orphan")


class TestResult(Base):
    """Individual test case result"""
    __tablename__ = "test_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("test_runs.id"), nullable=False, index=True)
    test_name = Column(String(500), nullable=False, index=True)
    full_name = Column(Text)  # Full qualified test name
    status = Column(Enum(TestStatus), nullable=False, index=True)
    duration_ms = Column(Integer)
    
    # Error information
    error_message = Column(Text)
    error_trace = Column(Text)
    
    # Test metadata
    description = Column(Text)
    labels = Column(JSONB)  # Tags, categories, etc.
    parameters = Column(JSONB)
    
    # Attachments
    attachments = Column(JSONB)  # References to screenshots, logs, etc.
    
    # History
    history_id = Column(String(255), index=True)  # For tracking same test over time
    retry_count = Column(Integer, default=0)
    
    # Original Allure UUID from result.json file (for mapping back to source file)
    allure_uuid = Column(String(255), index=True, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    run = relationship("TestRun", back_populates="test_results")
    ai_analyses = relationship("AIAnalysis", back_populates="test_result", cascade="all, delete-orphan")


# ==================== AI Analysis ====================

class AIAnalysis(Base):
    """AI analysis results for test failures"""
    __tablename__ = "ai_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_result_id = Column(UUID(as_uuid=True), ForeignKey("test_results.id"), nullable=False, index=True)
    analysis_type = Column(Enum(AnalysisType), nullable=False, index=True)
    
    # Analysis results
    result = Column(JSONB, nullable=False)
    confidence = Column(Float)  # 0.0 to 1.0
    
    # Context
    prompt_used = Column(Text)
    model_used = Column(String(100))
    
    # Similar issues
    similar_issues = Column(JSONB)  # References to similar past failures
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    test_result = relationship("TestResult", back_populates="ai_analyses")


# ==================== Flaky Test Tracking ====================

class FlakyTest(Base):
    """Tracking flaky tests"""
    __tablename__ = "flaky_tests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    test_name = Column(String(500), nullable=False, index=True)
    history_id = Column(String(255), nullable=False, index=True)
    
    # Flakiness metrics
    total_runs = Column(Integer, default=0)
    passed_runs = Column(Integer, default=0)
    failed_runs = Column(Integer, default=0)
    flakiness_score = Column(Float)  # 0.0 to 1.0
    
    # Time windows
    first_detected = Column(DateTime, default=datetime.utcnow)
    last_detected = Column(DateTime, default=datetime.utcnow)
    
    # Status
    is_active = Column(Boolean, default=True)
    resolved_at = Column(DateTime)
    
    # Additional info
    failure_patterns = Column(JSONB)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== Attachments (Screenshots, Logs) ====================

class Attachment(Base):
    """File attachments (screenshots, logs, videos)"""
    __tablename__ = "attachments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_result_id = Column(UUID(as_uuid=True), ForeignKey("test_results.id"), nullable=False)
    
    # File information
    filename = Column(String(500), nullable=False)
    file_type = Column(String(100))  # screenshot, log, video, etc.
    mime_type = Column(String(100))
    file_size = Column(Integer)
    
    # Storage
    storage_path = Column(String(1000), nullable=False)  # S3/MinIO path
    storage_bucket = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow)

