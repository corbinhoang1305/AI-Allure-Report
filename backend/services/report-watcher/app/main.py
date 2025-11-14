"""
Report Watcher Service
Automatically scans Allure report folders and imports data
"""
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import asyncio
import os
import json
from pathlib import Path
from typing import List, Dict, Any
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from shared.config import settings
from shared.database import get_db_context
from shared.models import Project, TestSuite, TestRun, TestResult, TestStatus
from shared.utils import logger, generate_uuid, generate_history_id

app = FastAPI(
    title="Report Watcher Service",
    description="Automatically scan and import Allure reports",
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

# Global configuration
WATCH_FOLDER = os.getenv("ALLURE_REPORTS_PATH", "D:/allure-reports")
SCAN_INTERVAL_MINUTES = int(os.getenv("SCAN_INTERVAL_MINUTES", "5"))
scheduler = AsyncIOScheduler()

# Track processed files to avoid duplicates
processed_files = set()


class AllureReportScanner:
    """Scanner for Allure report folders"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        
    async def scan_reports(self) -> List[Dict[str, Any]]:
        """
        Scan folder structure: base_path/dd-mm-yyyy/*.json
        Returns list of report batches with metadata
        """
        reports = []
        
        if not self.base_path.exists():
            logger.warning(f"Watch folder does not exist: {self.base_path}")
            return reports
        
        # Scan each date folder
        for date_folder in self.base_path.iterdir():
            if not date_folder.is_dir():
                continue
                
            # Validate date format: dd-mm-yyyy
            folder_name = date_folder.name
            if not self._is_valid_date_folder(folder_name):
                continue
            
            # Parse date
            try:
                test_date = datetime.strptime(folder_name, "%d-%m-%Y")
            except ValueError:
                logger.warning(f"Invalid date folder format: {folder_name}")
                continue
            
            # Scan JSON files in this date folder
            json_files = list(date_folder.glob("*.json"))
            
            if json_files:
                reports.append({
                    "date": test_date,
                    "folder": str(date_folder),
                    "files": [str(f) for f in json_files],
                    "count": len(json_files)
                })
                
                logger.info(f"Found {len(json_files)} reports in {folder_name}")
        
        return reports
    
    def _is_valid_date_folder(self, folder_name: str) -> bool:
        """Check if folder name matches dd-mm-yyyy format"""
        parts = folder_name.split('-')
        if len(parts) != 3:
            return False
        
        try:
            day, month, year = parts
            return (len(day) == 2 and len(month) == 2 and len(year) == 4 and
                    day.isdigit() and month.isdigit() and year.isdigit())
        except:
            return False
    
    async def load_json_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Load and parse JSON files"""
        results = []
        
        for file_path in file_paths:
            # Skip if already processed
            if file_path in processed_files:
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    results.append(data)
                    processed_files.add(file_path)
                    
            except Exception as e:
                logger.error(f"Error loading {file_path}: {str(e)}")
                continue
        
        return results


class AllureDataProcessor:
    """Process and store Allure data to database"""
    
    async def process_reports(self, reports: List[Dict[str, Any]]):
        """Process scanned reports and save to database"""
        
        for report_batch in reports:
            date = report_batch["date"]
            files = report_batch["files"]
            
            logger.info(f"Processing {len(files)} files from {date.strftime('%d-%m-%Y')}")
            
            # Load JSON data
            scanner = AllureReportScanner(WATCH_FOLDER)
            test_results = await scanner.load_json_files(files)
            
            if not test_results:
                continue
            
            # Save to database
            await self._save_to_database(test_results, date)
    
    async def _save_to_database(self, test_results: List[Dict[str, Any]], test_date: datetime):
        """Save test results to database"""
        
        async with get_db_context() as db:
            try:
                # Get or create project (using default project for now)
                project = await self._get_or_create_project(db, "Auto-Imported Project")
                
                # Get or create test suite
                suite = await self._get_or_create_suite(db, project.id, f"Suite-{test_date.strftime('%Y-%m-%d')}")
                
                # Create test run
                run_id = generate_uuid()
                
                # Calculate run statistics
                total = len(test_results)
                passed = sum(1 for r in test_results if r.get("status") == "passed")
                failed = sum(1 for r in test_results if r.get("status") in ["failed", "broken"])
                
                # Determine overall status
                run_status = TestStatus.PASSED if failed == 0 else TestStatus.FAILED
                
                # Get time range
                start_times = [r.get("start", 0) for r in test_results if r.get("start")]
                stop_times = [r.get("stop", 0) for r in test_results if r.get("stop")]
                
                start_time = datetime.fromtimestamp(min(start_times) / 1000) if start_times else test_date
                end_time = datetime.fromtimestamp(max(stop_times) / 1000) if stop_times else test_date
                total_duration = sum([(r.get("stop", 0) - r.get("start", 0)) for r in test_results])
                
                # Create test run
                from sqlalchemy import select
                from shared.models import TestRun
                
                test_run = TestRun(
                    suite_id=suite.id,
                    run_id=run_id,
                    status=run_status,
                    started_at=start_time,
                    finished_at=end_time,
                    duration_ms=total_duration,
                    environment="production",
                    branch="main",
                    metadata={
                        "stats": {
                            "total": total,
                            "passed": passed,
                            "failed": failed,
                            "pass_rate": (passed / total * 100) if total > 0 else 0
                        },
                        "auto_imported": True,
                        "import_date": datetime.utcnow().isoformat()
                    }
                )
                
                db.add(test_run)
                await db.flush()
                
                # Save individual test results
                for result_data in test_results:
                    await self._save_test_result(db, test_run.id, result_data)
                
                await db.commit()
                
                logger.info(f"✅ Saved run {run_id}: {passed}/{total} passed")
                
            except Exception as e:
                logger.error(f"Error saving to database: {str(e)}")
                await db.rollback()
    
    async def _get_or_create_project(self, db, name: str):
        """Get or create project"""
        from sqlalchemy import select
        from shared.models import Project
        
        result = await db.execute(select(Project).filter(Project.name == name))
        project = result.scalar_one_or_none()
        
        if not project:
            project = Project(
                name=name,
                description="Auto-imported from Allure reports"
            )
            db.add(project)
            await db.flush()
        
        return project
    
    async def _get_or_create_suite(self, db, project_id, name: str):
        """Get or create test suite"""
        from sqlalchemy import select
        from shared.models import TestSuite
        
        result = await db.execute(
            select(TestSuite).filter(
                TestSuite.project_id == project_id,
                TestSuite.name == name
            )
        )
        suite = result.scalar_one_or_none()
        
        if not suite:
            suite = TestSuite(
                project_id=project_id,
                name=name,
                path=f"/auto-import/{name}"
            )
            db.add(suite)
            await db.flush()
        
        return suite
    
    async def _save_test_result(self, db, run_id, result_data: Dict[str, Any]):
        """Save individual test result"""
        from shared.models import TestResult
        
        # Parse status
        status_map = {
            "passed": TestStatus.PASSED,
            "failed": TestStatus.FAILED,
            "broken": TestStatus.BROKEN,
            "skipped": TestStatus.SKIPPED
        }
        status = status_map.get(result_data.get("status", "unknown"), TestStatus.UNKNOWN)
        
        # Extract error info
        status_details = result_data.get("statusDetails", {})
        error_message = status_details.get("message", "")
        error_trace = status_details.get("trace", "")
        
        # Parse labels
        labels = {}
        for label in result_data.get("labels", []):
            name = label.get("name")
            value = label.get("value")
            if name:
                if name not in labels:
                    labels[name] = []
                labels[name].append(value)
        
        # Calculate duration
        start = result_data.get("start", 0)
        stop = result_data.get("stop", 0)
        duration_ms = stop - start
        
        # Generate history ID
        test_name = result_data.get("name", "unknown")
        parameters = {p.get("name"): p.get("value") for p in result_data.get("parameters", [])}
        history_id = result_data.get("historyId") or generate_history_id(test_name, parameters)
        
        # Create test result
        test_result = TestResult(
            run_id=run_id,
            test_name=test_name,
            full_name=result_data.get("fullName", test_name),
            status=status,
            duration_ms=duration_ms,
            error_message=error_message,
            error_trace=error_trace,
            description=result_data.get("description", ""),
            labels=labels,
            parameters=parameters,
            attachments=result_data.get("attachments", []),
            history_id=history_id,
            allure_uuid=result_data.get("uuid")  # Store original Allure UUID
        )
        
        db.add(test_result)


# Background task
async def scan_and_process():
    """Scheduled task to scan and process reports"""
    logger.info(f"🔍 Starting scheduled scan of {WATCH_FOLDER}")
    
    try:
        # Scan for new reports
        scanner = AllureReportScanner(WATCH_FOLDER)
        reports = await scanner.scan_reports()
        
        if not reports:
            logger.info("No new reports found")
            return
        
        # Process reports
        processor = AllureDataProcessor()
        await processor.process_reports(reports)
        
        logger.info(f"✅ Scan completed. Processed {len(reports)} report batches")
        
    except Exception as e:
        logger.error(f"Error in scan_and_process: {str(e)}")


# Startup
@app.on_event("startup")
async def startup_event():
    """Initialize scheduler on startup"""
    from shared.database import init_db
    await init_db()
    
    logger.info(f"📂 Watching folder: {WATCH_FOLDER}")
    logger.info(f"⏰ Scan interval: {SCAN_INTERVAL_MINUTES} minutes")
    
    # Schedule the scan job
    scheduler.add_job(
        scan_and_process,
        'interval',
        minutes=SCAN_INTERVAL_MINUTES,
        id='scan_allure_reports',
        replace_existing=True
    )
    
    # Run initial scan
    asyncio.create_task(scan_and_process())
    
    # Start scheduler
    scheduler.start()
    
    logger.info("✅ Report Watcher Service started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    scheduler.shutdown()
    logger.info("Report Watcher Service stopped")


# Manual trigger endpoint
@app.post("/scan/trigger")
async def trigger_scan(background_tasks: BackgroundTasks):
    """Manually trigger a scan"""
    background_tasks.add_task(scan_and_process)
    return {"message": "Scan triggered", "folder": WATCH_FOLDER}


@app.get("/scan/status")
async def get_status():
    """Get scanner status"""
    return {
        "status": "running",
        "watch_folder": WATCH_FOLDER,
        "scan_interval_minutes": SCAN_INTERVAL_MINUTES,
        "processed_files_count": len(processed_files),
        "next_scan": scheduler.get_job('scan_allure_reports').next_run_time.isoformat() if scheduler.get_job('scan_allure_reports') else None
    }


@app.get("/scan/processed")
async def get_processed_files():
    """Get list of processed files"""
    return {
        "count": len(processed_files),
        "files": list(processed_files)[-50:]  # Last 50 files
    }


@app.delete("/scan/reset")
async def reset_processed_files():
    """Reset processed files tracking"""
    global processed_files
    count = len(processed_files)
    processed_files.clear()
    return {"message": f"Reset {count} processed files"}


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "report-watcher",
        "watching": WATCH_FOLDER
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)

