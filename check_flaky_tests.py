#!/usr/bin/env python3
"""
Script để phát hiện Flaky Tests từ Allure Reports
Phân tích tất cả file JSON trong folder và tìm các test có kết quả không ổn định
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set
from datetime import datetime


class FlakyTestDetector:
    """Class để phát hiện flaky tests từ Allure results"""
    
    def __init__(self, folder_path: str):
        self.folder_path = Path(folder_path)
        self.test_results = []
        self.flaky_tests = []
        
    def load_json_files(self) -> int:
        """Load tất cả file JSON từ folder"""
        count = 0
        print(f"🔍 Đang quét folder: {self.folder_path}")
        print("=" * 80)
        
        if not self.folder_path.exists():
            print(f"❌ Lỗi: Folder không tồn tại: {self.folder_path}")
            return 0
            
        for json_file in self.folder_path.glob("*-result.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.test_results.append({
                        'file': json_file.name,
                        'data': data
                    })
                    count += 1
            except json.JSONDecodeError as e:
                print(f"⚠️  Không thể đọc file: {json_file.name} - {e}")
            except Exception as e:
                print(f"⚠️  Lỗi khi xử lý file: {json_file.name} - {e}")
        
        print(f"✅ Đã load {count} file JSON result\n")
        return count
    
    def analyze_test_results(self) -> Dict:
        """Phân tích kết quả tests và tìm flaky tests"""
        # Group tests theo testCaseId và historyId
        tests_by_case_id = defaultdict(list)
        tests_by_history_id = defaultdict(list)
        tests_by_full_name = defaultdict(list)
        
        for result in self.test_results:
            data = result['data']
            test_case_id = data.get('testCaseId', '')
            history_id = data.get('historyId', '')
            full_name = data.get('fullName', data.get('name', 'Unknown'))
            status = data.get('status', 'unknown')
            
            test_info = {
                'file': result['file'],
                'name': data.get('name', 'Unknown'),
                'fullName': full_name,
                'status': status,
                'testCaseId': test_case_id,
                'historyId': history_id,
                'start': data.get('start', 0),
                'stop': data.get('stop', 0),
                'labels': data.get('labels', [])
            }
            
            if test_case_id:
                tests_by_case_id[test_case_id].append(test_info)
            if history_id:
                tests_by_history_id[history_id].append(test_info)
            tests_by_full_name[full_name].append(test_info)
        
        return {
            'by_case_id': tests_by_case_id,
            'by_history_id': tests_by_history_id,
            'by_full_name': tests_by_full_name
        }
    
    def detect_flaky_tests(self, grouped_tests: Dict) -> List[Dict]:
        """Phát hiện flaky tests dựa trên status không nhất quán"""
        flaky_tests = []
        
        # Kiểm tra theo testCaseId
        for test_case_id, tests in grouped_tests['by_case_id'].items():
            if len(tests) > 1:
                statuses = set([t['status'] for t in tests])
                if len(statuses) > 1:
                    flaky_tests.append({
                        'identifier': test_case_id,
                        'identifier_type': 'testCaseId',
                        'name': tests[0]['name'],
                        'fullName': tests[0]['fullName'],
                        'statuses': statuses,
                        'occurrences': len(tests),
                        'tests': tests
                    })
        
        # Kiểm tra theo historyId
        for history_id, tests in grouped_tests['by_history_id'].items():
            if len(tests) > 1:
                statuses = set([t['status'] for t in tests])
                if len(statuses) > 1:
                    # Kiểm tra xem đã thêm chưa (tránh duplicate)
                    test_case_id = tests[0]['testCaseId']
                    if not any(f['identifier'] == test_case_id for f in flaky_tests):
                        flaky_tests.append({
                            'identifier': history_id,
                            'identifier_type': 'historyId',
                            'name': tests[0]['name'],
                            'fullName': tests[0]['fullName'],
                            'statuses': statuses,
                            'occurrences': len(tests),
                            'tests': tests
                        })
        
        # Kiểm tra theo fullName (fallback nếu không có ID)
        for full_name, tests in grouped_tests['by_full_name'].items():
            if len(tests) > 1:
                statuses = set([t['status'] for t in tests])
                if len(statuses) > 1:
                    # Kiểm tra xem đã thêm chưa
                    if not any(f['fullName'] == full_name for f in flaky_tests):
                        flaky_tests.append({
                            'identifier': full_name,
                            'identifier_type': 'fullName',
                            'name': tests[0]['name'],
                            'fullName': full_name,
                            'statuses': statuses,
                            'occurrences': len(tests),
                            'tests': tests
                        })
        
        return flaky_tests
    
    def get_statistics(self) -> Dict:
        """Tính toán thống kê tổng quan"""
        stats = {
            'total': len(self.test_results),
            'passed': 0,
            'failed': 0,
            'broken': 0,
            'skipped': 0,
            'unknown': 0,
            'flaky_count': 0
        }
        
        for result in self.test_results:
            status = result['data'].get('status', 'unknown')
            if status in stats:
                stats[status] += 1
            else:
                stats['unknown'] += 1
        
        stats['flaky_count'] = len(self.flaky_tests)
        return stats
    
    def print_report(self, flaky_tests: List[Dict], stats: Dict):
        """In báo cáo chi tiết"""
        print("\n" + "=" * 80)
        print("📊 TỔNG QUAN THỐNG KÊ")
        print("=" * 80)
        print(f"📁 Folder: {self.folder_path}")
        print(f"📄 Tổng số test results: {stats['total']}")
        print(f"✅ Passed: {stats['passed']}")
        print(f"❌ Failed: {stats['failed']}")
        print(f"💔 Broken: {stats['broken']}")
        print(f"⏭️  Skipped: {stats['skipped']}")
        print(f"❓ Unknown: {stats['unknown']}")
        print(f"\n🔄 Tổng số FLAKY TESTS phát hiện: {len(flaky_tests)}")
        
        if not flaky_tests:
            print("\n" + "=" * 80)
            print("✨ TUYỆT VỜI! Không phát hiện flaky test nào!")
            print("=" * 80)
            return
        
        print("\n" + "=" * 80)
        print("⚠️  DANH SÁCH FLAKY TESTS")
        print("=" * 80)
        
        for idx, flaky in enumerate(flaky_tests, 1):
            print(f"\n{'─' * 80}")
            print(f"🔄 Flaky Test #{idx}")
            print(f"{'─' * 80}")
            print(f"📝 Test Name: {flaky['name']}")
            print(f"📍 Full Name: {flaky['fullName']}")
            print(f"🆔 Identifier ({flaky['identifier_type']}): {flaky['identifier']}")
            print(f"📊 Số lần xuất hiện: {flaky['occurrences']}")
            print(f"⚡ Các trạng thái khác nhau: {', '.join(sorted(flaky['statuses']))}")
            
            print(f"\n   Chi tiết các lần chạy:")
            for i, test in enumerate(flaky['tests'], 1):
                status_icon = {
                    'passed': '✅',
                    'failed': '❌',
                    'broken': '💔',
                    'skipped': '⏭️'
                }.get(test['status'], '❓')
                
                duration = (test['stop'] - test['start']) / 1000 if test['stop'] > test['start'] else 0
                print(f"   Run {i}: {status_icon} {test['status'].upper():8} | "
                      f"Duration: {duration:.2f}s | File: {test['file']}")
        
        print("\n" + "=" * 80)
    
    def export_to_json(self, flaky_tests: List[Dict], output_file: str = None):
        """Export kết quả ra file JSON"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"flaky_tests_report_{timestamp}.json"
        
        report = {
            'folder': str(self.folder_path),
            'scan_time': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'flaky_tests': [
                {
                    'test_name': flaky['name'],
                    'full_name': flaky['fullName'],
                    'identifier': flaky['identifier'],
                    'identifier_type': flaky['identifier_type'],
                    'occurrences': flaky['occurrences'],
                    'statuses': list(flaky['statuses']),
                    'runs': [
                        {
                            'status': test['status'],
                            'file': test['file'],
                            'duration_ms': test['stop'] - test['start']
                        }
                        for test in flaky['tests']
                    ]
                }
                for flaky in flaky_tests
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Đã export báo cáo ra file: {output_file}")
    
    def run(self, export_json: bool = True):
        """Chạy toàn bộ quá trình phân tích"""
        print("\n" + "=" * 80)
        print("🔍 FLAKY TEST DETECTOR - Allure Reports Analyzer")
        print("=" * 80)
        
        # Load files
        count = self.load_json_files()
        if count == 0:
            print("❌ Không tìm thấy file JSON nào để phân tích!")
            return
        
        # Analyze
        print("🔬 Đang phân tích test results...")
        grouped_tests = self.analyze_test_results()
        
        # Detect flaky
        print("🔄 Đang tìm kiếm flaky tests...")
        self.flaky_tests = self.detect_flaky_tests(grouped_tests)
        
        # Get stats
        stats = self.get_statistics()
        
        # Print report
        self.print_report(self.flaky_tests, stats)
        
        # Export to JSON
        if export_json and self.flaky_tests:
            self.export_to_json(self.flaky_tests)
        
        return self.flaky_tests


def main():
    """Main function"""
    # Default folder
    default_folder = r"D:\allure-reports\14-11-2025"
    
    # Get folder from command line or use default
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        folder_path = default_folder
    
    # Check if export JSON
    export_json = True
    if len(sys.argv) > 2 and sys.argv[2].lower() == '--no-export':
        export_json = False
    
    # Run detector
    detector = FlakyTestDetector(folder_path)
    flaky_tests = detector.run(export_json=export_json)
    
    # Exit code
    if flaky_tests:
        print(f"\n⚠️  Phát hiện {len(flaky_tests)} flaky test(s)!")
        sys.exit(1)
    else:
        print("\n✅ Không có flaky test nào!")
        sys.exit(0)


if __name__ == "__main__":
    main()


