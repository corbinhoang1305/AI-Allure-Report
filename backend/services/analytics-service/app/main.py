"""
Analytics Service
Provides metrics, trends, and dashboard data
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from shared.config import settings
from shared.database import get_db, init_db
from shared.models import Project, TestSuite, TestRun, TestResult, FlakyTest, TestStatus
from shared.schemas import DashboardResponse, ProjectStats, HistoricalTrend, TrendDataPoint
from shared.utils import logger, calculate_pass_rate

app = FastAPI(
    title="Analytics Service",
    description="Test analytics and metrics",
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


# ==================== Startup ====================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    await init_db()
    logger.info("Analytics Service started")


# ==================== Dashboard ====================

@app.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard(
    project_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive dashboard data
    """
    # Get overall health
    overall_health = await get_overall_health(project_id, db)
    
    # Get recent trends (30 days)
    trends = await get_trends(project_id, "30d", db)
    
    # Get flaky tests
    flaky_query = select(FlakyTest).filter(FlakyTest.is_active == True)
    if project_id:
        flaky_query = flaky_query.filter(FlakyTest.project_id == project_id)
    flaky_query = flaky_query.order_by(FlakyTest.flakiness_score.desc()).limit(10)
    
    result = await db.execute(flaky_query)
    flaky_tests = result.scalars().all()
    
    # Get projects summary
    projects_summary = await get_projects_summary(db)
    
    # Get failed tests data (last 7 days, latest run only)
    failed_tests_data = await get_failed_tests_data(project_id, db)
    failed_test_names = [ft["name"] for ft in failed_tests_data[:5]]
    
    # Get recent runs
    recent_runs = await get_recent_runs(project_id, db)
    
    # AI insights (placeholder - would call AI service)
    ai_insights = [
        {
            "type": "flaky_detection",
            "count": len(flaky_tests),
            "message": f"{len(flaky_tests)} flaky tests detected"
        }
    ]
    
    return {
        "overall_health": overall_health,
        "pass_rate": overall_health.get("pass_rate", 0),
        "recent_trends": trends,
        "flaky_tests": [
            {
                "name": ft.test_name,
                "score": ft.flakiness_score,
                "runs": ft.total_runs
            }
            for ft in flaky_tests
        ],
        "failed_test_names": failed_test_names,
        "failed_tests_data": failed_tests_data,
        "recent_runs": recent_runs,
        "ai_insights": ai_insights,
        "projects": projects_summary
    }


async def get_overall_health(
    project_id: Optional[UUID],
    db: AsyncSession
) -> Dict[str, Any]:
    """Calculate overall quality health with proper flaky detection"""
    # Get recent test results (last 7 days)
    cutoff_date = datetime.utcnow() - timedelta(days=7)
    
    query = select(TestResult).join(TestResult.run).filter(
        TestResult.created_at >= cutoff_date
    )
    
    if project_id:
        query = query.join(TestRun.suite).filter(TestSuite.project_id == project_id)
    
    result = await db.execute(query)
    recent_results = result.scalars().all()
    
    if not recent_results:
        return {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "flaky": 0,
            "pass_rate": 0,
            "avg_duration_ms": 0
        }
    
    # Group by history_id to identify unique test cases and their retries
    test_cases = {}
    for r in recent_results:
        test_key = r.history_id or r.full_name or r.test_name
        if test_key not in test_cases:
            test_cases[test_key] = []
        test_cases[test_key].append(r)
    
    # Categorize each test case
    passed_count = 0
    flaky_count = 0
    failed_count = 0
    total_duration = 0
    
    for test_key, results_list in test_cases.items():
        # Sort by created_at
        results_list.sort(key=lambda x: x.created_at)
        
        num_runs = len(results_list)
        first_status = results_list[0].status
        final_status = results_list[-1].status
        
        # Calculate average duration for this test
        durations = [r.duration_ms or 0 for r in results_list]
        if durations:
            total_duration += sum(durations) / len(durations)
        
        # Logic verified from analyze_allure_folder.py:
        # - Passed: Test ran ONCE and passed
        # - Flaky: Test FAILED first, then PASSED on retry
        # - Failed: Test failed (with or without retry)
        
        if num_runs == 1:
            # Single run - no retry
            if first_status == TestStatus.PASSED:
                # Passed: ran once and passed
                passed_count += 1
            else:
                # Failed: ran once and failed
                failed_count += 1
        else:
            # Multiple runs - has retry
            if first_status in [TestStatus.FAILED, TestStatus.BROKEN]:
                # First run failed
                if final_status == TestStatus.PASSED:
                    # Flaky: failed first, then passed on retry
                    flaky_count += 1
                else:
                    # Failed: failed first, and still failed after retry
                    failed_count += 1
            elif first_status == TestStatus.PASSED:
                # First run passed but has multiple runs
                # Treat as Passed (stable - likely duplicate data import)
                passed_count += 1
    
    total_tests = passed_count + flaky_count + failed_count
    avg_duration = int(total_duration / total_tests) if total_tests > 0 else 0
    
    return {
        "total_tests": total_tests,
        "passed": passed_count,
        "failed": failed_count,
        "flaky": flaky_count,
        "pass_rate": calculate_pass_rate(passed_count + flaky_count, total_tests),
        "avg_duration_ms": avg_duration
    }


