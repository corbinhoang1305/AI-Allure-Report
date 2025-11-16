#!/usr/bin/env python3
"""
Debug script to check analytics logic
"""
import asyncio
import asyncpg
from datetime import datetime, timedelta

async def main():
    # Connect to database
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='qualify',
        password='qualify_password',
        database='qualify_db'
    )
    
    try:
        print("=" * 80)
        print("DEBUG ANALYTICS LOGIC")
        print("=" * 80)
        print()
        
        # Get recent test results (last 7 days)
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        query = """
        SELECT 
            tr.id as result_id,
            tr.test_name,
            tr.history_id,
            tr.test_case_id,
            tr.full_name,
            tr.status,
            tr.created_at,
            tr.duration_ms,
            run.started_at as run_started_at,
            DATE(run.started_at) as run_date
        FROM test_results tr
        JOIN test_runs run ON tr.run_id = run.id
        WHERE tr.created_at >= $1
        ORDER BY run.started_at, tr.history_id, tr.created_at
        """
        
        results = await conn.fetch(query, cutoff_date)
        
        print(f"Total results in last 7 days: {len(results)}")
        print()
        
        # Group by date and history_id
        from collections import defaultdict
        by_date_and_test = defaultdict(lambda: defaultdict(list))
        
        for row in results:
            date_key = row['run_date'].isoformat()
            test_key = row['history_id'] or row['full_name'] or row['test_name']
            by_date_and_test[date_key][test_key].append(row)
        
        print(f"Dates with data: {list(by_date_and_test.keys())}")
        print()
        
        # Analyze each date
        for date_key in sorted(by_date_and_test.keys()):
            tests = by_date_and_test[date_key]
            print(f"Date: {date_key}")
            print(f"  Unique tests: {len(tests)}")
            
            # Categorize
            passed_count = 0
            flaky_count = 0
            failed_count = 0
            
            for test_key, test_results in tests.items():
                num_runs = len(test_results)
                statuses = [r['status'] for r in test_results]
                final_status = test_results[-1]['status']
                
                if num_runs == 1:
                    if final_status == 'passed':
                        passed_count += 1
                    elif final_status in ['failed', 'broken']:
                        failed_count += 1
                else:
                    if final_status == 'passed':
                        flaky_count += 1
                    elif final_status in ['failed', 'broken']:
                        failed_count += 1
            
            print(f"  Passed (1 run, passed): {passed_count}")
            print(f"  Flaky (>1 run, passed): {flaky_count}")
            print(f"  Failed: {failed_count}")
            print()
            
            # Show examples of multi-run tests
            multi_run = {k: v for k, v in tests.items() if len(v) > 1}
            if multi_run:
                print(f"  Multi-run tests: {len(multi_run)}")
                for i, (test_key, test_results) in enumerate(list(multi_run.items())[:3]):
                    print(f"    Example {i+1}: {test_results[0]['test_name'][:50]}")
                    print(f"      Runs: {len(test_results)}")
                    print(f"      Statuses: {[r['status'] for r in test_results]}")
                print()
    
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())

