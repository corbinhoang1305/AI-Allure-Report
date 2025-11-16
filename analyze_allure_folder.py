#!/usr/bin/env python3
"""
Analyze Allure Reports Folder to Find Passed/Flaky/Failed Test Cases
Based on retry logic
"""

import json
import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

def analyze_allure_folder(folder_path: str):
    """
    Analyze Allure results folder and categorize tests
    
    Logic:
    - Passed: Test ran ONCE and passed
    - Flaky: Test failed first, then passed on retry
    - Failed: Test failed first, and still failed on retry (OR failed once without retry)
    """
    
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ Folder không tồn tại: {folder_path}")
        return
    
    print("=" * 80)
    print(f"📁 Analyzing Folder: {folder_path}")
    print("=" * 80)
    print()
    
    # Find all result JSON files
    result_files = list(folder.glob("*-result.json"))
    print(f"📄 Tìm thấy {len(result_files)} result files")
    print()
    
    # Group by history_id (or testCaseId or fullName)
    test_cases = defaultdict(list)
    
    for file_path in result_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Get unique identifier for test case
            history_id = data.get('historyId', '')
            test_case_id = data.get('testCaseId', '')
            full_name = data.get('fullName', '')
            test_name = data.get('name', 'Unknown')
            
            # Use historyId as primary key
            test_key = history_id or test_case_id or full_name
            
            if not test_key:
                print(f"⚠️  Skipping {file_path.name} - no identifier")
                continue
            
            # Get status and timing
            status = data.get('status', 'unknown')
            start = data.get('start', 0)
            stop = data.get('stop', 0)
            
            test_cases[test_key].append({
                'file': file_path.name,
                'name': test_name,
                'status': status,
                'start': start,
                'stop': stop,
                'duration': (stop - start) / 1000 if stop > start else 0
            })
        except Exception as e:
            print(f"⚠️  Error reading {file_path.name}: {e}")
    
    print(f"✅ Nhận diện được {len(test_cases)} unique test cases")
    print()
    
    # Categorize test cases
    passed_tests = []
    flaky_tests = []
    failed_tests = []
    
    for test_key, results in test_cases.items():
        # Sort by start time (chronological order)
        results.sort(key=lambda x: x['start'])
        
        num_runs = len(results)
        statuses = [r['status'] for r in results]
        first_status = results[0]['status']
        final_status = results[-1]['status']
        
        test_info = {
            'key': test_key[:50] + '...' if len(test_key) > 50 else test_key,
            'name': results[0]['name'],
            'num_runs': num_runs,
            'statuses': statuses,
            'results': results
        }
        
        # Logic verified:
        # - Passed: Test ran ONCE and passed
        # - Flaky: Test FAILED first, then PASSED on retry
        # - Failed: Test failed (with or without retry)
        
        if num_runs == 1:
            # Single run - no retry
            if first_status == 'passed':
                # Passed: ran once and passed
                passed_tests.append(test_info)
            else:
                # Failed: ran once and failed (no retry attempted)
                failed_tests.append(test_info)
        else:
            # Multiple runs - has retry
            if first_status in ['failed', 'broken']:
                # First run failed
                if final_status == 'passed':
                    # Flaky: failed first, then passed on retry
                    flaky_tests.append(test_info)
                else:
                    # Failed: failed first, and still failed after retry
                    failed_tests.append(test_info)
            elif first_status == 'passed':
                # First run passed but has multiple runs
                # Treat as Passed (stable - just duplicate data)
                # Note: This differs from backend which treats it as Flaky
                # because duplicate data shouldn't count as instability
                passed_tests.append(test_info)
    
    # Print summary
    print("=" * 80)
    print("📊 KẾT QUẢ PHÂN TÍCH")
    print("=" * 80)
    print()
    print(f"✅ PASSED: {len(passed_tests)} tests (chạy 1 lần và passed)")
    print(f"🟠 FLAKY:  {len(flaky_tests)} tests (có retry)")
    print(f"❌ FAILED: {len(failed_tests)} tests (failed)")
    print()
    print(f"📊 Total test cases: {len(test_cases)}")
    print(f"📄 Total result files: {len(result_files)}")
    print()
    
    # Show details
    if flaky_tests:
        print("=" * 80)
        print("🟠 FLAKY TESTS (Chi tiết)")
        print("=" * 80)
        for i, test in enumerate(flaky_tests, 1):
            print(f"\n{i}. {test['name']}")
            print(f"   Runs: {test['num_runs']}")
            print(f"   Statuses: {' → '.join(test['statuses'])}")
            for j, result in enumerate(test['results'], 1):
                status_icon = '✅' if result['status'] == 'passed' else '❌'
                print(f"      Run {j}: {status_icon} {result['status'].upper():8} ({result['duration']:.2f}s)")
    
    if failed_tests:
        print()
        print("=" * 80)
        print("❌ FAILED TESTS (Chi tiết)")
        print("=" * 80)
        for i, test in enumerate(failed_tests, 1):
            print(f"\n{i}. {test['name']}")
            print(f"   Runs: {test['num_runs']}")
            print(f"   Statuses: {' → '.join(test['statuses'])}")
            if test['num_runs'] > 1:
                for j, result in enumerate(test['results'], 1):
                    print(f"      Run {j}: ❌ {result['status'].upper():8} ({result['duration']:.2f}s)")
    
    # Export to CSV
    csv_filename = f"analyzed_results_{Path(folder_path).name}.csv"
    with open(csv_filename, 'w', encoding='utf-8') as f:
        f.write("Category,Test Name,Runs,Statuses\n")
        
        for test in passed_tests:
            f.write(f"Passed,\"{test['name']}\",{test['num_runs']},\"{' → '.join(test['statuses'])}\"\n")
        
        for test in flaky_tests:
            f.write(f"Flaky,\"{test['name']}\",{test['num_runs']},\"{' → '.join(test['statuses'])}\"\n")
        
        for test in failed_tests:
            f.write(f"Failed,\"{test['name']}\",{test['num_runs']},\"{' → '.join(test['statuses'])}\"\n")
    
    print()
    print("=" * 80)
    print(f"💾 Đã export ra file: {csv_filename}")
    print("=" * 80)
    print()
    
    # Verification
    print("=" * 80)
    print("✅ VERIFICATION")
    print("=" * 80)
    print(f"Expected: 66 passed, 4 flaky, 1 failed")
    print(f"Actual:   {len(passed_tests)} passed, {len(flaky_tests)} flaky, {len(failed_tests)} failed")
    print()
    
    if len(passed_tests) == 66 and len(flaky_tests) == 4 and len(failed_tests) == 1:
        print("✅ MATCH! Kết quả đúng với expected!")
    else:
        print("⚠️  Kết quả khác với expected!")
        diff_passed = len(passed_tests) - 66
        diff_flaky = len(flaky_tests) - 4
        diff_failed = len(failed_tests) - 1
        if diff_passed != 0:
            print(f"   Passed: {diff_passed:+d}")
        if diff_flaky != 0:
            print(f"   Flaky: {diff_flaky:+d}")
        if diff_failed != 0:
            print(f"   Failed: {diff_failed:+d}")
    print()
    
    return {
        'passed': len(passed_tests),
        'flaky': len(flaky_tests),
        'failed': len(failed_tests),
        'total': len(test_cases),
        'passed_tests': passed_tests,
        'flaky_tests': flaky_tests,
        'failed_tests': failed_tests
    }


def main():
    folder_path = r"D:\allure-reports\14-11-2025"
    
    print()
    print("🔍 ALLURE FOLDER ANALYZER")
    print("Logic:")
    print("  - Passed: Test chạy 1 lần và passed")
    print("  - Flaky:  Test failed lần đầu, passed lần retry")
    print("  - Failed: Test failed (dù có retry hay không)")
    print()
    
    results = analyze_allure_folder(folder_path)
    
    return results


if __name__ == "__main__":
    main()