async def get_trends(
    project_id: Optional[UUID],
    period: str,
    db: AsyncSession
) -> List[Dict[str, Any]]:
    """Get historical trends - returns full period with zeros for days without data"""
    # Parse period
    days = 7
    if period == "24h":
        days = 1
    elif period == "30d":
        days = 30
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get test runs
    query = select(TestRun).filter(TestRun.started_at >= cutoff_date)
    
    if project_id:
        query = query.join(TestRun.suite).filter(TestSuite.project_id == project_id)
    
    query = query.order_by(TestRun.started_at)
    
    result = await db.execute(query)
    runs = result.scalars().all()
    
    # Group by day - calculate from actual test_results
    # Get ALL test results from ALL runs (not just latest run)
    # This allows us to detect retries within the same day
    daily_stats = {}
    
    # Get ALL run IDs (not just latest)
    all_run_ids = [run.id for run in runs]
    
    if all_run_ids:
        from sqlalchemy import and_, func
        results_query = select(TestResult, TestRun).join(
            TestRun, TestResult.run_id == TestRun.id
        ).filter(TestResult.run_id.in_(all_run_ids))
        
        results = await db.execute(results_query)
        test_results_with_runs = results.all()
        
        # Group by history_id to analyze retries and categorize test cases
        # Logic:
        # - Passed: test ran once and passed
        # - Flaky: test passed eventually but had retries (passed after fail)
        # - Failed: test failed even with retries OR failed once without retry
        test_cases_by_date = {}
        
        for test_result, test_run in test_results_with_runs:
            date_key = test_run.started_at.date().isoformat()
            
            if date_key not in test_cases_by_date:
                test_cases_by_date[date_key] = {}
            
            # Use history_id as unique key for test case
            test_key = test_result.history_id or test_result.full_name or test_result.test_name
            
            # Collect ALL results for each test case (not just the latest)
            if test_key not in test_cases_by_date[date_key]:
                test_cases_by_date[date_key][test_key] = []
            
            test_cases_by_date[date_key][test_key].append((test_result, test_run))
        
        # Analyze each test case to determine if it's Passed, Flaky, or Failed
        for date_key, test_cases in test_cases_by_date.items():
            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    "date": date_key,
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "flaky": 0
                }
            
            for test_key, results_list in test_cases.items():
                # Sort by created_at to get chronological order
                results_list.sort(key=lambda x: x[0].created_at)
                
                daily_stats[date_key]["total"] += 1
                
                # Analyze the results for this test case
                num_runs = len(results_list)
                first_status = results_list[0][0].status
                final_status = results_list[-1][0].status
                
                # Logic verified from analyze_allure_folder.py:
                # - Passed: Test ran ONCE and passed
                # - Flaky: Test FAILED first, then PASSED on retry
                # - Failed: Test failed (with or without retry)
                
                if num_runs == 1:
                    # Single run - no retry
                    if first_status == TestStatus.PASSED:
                        # Passed: ran once and passed
                        daily_stats[date_key]["passed"] += 1
                    else:
                        # Failed: ran once and failed (no retry attempted)
                        daily_stats[date_key]["failed"] += 1
                else:
                    # Multiple runs - has retry
                    if first_status in [TestStatus.FAILED, TestStatus.BROKEN]:
                        # First run failed
                        if final_status == TestStatus.PASSED:
                            # Flaky: failed first, then passed on retry
                            daily_stats[date_key]["flaky"] += 1
                        else:
                            # Failed: failed first, and still failed after retry
                            daily_stats[date_key]["failed"] += 1
                    elif first_status == TestStatus.PASSED:
                        # First run passed but has multiple runs
                        # Treat as Passed (stable - likely duplicate data import)
                        daily_stats[date_key]["passed"] += 1
    
    # Fill all days in the period, even if no data
    trends = []
    today = datetime.utcnow().date()
    
    for i in range(days - 1, -1, -1):  # From (days-1) days ago to today
        current_date = today - timedelta(days=i)
        date_key = current_date.isoformat()
        
        if date_key in daily_stats:
            stat = daily_stats[date_key]
            trends.append({
                "date": date_key,
                "total": stat["total"],
                "passed": stat["passed"],
                "failed": stat["failed"],
                "flaky": stat["flaky"],
                "pass_rate": calculate_pass_rate(stat["passed"] + stat["flaky"], stat["total"])
            })
        else:
            # No data for this day - add zeros
            trends.append({
                "date": date_key,
                "total": 0,
                "passed": 0,
                "failed": 0,
                "flaky": 0,
                "pass_rate": 0
            })
    
    return trends


