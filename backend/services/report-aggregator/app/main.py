"""
Report Aggregator Service
Handles Allure report parsing and storage
"""
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from shared.config import settings
from shared.database import get_db, init_db
from shared.models import Project, TestSuite, TestRun, TestResult, TestStatus
from shared.schemas import (
    ProjectCreate, ProjectResponse, ProjectUpdate,
    TestSuiteCreate, TestSuiteResponse,
    TestRunCreate, TestRunResponse,
    TestResultCreate, TestResultResponse,
    AllureReportUploadResponse
)
from shared.utils import logger, generate_uuid

from .parsers.allure_parser import AllureParser, AllureAggregator

app = FastAPI(
    title="Report Aggregator Service",
    description="Parse and aggregate Allure test reports",
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

parser = AllureParser()
aggregator = AllureAggregator()

# Scheduler for automatic folder scanning
scheduler = AsyncIOScheduler()
SCAN_INTERVAL_MINUTES = int(os.getenv("SCAN_INTERVAL_MINUTES", "2"))  # Default 2 minutes


# ==================== Helper Functions ====================

def _deduplicate_retries(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Group retries by testCaseId and keep only the latest result
    """
    test_cases = {}
    
    for result in results:
        key = result.get("testCaseId") or result.get("historyId") or result.get("fullName", result.get("name", ""))
        
        if key not in test_cases:
            test_cases[key] = []
        
        test_cases[key].append(result)
    
    # Keep latest result for each test case (by stop time)
    final_results = []
    for key, results_list in test_cases.items():
        # Sort by stop time (latest first)
        results_list.sort(key=lambda x: x.get("time", {}).get("stop", 0), reverse=True)
        final_results.append(results_list[0])
    
    return final_results


# ==================== Background Tasks ====================

async def auto_scan_and_import():
    """Automatically scan and import reports from folder"""
    try:
        logger.info(f"🔍 Auto-scanning {settings.ALLURE_REPORTS_PATH} for new reports...")
        
        reports_path = Path(settings.ALLURE_REPORTS_PATH)
        
        if not reports_path.exists():
            logger.warning(f"Reports folder not found: {reports_path}")
            return
        
        # Get all date folders
        folders_to_process = [d for d in reports_path.iterdir() if d.is_dir()]
        
        if not folders_to_process:
            logger.info("No folders found to process")
            return
        
        # Use database session
        from shared.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            try:
                imported_count = 0
                
                for folder in folders_to_process:
                    folder_date = folder.name
                    
                    # Skip non-date folders (like test-results-node-18, etc.)
                    if not any(char.isdigit() for char in folder_date):
                        continue
                    
                    # Check if this folder was already imported today
                    # (We'll import all folders, but skip if already processed recently)
                    
                    # Parse date from folder name
                    try:
                        date_parts = folder_date.split('-')
                        if len(date_parts) == 3:
                            day, month, year = date_parts
                            folder_datetime = datetime(int(year), int(month), int(day))
                        else:
                            folder_datetime = datetime.fromtimestamp(folder.stat().st_mtime)
                    except Exception as e:
                        logger.warning(f"Could not parse date from folder {folder_date}: {e}")
                        folder_datetime = datetime.fromtimestamp(folder.stat().st_mtime)
                    
                    # Check if we already have a run for this folder today
                    from datetime import timedelta
                    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    existing_run = await db.execute(
                        select(TestRun)
                        .filter(TestRun.build_number == folder_date)
                        .filter(TestRun.created_at >= today_start)
                    )
                    
                    if existing_run.scalar_one_or_none():
                        logger.debug(f"Folder {folder_date} already imported today, skipping")
                        continue
                    
                    # Import this folder
                    project_name = "Default Project"
                    suite_name = folder_date
                    
                    # Get or create project
                    project_result = await db.execute(
                        select(Project).filter(Project.name == project_name)
                    )
                    project = project_result.scalar_one_or_none()
                    
                    if not project:
                        project = Project(
                            name=project_name,
                            description=f"Auto-imported from {folder_date}",
                            meta_data={"imported_from": str(folder)}
                        )
                        db.add(project)
                        await db.flush()
                    
                    # Get or create test suite
                    suite_result = await db.execute(
                        select(TestSuite)
                        .filter(TestSuite.project_id == project.id)
                        .filter(TestSuite.name == suite_name)
                    )
                    suite = suite_result.scalar_one_or_none()
                    
                    if not suite:
                        suite = TestSuite(
                            project_id=project.id,
                            name=suite_name,
                            description=f"Test suite for {folder_date}"
                        )
                        db.add(suite)
                        await db.flush()
                    
                    # Parse all result files in folder
                    try:
                        test_results = parser.parse_results_directory(str(folder))
                        
                        if not test_results:
                            logger.debug(f"No test results found in {folder_date}")
                            continue
                        
                        # Aggregate statistics
                        stats = aggregator.aggregate_reports(test_results)
                        
                        # Create test run
                        run_id = generate_uuid()
                        test_run = TestRun(
                            suite_id=suite.id,
                            run_id=run_id,
                            status=TestStatus.PASSED if stats['failed'] == 0 else TestStatus.FAILED,
                            started_at=folder_datetime,
                            finished_at=folder_datetime,
                            duration_ms=stats['total_duration_ms'],
                            environment="auto-imported",
                            build_number=folder_date,
                            branch="main",
                            meta_data={
                                "stats": stats,
                                "folder": str(folder),
                                "date_folder": folder_date,
                                "auto_imported": True
                            }
                        )
                        
                        db.add(test_run)
                        await db.flush()
                        
                        # Store individual test results (already deduplicated by parser)
                        flaky_detected = []
                        
                        for test_result_data in test_results:
                            error_info = parser.extract_error_info(test_result_data.get("statusDetails", {}))
                            
                            # Get testCaseId for flaky detection
                            test_case_id = test_result_data.get("testCaseId") or test_result_data.get("historyId")
                            is_flaky = test_result_data.get("is_flaky", False)
                            
                            test_result = TestResult(
                                run_id=test_run.id,
                                test_name=test_result_data["name"],
                                full_name=test_result_data["fullName"],
                                status=test_result_data["status"],
                                duration_ms=test_result_data["time"]["duration"],
                                error_message=error_info["message"],
                                error_trace=error_info["trace"],
                                description=test_result_data.get("description", ""),
                                labels=test_result_data.get("labels", {}),
                                parameters=test_result_data.get("parameters", {}),
                                attachments=test_result_data.get("attachments", []),
                                history_id=test_result_data["historyId"],
                                allure_uuid=test_result_data.get("uuid")  # Store original Allure UUID
                            )
                            
                            db.add(test_result)
                            
                            # Track flaky tests for later processing
                            if is_flaky and test_case_id:
                                logger.debug(f"Found flaky test: {test_result_data['name']}, retry_count: {test_result_data.get('retry_count', 0)}")
                                flaky_detected.append({
                                    "test_case_id": test_case_id,
                                    "test_name": test_result_data["name"],
                                    "history_id": test_result_data["historyId"],
                                    "retry_count": test_result_data.get("retry_count", 0),
                                    "retry_statuses": test_result_data.get("retry_statuses", [])
                                })
                        
                        await db.flush()
                        
                        # Store flaky tests if detected
                        if flaky_detected:
                            logger.info(f"💾 Storing {len(flaky_detected)} flaky tests...")
                            from shared.models import FlakyTest
                            
                            for flaky_info in flaky_detected:
                                # Check if flaky test already exists
                                existing_flaky_query = select(FlakyTest).filter(
                                    FlakyTest.project_id == project.id,
                                    FlakyTest.history_id == flaky_info["history_id"]
                                )
                                existing_flaky_result = await db.execute(existing_flaky_query)
                                flaky_record = existing_flaky_result.scalar_one_or_none()
                                
                                # Calculate stats from retry_statuses
                                passed_count = sum(1 for s in flaky_info["retry_statuses"] if s.lower() in ["passed"])
                                failed_count = sum(1 for s in flaky_info["retry_statuses"] if s.lower() in ["failed", "broken"])
                                total_count = len(flaky_info["retry_statuses"])
                                flakiness_score = min(passed_count, failed_count) / total_count if total_count > 0 else 0
                                
                                if flaky_record:
                                    # Update existing - add new retry data
                                    flaky_record.total_runs += total_count
                                    flaky_record.passed_runs += passed_count
                                    flaky_record.failed_runs += failed_count
                                    # Recalculate flakiness score
                                    total_runs = flaky_record.total_runs
                                    flaky_record.flakiness_score = min(flaky_record.passed_runs, flaky_record.failed_runs) / total_runs if total_runs > 0 else 0
                                    flaky_record.last_detected = datetime.utcnow()
                                    flaky_record.is_active = True
                                else:
                                    # Create new flaky test record
                                    flaky_record = FlakyTest(
                                        project_id=project.id,
                                        test_name=flaky_info["test_name"],
                                        history_id=flaky_info["history_id"],
                                        total_runs=total_count,
                                        passed_runs=passed_count,
                                        failed_runs=failed_count,
                                        flakiness_score=flakiness_score,
                                        is_active=True
                                    )
                                    db.add(flaky_record)
                            
                            await db.flush()
                            logger.info(f"💾 Stored flaky test: {flaky_info['test_name']} (score: {flakiness_score:.2f})")
                        
                        await db.commit()
                        imported_count += 1
                        
                        logger.info(f"✅ Auto-imported {len(test_results)} test results from {folder_date}")
                        
                    except Exception as e:
                        logger.error(f"Error importing from {folder_date}: {str(e)}")
                        await db.rollback()
                        continue
                
                if imported_count > 0:
                    logger.info(f"✅ Auto-scan completed: imported {imported_count} folders")
                else:
                    logger.info("✅ Auto-scan completed: no new folders to import")
                    
            except Exception as db_error:
                logger.error(f"Database error in auto_scan: {str(db_error)}")
                await db.rollback()
                
    except Exception as e:
        logger.error(f"Error in auto_scan_and_import: {str(e)}")


# ==================== Startup ====================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    await init_db()
    
    # Start scheduler for automatic folder scanning
    logger.info(f"📂 Auto-scan folder: {settings.ALLURE_REPORTS_PATH}")
    logger.info(f"⏰ Auto-scan interval: {SCAN_INTERVAL_MINUTES} minutes")
    
    scheduler.add_job(
        auto_scan_and_import,
        'interval',
        minutes=SCAN_INTERVAL_MINUTES,
        id='auto_scan_allure_reports',
        replace_existing=True
    )
    
    # Run initial scan after a short delay
    async def delayed_scan():
        await asyncio.sleep(5)
        await auto_scan_and_import()
    
    asyncio.create_task(delayed_scan())
    
    # Start scheduler
    scheduler.start()
    
    logger.info("✅ Report Aggregator Service started with auto-scan enabled")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    scheduler.shutdown()
    logger.info("Report Aggregator Service stopped")


# ==================== Project Management ====================

@app.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new project"""
    
    db_project = Project(
        name=project.name,
        description=project.description,
        repository_url=project.repository_url
    )
    
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    
    logger.info(f"Project created: {project.name}")
    return db_project


@app.get("/projects", response_model=List[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    """List all projects"""
    
    result = await db.execute(select(Project))
    projects = result.scalars().all()
    
    return projects


@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get project by ID"""
    
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


@app.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update project"""
    
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project_update.name:
        project.name = project_update.name
    if project_update.description:
        project.description = project_update.description
    if project_update.repository_url:
        project.repository_url = project_update.repository_url
    
    await db.commit()
    await db.refresh(project)
    
    return project


# ==================== Test Suite Management ====================

@app.post("/suites", response_model=TestSuiteResponse, status_code=status.HTTP_201_CREATED)
async def create_test_suite(
    suite: TestSuiteCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new test suite"""
    
    db_suite = TestSuite(
        project_id=suite.project_id,
        name=suite.name,
        path=suite.path,
        description=suite.description
    )
    
    db.add(db_suite)
    await db.commit()
    await db.refresh(db_suite)
    
    logger.info(f"Test suite created: {suite.name}")
    return db_suite


@app.get("/projects/{project_id}/suites", response_model=List[TestSuiteResponse])
async def list_project_suites(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """List all suites for a project"""
    
    result = await db.execute(
        select(TestSuite).filter(TestSuite.project_id == project_id)
    )
    suites = result.scalars().all()
    
    return suites


# ==================== Report Upload & Processing ====================

@app.post("/upload", response_model=AllureReportUploadResponse)
async def upload_allure_report(
    project_id: UUID = Form(...),
    suite_id: UUID = Form(...),
    environment: Optional[str] = Form("default"),
    build_number: Optional[str] = Form(None),
    branch: Optional[str] = Form("main"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and process Allure report
    Accepts ZIP file containing Allure results
    """
    
    # Verify project and suite exist
    project_result = await db.execute(select(Project).filter(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    suite_result = await db.execute(select(TestSuite).filter(TestSuite.id == suite_id))
    suite = suite_result.scalar_one_or_none()
    
    if not suite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test suite not found"
        )
    
    # Read file content
    content = await file.read()
    
    # Parse results (will be deduplicated if directory contains retries)
    try:
        if file.filename.endswith('.zip'):
            # For ZIP files, parse and deduplicate retries
            raw_results = parser.parse_zip_file(content)
            # Group by testCaseId and keep latest
            test_results = _deduplicate_retries(raw_results)
        elif file.filename.endswith('.json'):
            # Single JSON file - no deduplication needed
            test_results = [parser.parse_json_content(content.decode('utf-8'))]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format. Please upload ZIP or JSON file."
            )
    except Exception as e:
        logger.error(f"Error parsing report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing report: {str(e)}"
        )
    
    # Aggregate statistics
    stats = aggregator.aggregate_reports(test_results)
    
    # Create test run
    run_id = generate_uuid()
    test_run = TestRun(
        suite_id=suite_id,
        run_id=run_id,
        status=TestStatus.PASSED if stats['failed'] == 0 else TestStatus.FAILED,
        started_at=datetime.fromtimestamp(stats['start_time'] / 1000) if stats['start_time'] > 0 else datetime.utcnow(),
        finished_at=datetime.fromtimestamp(stats['end_time'] / 1000) if stats['end_time'] > 0 else datetime.utcnow(),
        duration_ms=stats['total_duration_ms'],
        environment=environment,
        build_number=build_number,
        branch=branch,
        meta_data={
            "stats": stats,
            "original_filename": file.filename
        }
    )
    
    db.add(test_run)
    await db.flush()
    
    # Store individual test results
    for test_result_data in test_results:
        error_info = parser.extract_error_info(test_result_data.get("statusDetails", {}))
        
        test_result = TestResult(
            run_id=test_run.id,
            test_name=test_result_data["name"],
            full_name=test_result_data["fullName"],
            status=test_result_data["status"],
            duration_ms=test_result_data["time"]["duration"],
            error_message=error_info["message"],
            error_trace=error_info["trace"],
            description=test_result_data["description"],
            labels=test_result_data["labels"],
            parameters=test_result_data["parameters"],
            attachments=test_result_data["attachments"],
            history_id=test_result_data["historyId"],
            allure_uuid=test_result_data.get("uuid")  # Store original Allure UUID
        )
        
        db.add(test_result)
    
    await db.commit()
    
    logger.info(f"Processed {len(test_results)} test results for run {run_id}")
    
    return AllureReportUploadResponse(
        run_id=test_run.id,
        message="Report processed successfully",
        tests_processed=stats['total'],
        tests_failed=stats['failed'],
        tests_passed=stats['passed']
    )


# ==================== Test Results Query ====================

@app.get("/runs/{run_id}/results", response_model=List[TestResultResponse])
async def get_run_results(
    run_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all test results for a run"""
    
    result = await db.execute(
        select(TestResult).filter(TestResult.run_id == run_id)
    )
    results = result.scalars().all()
    
    return results


@app.get("/tests/{history_id}/history", response_model=List[TestResultResponse])
async def get_test_history(
    history_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get historical results for a specific test"""
    
    result = await db.execute(
        select(TestResult)
        .filter(TestResult.history_id == history_id)
        .order_by(TestResult.created_at.desc())
        .limit(limit)
    )
    results = result.scalars().all()
    
    return results


# ==================== Folder Import ====================

@app.post("/import/folder")
async def import_from_folder(
    date_folder: Optional[str] = None,
    project_name: Optional[str] = None,
    suite_name: Optional[str] = None,
    environment: Optional[str] = "default",
    db: AsyncSession = Depends(get_db)
):
    """
    Import Allure reports from folder structure
    Scans ALLURE_REPORTS_PATH for date-based folders and imports reports
    """
    reports_path = Path(settings.ALLURE_REPORTS_PATH)
    
    if not reports_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reports folder not found: {reports_path}"
        )
    
    imported_runs = []
    errors = []
    
    # If date_folder is specified, only process that folder
    if date_folder:
        folders_to_process = [reports_path / date_folder]
    else:
        # Process all date folders
        folders_to_process = [d for d in reports_path.iterdir() if d.is_dir()]
    
    for folder in folders_to_process:
        if not folder.exists():
            errors.append(f"Folder not found: {folder}")
            continue
        
        # Extract date from folder name (e.g., "10-11-2025")
        folder_date = folder.name
        
        # Parse date folder name to get actual date
        try:
            # Try to parse date from folder name (DD-MM-YYYY format)
            date_parts = folder_date.split('-')
            if len(date_parts) == 3:
                day, month, year = date_parts
                folder_datetime = datetime(int(year), int(month), int(day))
            else:
                folder_datetime = datetime.fromtimestamp(folder.stat().st_mtime)
        except Exception as e:
            logger.warning(f"Could not parse date from folder {folder_date}: {e}")
            folder_datetime = datetime.fromtimestamp(folder.stat().st_mtime)
        
        # Determine project and suite names
        if not project_name:
            # Try to extract from labels in first result file
            project_name = "Default Project"
        
        if not suite_name:
            suite_name = folder_date
        
        # Get or create project
        project_result = await db.execute(
            select(Project).filter(Project.name == project_name)
        )
        project = project_result.scalar_one_or_none()
        
        if not project:
            project = Project(
                name=project_name,
                description=f"Auto-imported from {folder_date}",
                meta_data={"imported_from": str(folder)}
            )
            db.add(project)
            await db.flush()
            logger.info(f"Created project: {project_name}")
        
        # Get or create test suite
        suite_result = await db.execute(
            select(TestSuite)
            .filter(TestSuite.project_id == project.id)
            .filter(TestSuite.name == suite_name)
        )
        suite = suite_result.scalar_one_or_none()
        
        if not suite:
            suite = TestSuite(
                project_id=project.id,
                name=suite_name,
                description=f"Test suite for {folder_date}"
            )
            db.add(suite)
            await db.flush()
            logger.info(f"Created suite: {suite_name}")
        
        # Parse all result files in folder
        try:
            test_results = parser.parse_results_directory(str(folder))
            
            if not test_results:
                logger.warning(f"No test results found in {folder}")
                continue
            
            # Aggregate statistics
            stats = aggregator.aggregate_reports(test_results)
            
            # Create test run
            run_id = generate_uuid()
            test_run = TestRun(
                suite_id=suite.id,
                run_id=run_id,
                status=TestStatus.PASSED if stats['failed'] == 0 else TestStatus.FAILED,
                started_at=folder_datetime,
                finished_at=folder_datetime,
                duration_ms=stats['total_duration_ms'],
                environment=environment,
                build_number=folder_date,
                branch="main",
                meta_data={
                    "stats": stats,
                    "folder": str(folder),
                    "date_folder": folder_date
                }
            )
            
            db.add(test_run)
            await db.flush()
            
            # Store individual test results
            for test_result_data in test_results:
                error_info = parser.extract_error_info(test_result_data.get("statusDetails", {}))
                
                test_result = TestResult(
                    run_id=test_run.id,
                    test_name=test_result_data["name"],
                    full_name=test_result_data["fullName"],
                    status=test_result_data["status"],
                    duration_ms=test_result_data["time"]["duration"],
                    error_message=error_info["message"],
                    error_trace=error_info["trace"],
                    description=test_result_data.get("description", ""),
                    labels=test_result_data.get("labels", {}),
                    parameters=test_result_data.get("parameters", {}),
                    attachments=test_result_data.get("attachments", []),
                    history_id=test_result_data["historyId"]
                )
                
                db.add(test_result)
            
            await db.commit()
            
            imported_runs.append({
                "run_id": str(test_run.id),
                "folder": folder_date,
                "tests_processed": stats['total'],
                "tests_passed": stats['passed'],
                "tests_failed": stats['failed'],
                "project": project_name,
                "suite": suite_name
            })
            
            logger.info(f"Imported {len(test_results)} test results from {folder_date}")
            
        except Exception as e:
            error_msg = f"Error importing from {folder_date}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            await db.rollback()
            continue
    
    return {
        "message": f"Import completed. Processed {len(imported_runs)} folders.",
        "imported_runs": imported_runs,
        "errors": errors,
        "total_runs": len(imported_runs)
    }


@app.get("/import/folders")
async def list_available_folders():
    """List all available date folders in ALLURE_REPORTS_PATH"""
    reports_path = Path(settings.ALLURE_REPORTS_PATH)
    
    if not reports_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reports folder not found: {reports_path}"
        )
    
    folders = []
    for folder in reports_path.iterdir():
        if folder.is_dir():
            # Count result files
            result_files = list(folder.glob("*-result.json"))
            folders.append({
                "name": folder.name,
                "path": str(folder),
                "result_count": len(result_files),
                "last_modified": datetime.fromtimestamp(folder.stat().st_mtime).isoformat()
            })
    
    return {
        "reports_path": str(reports_path),
        "folders": sorted(folders, key=lambda x: x["name"], reverse=True)
    }


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "report-aggregator"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

