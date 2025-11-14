"""
Script to backfill Allure UUID from JSON files into database
Usage: python scripts/backfill-allure-uuid.py [folder_path]
Example: python scripts/backfill-allure-uuid.py "D:\allure-reports\14-11-2025"
"""
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.shared.database import get_db_context
from backend.shared.models import TestResult, TestRun
from backend.shared.utils import logger


async def backfill_allure_uuid_from_folder(folder_path: str):
    """Backfill Allure UUID from JSON files in a folder"""
    
    folder = Path(folder_path)
    if not folder.exists():
        print(f"❌ Folder not found: {folder_path}")
        return
    
    print(f"🔍 Scanning folder: {folder_path}")
    print("")
    
    # Find all result.json files
    result_files = list(folder.glob("*-result.json"))
    
    if not result_files:
        print(f"❌ No *-result.json files found in {folder_path}")
        return
    
    print(f"✅ Found {len(result_files)} result files")
    print("")
    
    # Parse JSON files and create mapping: test_name + historyId -> allure_uuid
    uuid_mapping = {}
    
    for result_file in result_files:
        try:
            with open(result_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            allure_uuid = content.get('uuid', '')
            test_name = content.get('name', '')
            full_name = content.get('fullName', '')
            history_id = content.get('historyId', '')
            test_case_id = content.get('testCaseId', '')
            
            if not allure_uuid:
                continue
            
            # Create keys for matching
            # Key 1: test_name + historyId
            if test_name and history_id:
                key1 = f"{test_name}::{history_id}"
                uuid_mapping[key1] = allure_uuid
            
            # Key 2: full_name + historyId
            if full_name and history_id:
                key2 = f"{full_name}::{history_id}"
                uuid_mapping[key2] = allure_uuid
            
            # Key 3: test_name only (less reliable)
            if test_name:
                uuid_mapping[test_name] = allure_uuid
            
            print(f"  ✓ {result_file.name}: {allure_uuid[:8]}... ({test_name[:50]})")
            
        except Exception as e:
            print(f"  ✗ Error reading {result_file.name}: {e}")
            continue
    
    print("")
    print(f"📊 Created mapping for {len(uuid_mapping)} test identifiers")
    print("")
    
    # Update database
    async with get_db_context() as db:
        try:
            # Get all test results that don't have allure_uuid
            query = select(TestResult).filter(
                (TestResult.allure_uuid == None) | (TestResult.allure_uuid == '')
            )
            result = await db.execute(query)
            test_results = result.scalars().all()
            
            print(f"🔍 Found {len(test_results)} test results without Allure UUID")
            print("")
            
            updated_count = 0
            not_found_count = 0
            
            for test_result in test_results:
                # Try to find matching UUID
                allure_uuid = None
                
                # Try key 1: test_name + history_id
                if test_result.test_name and test_result.history_id:
                    key1 = f"{test_result.test_name}::{test_result.history_id}"
                    allure_uuid = uuid_mapping.get(key1)
                
                # Try key 2: full_name + history_id
                if not allure_uuid and test_result.full_name and test_result.history_id:
                    key2 = f"{test_result.full_name}::{test_result.history_id}"
                    allure_uuid = uuid_mapping.get(key2)
                
                # Try key 3: test_name only
                if not allure_uuid and test_result.test_name:
                    allure_uuid = uuid_mapping.get(test_result.test_name)
                
                if allure_uuid:
                    # Update test result
                    test_result.allure_uuid = allure_uuid
                    updated_count += 1
                    if updated_count % 10 == 0:
                        print(f"  Updated {updated_count} test results...")
                else:
                    not_found_count += 1
            
            # Commit changes
            await db.commit()
            
            print("")
            print("========================================")
            print(f"✅ Successfully updated {updated_count} test results")
            if not_found_count > 0:
                print(f"⚠️  {not_found_count} test results could not be matched")
            print("========================================")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error updating database: {e}")
            raise


async def backfill_from_date_folder(date_folder: str):
    """Backfill from a date folder like '14-11-2025'"""
    base_path = Path("D:/allure-reports")
    folder_path = base_path / date_folder
    
    if not folder_path.exists():
        print(f"❌ Folder not found: {folder_path}")
        return
    
    await backfill_allure_uuid_from_folder(str(folder_path))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        asyncio.run(backfill_allure_uuid_from_folder(folder_path))
    else:
        # Default: backfill from 14-11-2025
        print("No folder specified, using default: D:\\allure-reports\\14-11-2025")
        print("")
        asyncio.run(backfill_from_date_folder("14-11-2025"))