async def get_projects_summary(db: AsyncSession) -> List[Dict[str, Any]]:
    """Get summary for all projects"""
    result = await db.execute(select(Project))
    projects = result.scalars().all()
    
    summaries = []
    
    for project in projects:
        # Get recent results for this project
        stats = await get_project_stats(project.id, db)
        
        summaries.append({
            "id": str(project.id),
            "name": project.name,
            "pass_rate": stats.get("pass_rate", 0),
            "total_tests": stats.get("total_tests", 0),
            "failed_tests": stats.get("failed_tests", 0)
        })
    
    return summaries


async def get_failed_tests_data(
    project_id: Optional[UUID],
    db: AsyncSession
) -> List[Dict[str, Any]]:
    """Get failed tests data for dashboard"""
    # Get failed tests from latest run of each day (last 7 days)
    cutoff_date = datetime.utcnow() - timedelta(days=7)
    
    # Build query to get failed tests directly with joins, including run date/time
    if project_id:
        # Join through suite to filter by project
        failed_query = select(
            TestResult,
            TestRun.started_at.label("run_started_at"),
            TestRun.finished_at.label("run_finished_at"),
            TestRun.created_at.label("run_created_at")
        ).join(
            TestRun, TestResult.run_id == TestRun.id
        ).join(
            TestSuite, TestRun.suite_id == TestSuite.id
        ).filter(
            and_(
                TestSuite.project_id == project_id,
                TestRun.started_at >= cutoff_date,
                TestResult.status.in_([TestStatus.FAILED, TestStatus.BROKEN])
            )
        ).order_by(TestResult.created_at.desc()).limit(20)
    else:
        # No project filter - get from all projects
        failed_query = select(
            TestResult,
            TestRun.started_at.label("run_started_at"),
            TestRun.finished_at.label("run_finished_at"),
            TestRun.created_at.label("run_created_at")
        ).join(
            TestRun, TestResult.run_id == TestRun.id
        ).filter(
            and_(
                TestRun.started_at >= cutoff_date,
                TestResult.status.in_([TestStatus.FAILED, TestStatus.BROKEN])
            )
        ).order_by(TestResult.created_at.desc()).limit(20)
    
    failed_result = await db.execute(failed_query)
    failed_tests_with_runs = failed_result.all()
    
    # Convert to frontend format
    failed_tests_data = []
    for test, run_started_at, run_finished_at, run_created_at in failed_tests_with_runs:
        # Convert datetime to timestamp (milliseconds)
        run_started_timestamp = int(run_started_at.timestamp() * 1000) if run_started_at else 0
        run_finished_timestamp = int(run_finished_at.timestamp() * 1000) if run_finished_at else 0
        test_created_timestamp = int(test.created_at.timestamp() * 1000) if test.created_at else run_started_timestamp
        
        # Safely access attributes without lazy loading
        failed_tests_data.append({
            "uuid": str(test.id),  # Database UUID
            "allureUuid": test.allure_uuid or "",  # Original Allure UUID from result.json
            "name": test.test_name or "Unknown Test",
            "fullName": test.full_name or test.test_name or "Unknown Test",
            "status": test.status.value.lower() if test.status else "unknown",
            "statusDetails": {
                "message": test.error_message or "No error message available",
                "trace": test.error_trace or ""
            },
            "time": {
                "start": test_created_timestamp,
                "stop": run_finished_timestamp if run_finished_timestamp > 0 else test_created_timestamp + (test.duration_ms or 0),
                "duration": test.duration_ms or 0
            },
            "runDate": run_started_at.isoformat() if run_started_at else None,
            "runStartedAt": run_started_at.isoformat() if run_started_at else None,
            "runFinishedAt": run_finished_at.isoformat() if run_finished_at else None,
            "createdAt": test.created_at.isoformat() if test.created_at else None,
            "labels": test.labels if test.labels else [],
            "parameters": test.parameters if test.parameters else [],
            "attachments": test.attachments if test.attachments else [],
            "description": test.description or "",
            "historyId": test.history_id or "",
            "testCaseId": test.history_id or ""
        })
    
    return failed_tests_data


