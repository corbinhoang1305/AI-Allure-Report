"""
AI Analysis Service
Provides AI-powered analysis capabilities
"""
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from shared.config import settings
from shared.database import get_db, init_db
from shared.models import TestResult, AIAnalysis, FlakyTest, AnalysisType
from shared.schemas import (
    AIAnalysisCreate, AIAnalysisResponse,
    FlakyTestResponse,
    NLQueryRequest, NLQueryResponse
)
from shared.utils import logger

from .analyzers import (
    RootCauseAnalyzer,
    FlakyTestDetector,
    VisualAnalyzer,
    NLPQueryEngine
)

app = FastAPI(
    title="AI Analysis Service",
    description="AI-powered test analysis and insights",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzers
rca_analyzer = RootCauseAnalyzer()
flaky_detector = FlakyTestDetector()
visual_analyzer = VisualAnalyzer()
nlp_engine = NLPQueryEngine()


# ==================== Request Models ====================

class RCARequest(BaseModel):
    test_result_id: UUID


class FlakyDetectionRequest(BaseModel):
    project_id: UUID
    time_window_days: int = 30


class VisualAnalysisRequest(BaseModel):
    test_result_id: UUID
    baseline_result_id: UUID


# ==================== Startup ====================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    await init_db()
    logger.info("AI Analysis Service started")


# ==================== Root Cause Analysis ====================

@app.post("/analyze/rca", response_model=AIAnalysisResponse)
async def perform_root_cause_analysis(
    request: RCARequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Perform root cause analysis on a failed test
    """
    # Get test result
    result = await db.execute(
        select(TestResult).filter(TestResult.id == request.test_result_id)
    )
    test_result = result.scalar_one_or_none()
    
    if not test_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test result not found"
        )
    
    # Get historical failures
    history_result = await db.execute(
        select(TestResult)
        .filter(TestResult.history_id == test_result.history_id)
        .filter(TestResult.status.in_(["failed", "broken"]))
        .order_by(TestResult.created_at.desc())
        .limit(5)
    )
    historical_failures = history_result.scalars().all()
    
    # Prepare historical context
    historical_context = [
        {
            "date": h.created_at.isoformat(),
            "error_message": h.error_message,
            "stack_trace": h.error_trace
        }
        for h in historical_failures
    ]
    
    # Perform analysis
    analysis_result = await rca_analyzer.analyze_failure(
        test_name=test_result.test_name,
        error_message=test_result.error_message or "",
        stack_trace=test_result.error_trace or "",
        test_description=test_result.description or "",
        historical_failures=historical_context
    )
    
    # Store analysis
    ai_analysis = AIAnalysis(
        test_result_id=test_result.id,
        analysis_type=AnalysisType.ROOT_CAUSE,
        result=analysis_result,
        confidence=analysis_result.get("confidence", 0) / 100,
        model_used=analysis_result.get("analysis_model", ""),
        prompt_used="RCA analysis prompt"
    )
    
    db.add(ai_analysis)
    await db.commit()
    await db.refresh(ai_analysis)
    
    logger.info(f"RCA completed for test result: {test_result.id}")
    
    return ai_analysis


# ==================== Flaky Test Detection ====================

@app.post("/analyze/flaky", response_model=Dict[str, Any])
async def detect_flaky_tests(
    request: FlakyDetectionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Detect flaky tests for a project
    """
    # Get test results for the project
    query = """
        SELECT tr.*, test.history_id, test.test_name, test.status, test.created_at as timestamp
        FROM test_results test
        JOIN test_runs tr ON test.run_id = tr.id
        JOIN test_suites ts ON tr.suite_id = ts.id
        WHERE ts.project_id = :project_id
        AND test.created_at >= NOW() - INTERVAL ':days days'
        ORDER BY test.history_id, test.created_at
    """
    
    result = await db.execute(
        select(TestResult)
        .join(TestResult.run)
        .filter(TestResult.run.has(suite=lambda s: s.project_id == request.project_id))
        .order_by(TestResult.history_id, TestResult.created_at)
    )
    test_history = result.scalars().all()
    
    # Convert to format expected by detector
    history_data = [
        {
            "history_id": t.history_id,
            "test_name": t.test_name,
            "status": t.status.value,
            "timestamp": t.created_at
        }
        for t in test_history
    ]
    
    # Detect flaky tests
    flaky_tests = flaky_detector.detect_flaky_tests(
        history_data,
        time_window_days=request.time_window_days
    )
    
    # Rank by priority
    ranked_flaky_tests = flaky_detector.rank_flaky_tests(flaky_tests)
    
    # Generate report
    report = flaky_detector.generate_flaky_report(
        ranked_flaky_tests,
        time_period=f"{request.time_window_days} days"
    )
    
    # Store flaky tests in database
    for flaky in ranked_flaky_tests[:10]:  # Store top 10
        existing = await db.execute(
            select(FlakyTest).filter(
                FlakyTest.project_id == request.project_id,
                FlakyTest.history_id == flaky["test_id"]
            )
        )
        flaky_record = existing.scalar_one_or_none()
        
        if flaky_record:
            # Update existing
            flaky_record.total_runs = flaky["total_runs"]
            flaky_record.passed_runs = flaky["passed_runs"]
            flaky_record.failed_runs = flaky["failed_runs"]
            flaky_record.flakiness_score = flaky["flakiness_score"]
            flaky_record.last_detected = test_history[0].created_at if test_history else flaky_record.last_detected
            flaky_record.failure_patterns = flaky.get("patterns", {})
        else:
            # Create new
            flaky_record = FlakyTest(
                project_id=request.project_id,
                test_name=flaky["test_name"],
                history_id=flaky["test_id"],
                total_runs=flaky["total_runs"],
                passed_runs=flaky["passed_runs"],
                failed_runs=flaky["failed_runs"],
                flakiness_score=flaky["flakiness_score"],
                failure_patterns=flaky.get("patterns", {})
            )
            db.add(flaky_record)
    
    await db.commit()
    
    logger.info(f"Flaky test detection completed for project: {request.project_id}")
    
    return {
        "report": report,
        "flaky_tests": ranked_flaky_tests
    }


# ==================== Visual Analysis ====================

@app.post("/analyze/visual")
async def perform_visual_analysis(
    test_result_id: UUID,
    baseline_image: UploadFile = File(...),
    current_image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform visual analysis comparing screenshots
    """
    # Get test result
    result = await db.execute(
        select(TestResult).filter(TestResult.id == test_result_id)
    )
    test_result = result.scalar_one_or_none()
    
    if not test_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test result not found"
        )
    
    # Read images
    baseline_data = await baseline_image.read()
    current_data = await current_image.read()
    
    # Perform analysis
    analysis_result = visual_analyzer.compare_screenshots(
        baseline_image=baseline_data,
        current_image=current_data,
        test_name=test_result.test_name
    )
    
    # Store analysis
    ai_analysis = AIAnalysis(
        test_result_id=test_result.id,
        analysis_type=AnalysisType.VISUAL_ANALYSIS,
        result=analysis_result,
        confidence=analysis_result.get("similarity_score", 0),
        model_used="OpenCV Visual Analysis"
    )
    
    db.add(ai_analysis)
    await db.commit()
    
    logger.info(f"Visual analysis completed for test: {test_result.test_name}")
    
    return analysis_result


# ==================== Natural Language Query ====================

@app.post("/query/nl", response_model=NLQueryResponse)
async def process_natural_language_query(
    request: NLQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Process natural language query about test results
    """
    # Build context
    context = {}
    
    if request.project_id:
        # Get project-specific context
        # Add recent results, flaky tests, etc.
        pass
    
    # Add custom context
    if request.context:
        context.update(request.context)
    
    # Process query
    result = await nlp_engine.process_query(request.query, context)
    
    logger.info(f"NLP query processed: {request.query[:50]}")
    
    return NLQueryResponse(
        query=request.query,
        answer=result.get("answer", ""),
        data=result.get("data"),
        confidence=result.get("confidence", 0.5),
        sources=result.get("sources", [])
    )


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-analysis"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)

