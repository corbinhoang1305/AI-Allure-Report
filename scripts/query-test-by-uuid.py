"""
Script to query database for test details by UUID
and then search for corresponding result.json file
"""
import sys
import json
from pathlib import Path
from uuid import UUID
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.shared.database import get_db_context
from backend.shared.models import TestResult, TestRun, TestSuite


async def find_test_by_uuid(test_uuid: str):
    """Find test by database UUID and search for corresponding result.json"""
    
    try:
        uuid_obj = UUID(test_uuid)
    except ValueError:
        print(f"❌ Invalid UUID format: {test_uuid}")
        return
    
    print(f"🔍 Searching for test with database UUID: {test_uuid}")
    print("")
    
    async with get_db_context() as db:
        # Query test result
        query = select(TestResult).filter(TestResult.id == uuid_obj)
        result = await db.execute(query)
        test_result = result.scalar_one_or_none()
        
        if not test_result:
            print(f"❌ Test not found in database with UUID: {test_uuid}")
            return
        
        print("✅ Found test in database:")
        print(f"   Test Name: {test_result.test_name}")
        print(f"   Full Name: {test_result.full_name}")
        print(f"   Status: {test_result.status.value}")
        print(f"   History ID: {test_result.history_id}")
        print(f"   Created At: {test_result.created_at}")
        print("")
        
        # Get run details
        run_query = select(TestRun).filter(TestRun.id == test_result.run_id)
        run_result = await db.execute(run_query)
        test_run = run_result.scalar_one_or_none()
        
        if test_run:
            print("📊 Test Run Details:")
            print(f"   Run ID: {test_run.run_id}")
            print(f"   Started At: {test_run.started_at}")
            print(f"   Build Number: {test_run.build_number}")
            print(f"   Branch: {test_run.branch}")
            if test_run.meta_data:
                folder_info = test_run.meta_data.get("folder") or test_run.meta_data.get("date_folder")
                if folder_info:
                    print(f"   Source Folder: {folder_info}")
            print("")
        
        # Now search for result.json files
        print("🔍 Searching for corresponding result.json files...")
        print("")
        
        search_paths = [
            Path("D:/allure-reports"),
            Path(__file__).parent.parent / "frontend" / "public" / "real-data"
        ]
        
        found_files = []
        
        for search_path in search_paths:
            if not search_path.exists():
                continue
            
            print(f"   Searching in: {search_path}")
            
            # Search for result.json files
            result_files = list(search_path.rglob("*-result.json"))
            
            for result_file in result_files:
                try:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                    
                    # Match by test name
                    if (content.get("name") == test_result.test_name or 
                        content.get("fullName") == test_result.full_name):
                        found_files.append({
                            "file": result_file,
                            "content": content
                        })
                        print(f"   ✓ Found match: {result_file}")
                        print(f"     Allure UUID: {content.get('uuid', 'N/A')}")
                        print(f"     Status: {content.get('status', 'N/A')}")
                        print(f"     Date folder: {result_file.parent.name}")
                        print("")
                except Exception as e:
                    print(f"   ✗ Error reading {result_file.name}: {e}")
        
        if not found_files:
            print("❌ No matching result.json files found")
            print("")
            print("Possible reasons:")
            print("1. The result.json file was deleted or moved")
            print("2. The test was imported from a different location")
            print("3. The test name doesn't match exactly")
        else:
            print(f"✅ Found {len(found_files)} matching result.json file(s)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/query-test-by-uuid.py <database-uuid>")
        print("Example: python scripts/query-test-by-uuid.py 966f8822-2852-4139-80cd-2d631366abcb")
        sys.exit(1)
    
    test_uuid = sys.argv[1]
    asyncio.run(find_test_by_uuid(test_uuid))