async def get_recent_runs(
    project_id: Optional[UUID],
    db: AsyncSession
) -> List[Dict[str, Any]]:
    """Get recent test runs for dashboard"""
    cutoff_date = datetime.utcnow() - timedelta(days=7)
    
    # Build query with explicit joins to avoid lazy loading
    if project_id:
        query = select(TestRun, TestSuite.name.label("suite_name")).join(
            TestSuite, TestRun.suite_id == TestSuite.id
        ).filter(
            and_(
                TestSuite.project_id == project_id,
                TestRun.started_at >= cutoff_date
            )
        ).order_by(TestRun.started_at.desc()).limit(5)
    else:
        query = select(TestRun, TestSuite.name.label("suite_name")).join(
            TestSuite, TestRun.suite_id == TestSuite.id
        ).filter(
            TestRun.started_at >= cutoff_date
        ).order_by(TestRun.started_at.desc()).limit(5)
    
    result = await db.execute(query)
    runs_with_suites = result.all()
    
    recent_runs = []
    for run, suite_name in runs_with_suites:
        # Get stats from test results
        stats_query = select(TestResult).filter(TestResult.run_id == run.id)
        stats_result = await db.execute(stats_query)
        test_results = stats_result.scalars().all()
        
        passed = sum(1 for r in test_results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in test_results if r.status in [TestStatus.FAILED, TestStatus.BROKEN])
        
        recent_runs.append({
            "suite": suite_name or "Unknown Suite",
            "date": run.started_at.date().isoformat(),
            "passed": passed,
            "failed": failed,
            "status": "passed" if failed == 0 else "failed"
        })
    
    return recent_runs


# ==================== Project Stats ====================

