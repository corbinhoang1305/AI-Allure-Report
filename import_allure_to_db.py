#!/usr/bin/env python3
"""
Import Allure JSON results to database with complete retry information
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
import uuid

# Database configuration
DB_CONFIG = {
    'host': 'qualify-postgres',  # Docker service name
    'port': 5432,
    'database': 'qualify_db',
    'user': 'qualify',
    'password': 'qualify_password'
}

def parse_allure_results(folder_path):
    """Parse all Allure result files and group by history_id"""
    print(f"\n📂 Parsing Allure results from: {folder_path}")
    
    folder = Path(folder_path)
    if not folder.exists():
        print(f"❌ Folder not found: {folder_path}")
        sys.exit(1)
    
    test_cases = defaultdict(list)
    result_files = list(folder.glob("*-result.json"))
    
    print(f"📄 Found {len(result_files)} result files")
    
    for json_file in result_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            history_id = data.get('historyId')
            test_case_id = data.get('testCaseId')
            full_name = data.get('fullName', '')
            test_name = data.get('name', 'Unknown')
            
            # Use historyId as primary key
            test_key = history_id or test_case_id or full_name
            
            if not test_key:
                print(f"⚠️  Skipping {json_file.name} - no identifier")
                continue
            
            # Get status and timing
            status = data.get('status', 'unknown').upper()
            start = data.get('start', 0)
            stop = data.get('stop', 0)
            duration_ms = int((stop - start)) if stop > start else 0
            
            test_cases[test_key].append({
                'file': json_file.name,
                'history_id': history_id,
                'test_case_id': test_case_id,
                'full_name': full_name,
                'test_name': test_name,
                'status': status,
                'start': start,
                'stop': stop,
                'duration_ms': duration_ms,
                'created_at': datetime.fromtimestamp(start / 1000) if start else datetime.now()
            })
        except Exception as e:
            print(f"⚠️  Error reading {json_file.name}: {e}")
    
    print(f"✅ Identified {len(test_cases)} unique test cases")
    
    # Sort results by start time for each test
    for test_key in test_cases:
        test_cases[test_key].sort(key=lambda x: x['start'])
    
    return test_cases

def delete_existing_data(conn, date_str):
    """Delete existing test data for the specified date"""
    print(f"\n🗑️  Deleting existing data for {date_str}...")
    
    with conn.cursor() as cur:
        # Delete test results first (foreign key constraint)
        cur.execute("""
            DELETE FROM test_results 
            WHERE run_id IN (
                SELECT id FROM test_runs 
                WHERE started_at::date = %s
            )
        """, (date_str,))
        deleted_results = cur.rowcount
        
        # Delete test runs
        cur.execute("""
            DELETE FROM test_runs 
            WHERE started_at::date = %s
        """, (date_str,))
        deleted_runs = cur.rowcount
        
        conn.commit()
        print(f"✅ Deleted {deleted_results} test results and {deleted_runs} test runs")

def import_to_database(test_cases, run_date):
    """Import test cases with retry information to database"""
    print(f"\n📥 Connecting to database...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Connected to database")
        
        # Delete existing data
        delete_existing_data(conn, run_date)
        
        # Get or create test suite
        with conn.cursor() as cur:
            # Get default project
            cur.execute("SELECT id FROM projects LIMIT 1")
            project_result = cur.fetchone()
            if not project_result:
                print("❌ No project found in database!")
                return False
            project_id = project_result[0]
            
            # Check if suite exists for this project
            suite_name = f"Allure Import - {run_date}"
            cur.execute("""
                SELECT id FROM test_suites 
                WHERE project_id = %s 
                ORDER BY created_at DESC LIMIT 1
            """, (project_id,))
            suite_result = cur.fetchone()
            
            if suite_result:
                suite_id = suite_result[0]
            else:
                # Create a new suite
                suite_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO test_suites (id, project_id, name, created_at)
                    VALUES (%s, %s, %s, NOW())
                """, (suite_id, project_id, suite_name))
                conn.commit()
            
            print(f"✅ Using suite: {suite_id}")
        
        # Create a single test run
        run_id = str(uuid.uuid4())
        run_id_str = f"allure-import-{run_date}"
        started_at = datetime.strptime(run_date, '%Y-%m-%d')
        
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO test_runs (id, suite_id, run_id, started_at, status, created_at)
                VALUES (%s, %s, %s, %s, 'PASSED', NOW())
            """, (run_id, suite_id, run_id_str, started_at))
            conn.commit()
            print(f"✅ Created test run: {run_id_str}")
        
        # Prepare test results
        print(f"\n📊 Preparing test results...")
        results_to_insert = []
        
        for test_key, results in test_cases.items():
            for result in results:
                results_to_insert.append((
                    str(uuid.uuid4()),  # id
                    run_id,  # run_id
                    result['test_name'],  # test_name
                    result['full_name'],  # full_name
                    result['status'],  # status
                    result['duration_ms'],  # duration_ms
                    result['history_id'],  # history_id
                    result['created_at'],  # created_at
                ))
        
        print(f"📝 Inserting {len(results_to_insert)} test results...")
        
        with conn.cursor() as cur:
            execute_values(cur, """
                INSERT INTO test_results 
                (id, run_id, test_name, full_name, status, duration_ms, history_id, created_at)
                VALUES %s
            """, results_to_insert)
            
            conn.commit()
        
        print(f"✅ Successfully imported {len(results_to_insert)} test results!")
        
        # Analyze results
        print(f"\n📊 Analyzing imported data...")
        analyze_results(test_cases)
        
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def analyze_results(test_cases):
    """Analyze and categorize test results"""
    passed = 0
    flaky = 0
    failed = 0
    
    print("\n" + "="*80)
    print("📊 ANALYSIS SUMMARY")
    print("="*80)
    
    for test_key, results in test_cases.items():
        num_runs = len(results)
        first_status = results[0]['status']
        final_status = results[-1]['status']
        
        if num_runs == 1:
            if first_status == 'PASSED':
                passed += 1
            else:
                failed += 1
        else:
            if first_status in ['FAILED', 'BROKEN']:
                if final_status == 'PASSED':
                    flaky += 1
                else:
                    failed += 1
            elif first_status == 'PASSED':
                passed += 1
    
    total = passed + flaky + failed
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n✅ PASSED: {passed} tests (ran once and passed)")
    print(f"🟠 FLAKY:  {flaky} tests (failed first, passed on retry)")
    print(f"❌ FAILED: {failed} tests (failed consistently)")
    print(f"\n📊 Total: {total} test cases")
    print(f"📈 Pass Rate: {pass_rate:.2f}%")
    print("="*80)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python import_allure_to_db.py <allure_folder_path> [date YYYY-MM-DD]")
        print("Example: python import_allure_to_db.py D:\\allure-reports\\14-11-2025 2025-11-14")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    
    # Auto-detect date from folder name if not provided
    if len(sys.argv) >= 3:
        run_date = sys.argv[2]
    else:
        # Try to extract date from folder name (e.g., "14-11-2025" -> "2025-11-14")
        folder_name = Path(folder_path).name
        parts = folder_name.split('-')
        if len(parts) == 3:
            run_date = f"{parts[2]}-{parts[1]}-{parts[0]}"
        else:
            run_date = datetime.now().strftime('%Y-%m-%d')
    
    print("="*80)
    print("🚀 ALLURE TO DATABASE IMPORTER")
    print("="*80)
    print(f"📂 Source: {folder_path}")
    print(f"📅 Date: {run_date}")
    print("="*80)
    
    # Parse Allure results
    test_cases = parse_allure_results(folder_path)
    
    if not test_cases:
        print("❌ No test cases found!")
        sys.exit(1)
    
    # Import to database
    success = import_to_database(test_cases, run_date)
    
    if success:
        print("\n🎉 Import completed successfully!")
        print(f"\n💡 You can now check the dashboard at: http://localhost:3000")
        print(f"   API endpoint: http://localhost:8000/api/analytics/dashboard")
    else:
        print("\n❌ Import failed!")
        sys.exit(1)