@app.get("/projects/{project_id}/stats")
async def get_project_stats(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get statistics for a specific project"""
    # Get recent test results (last 30 days)
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    
    query = select(TestResult).join(TestResult.run).join(TestRun.suite).filter(
        and_(
            TestSuite.project_id == project_id,
            TestResult.created_at >= cutoff_date
        )
    )
    
    result = await db.execute(query)
    results = result.scalars().all()
    
    total = len(results)
    if total == 0:
        return {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "pass_rate": 0,
            "avg_duration_ms": 0,
            "total_runs": 0
        }
    
    passed = sum(1 for r in results if r.status == TestStatus.PASSED)
    failed = sum(1 for r in results if r.status in [TestStatus.FAILED, TestStatus.BROKEN])
    skipped = sum(1 for r in results if r.status == TestStatus.SKIPPED)
    
    avg_duration = sum(r.duration_ms or 0 for r in results) / total
    
    # Get unique runs
    run_ids = set(r.run_id for r in results)
    
    return {
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": failed,
        "skipped_tests": skipped,
        "pass_rate": calculate_pass_rate(passed, total),
        "avg_duration_ms": int(avg_duration),
        "total_runs": len(run_ids)
    }


# ==================== Trends ====================

@app.get("/projects/{project_id}/trends")
async def get_project_trends(
    project_id: UUID,
    period: str = "30d",
    db: AsyncSession = Depends(get_db)
):
    """Get historical trends for a project"""
    trends = await get_trends(project_id, period, db)
    
    return {
        "period": period,
        "data_points": trends
    }


# ==================== Test History ====================

@app.get("/tests/{history_id}/metrics")
async def get_test_metrics(
    history_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get metrics for a specific test over time"""
    # Get all results for this test
    result = await db.execute(
        select(TestResult)
        .filter(TestResult.history_id == history_id)
        .order_by(TestResult.created_at.desc())
        .limit(100)
    )
    results = result.scalars().all()
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    
    total_runs = len(results)
    passed_runs = sum(1 for r in results if r.status == TestStatus.PASSED)
    failed_runs = sum(1 for r in results if r.status in [TestStatus.FAILED, TestStatus.BROKEN])
    
    # Calculate average duration
    durations = [r.duration_ms for r in results if r.duration_ms]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    # Get recent trend
    recent_results = results[:10]
    recent_status = [r.status.value for r in recent_results]
    
    return {
        "test_name": results[0].test_name,
        "history_id": history_id,
        "total_runs": total_runs,
        "passed_runs": passed_runs,
        "failed_runs": failed_runs,
        "pass_rate": calculate_pass_rate(passed_runs, total_runs),
        "avg_duration_ms": int(avg_duration),
        "recent_trend": recent_status,
        "last_run": results[0].created_at.isoformat() if results else None
    }


# ==================== Failure Analysis ====================

@app.get("/projects/{project_id}/failures")
async def get_failure_analysis(
    project_id: UUID,
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """Get analysis of test failures"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get failed tests
    query = select(TestResult).join(TestResult.run).join(TestRun.suite).filter(
        and_(
            TestSuite.project_id == project_id,
            TestResult.status.in_([TestStatus.FAILED, TestStatus.BROKEN]),
            TestResult.created_at >= cutoff_date
        )
    )
    
    result = await db.execute(query)
    failures = result.scalars().all()
    
    # Analyze failures
    error_categories = {}
    failing_tests = {}
    
    for failure in failures:
        # Categorize by error type
        error_msg = failure.error_message or "Unknown error"
        category = categorize_error(error_msg)
        
        error_categories[category] = error_categories.get(category, 0) + 1
        
        # Track individual test failures
        test_name = failure.test_name
        if test_name not in failing_tests:
            failing_tests[test_name] = {
                "name": test_name,
                "failures": 0,
                "last_error": error_msg
            }
        failing_tests[test_name]["failures"] += 1
    
    # Get top failing tests
    top_failures = sorted(
        failing_tests.values(),
        key=lambda x: x["failures"],
        reverse=True
    )[:10]
    
    return {
        "time_period": f"{days} days",
        "total_failures": len(failures),
        "unique_tests_failed": len(failing_tests),
        "error_categories": error_categories,
        "top_failing_tests": top_failures
    }


def categorize_error(error_message: str) -> str:
    """Categorize error by type"""
    error_lower = error_message.lower()
    
    if "timeout" in error_lower:
        return "Timeout"
    elif "null" in error_lower or "none" in error_lower:
        return "Null/None Error"
    elif "connection" in error_lower or "network" in error_lower:
        return "Connection Error"
    elif "assertion" in error_lower or "expected" in error_lower:
        return "Assertion Failure"
    elif "not found" in error_lower or "404" in error_lower:
        return "Not Found"
    elif "500" in error_lower or "internal server" in error_lower:
        return "Server Error"
    else:
        return "Other"


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "analytics"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)

