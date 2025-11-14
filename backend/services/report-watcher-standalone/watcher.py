"""
Standalone Report Watcher
Scans Allure report folders and generates JSON for frontend
No database required - writes directly to frontend/public
"""
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import shutil

# Configuration
WATCH_FOLDER = os.getenv("ALLURE_REPORTS_PATH", "D:/allure-reports")
OUTPUT_FOLDER = os.getenv("OUTPUT_PATH", "D:/practice/AI-Allure-Report/frontend/public/real-data")
SCAN_INTERVAL_SECONDS = int(os.getenv("SCAN_INTERVAL_SECONDS", "300"))  # 5 minutes = 300 seconds

print(f"""
╔════════════════════════════════════════════╗
║   QUALIFY.AI - Report Watcher Service     ║
╚════════════════════════════════════════════╝

📂 Watching: {WATCH_FOLDER}
📤 Output: {OUTPUT_FOLDER}
⏰ Scan interval: {SCAN_INTERVAL_SECONDS} seconds ({SCAN_INTERVAL_SECONDS//60} minutes)

Starting initial scan...
""")

class AllureReportScanner:
    """Scanner for Allure report folders"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        
    def scan_folders(self) -> List[Dict[str, Any]]:
        """
        Scan for folders with format: dd-MM-yyyy
        Returns list of folders with their test files
        """
        if not self.base_path.exists():
            print(f"⚠️  Warning: Folder does not exist: {self.base_path}")
            return []
        
        folders = []
        
        for folder in self.base_path.iterdir():
            if not folder.is_dir():
                continue
            
            # Check if folder name matches dd-MM-yyyy format
            if not self._is_valid_date_folder(folder.name):
                continue
            
            # Get all result JSON files
            result_files = list(folder.glob("*-result.json"))
            
            if result_files:
                folders.append({
                    "folder_name": folder.name,
                    "path": str(folder),
                    "files": [str(f) for f in result_files],
                    "count": len(result_files)
                })
        
        return sorted(folders, key=lambda x: x["folder_name"])
    
    def _is_valid_date_folder(self, folder_name: str) -> bool:
        """Validate dd-MM-yyyy format"""
        parts = folder_name.split('-')
        if len(parts) != 3:
            return False
        
        try:
            day, month, year = parts
            return (len(day) == 2 and len(month) == 2 and len(year) == 4 and
                    day.isdigit() and month.isdigit() and year.isdigit())
        except:
            return False


class DataProcessor:
    """Process Allure data and generate output files"""
    
    def process_folders(self, folders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process all folders and generate dashboard data"""
        
        all_results = []
        trend_data = []
        
        for folder_info in folders:
            print(f"📊 Processing {folder_info['folder_name']}: {folder_info['count']} files")
            
            # Parse date from folder name (dd-MM-yyyy)
            date_parts = folder_info['folder_name'].split('-')
            display_date = f"{date_parts[0]}/{date_parts[1]}"  # dd/MM
            
            # Load and analyze files
            day_passed = 0
            day_failed = 0
            day_broken = 0
            
            for file_path in folder_info['files']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        result = json.load(f)
                        all_results.append(result)
                        
                        # Count by status
                        status = result.get('status', 'unknown')
                        if status == 'passed':
                            day_passed += 1
                        elif status == 'failed':
                            day_failed += 1
                        elif status == 'broken':
                            day_broken += 1
                            
                except Exception as e:
                    print(f"  ⚠️  Error reading {Path(file_path).name}: {e}")
                    continue
            
            # Add to trend data
            trend_data.append({
                "date": display_date,
                "passed": day_passed,
                "failed": day_failed + day_broken,  # Combine failed + broken
                "total": day_passed + day_failed + day_broken
            })
            
            print(f"   ✓ {day_passed} passed, {day_failed + day_broken} failed")
        
        return {
            "all_results": all_results,
            "trend_data": trend_data
        }
    
    def save_output(self, data: Dict[str, Any], output_path: str):
        """Save processed data to JSON files"""
        
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save all results
        all_results_file = output_dir / "all-results.json"
        with open(all_results_file, 'w', encoding='utf-8') as f:
            json.dump(data['all_results'], f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved: {all_results_file}")
        print(f"   Total tests: {len(data['all_results'])}")
        
        # Save trend data
        trend_data_file = output_dir / "trend-data.json"
        with open(trend_data_file, 'w', encoding='utf-8') as f:
            json.dump(data['trend_data'], f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved: {trend_data_file}")
        print(f"   Trend days: {len(data['trend_data'])}")
        
        # Calculate and save statistics
        passed = sum(1 for r in data['all_results'] if r.get('status') == 'passed')
        failed = sum(1 for r in data['all_results'] if r.get('status') in ['failed', 'broken'])
        total = len(data['all_results'])
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        stats = {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(pass_rate, 1),
            "last_updated": datetime.now().isoformat(),
            "days_with_data": len(data['trend_data'])
        }
        
        stats_file = output_dir / "stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Statistics:")
        print(f"   Pass Rate: {stats['pass_rate']}%")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        
        return stats


def scan_and_process():
    """Main scan and process function"""
    print(f"\n{'='*50}")
    print(f"🔍 Scanning at {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*50}\n")
    
    try:
        # Scan folders
        scanner = AllureReportScanner(WATCH_FOLDER)
        folders = scanner.scan_folders()
        
        if not folders:
            print("⚠️  No folders found with format dd-MM-yyyy")
            print(f"   Check: {WATCH_FOLDER}")
            return
        
        print(f"✓ Found {len(folders)} date folders\n")
        
        # Process data
        processor = DataProcessor()
        data = processor.process_folders(folders)
        
        # Save output
        stats = processor.save_output(data, OUTPUT_FOLDER)
        
        print(f"\n{'='*50}")
        print(f"✅ Scan completed successfully!")
        print(f"{'='*50}\n")
        
        return stats
        
    except Exception as e:
        print(f"\n❌ Error during scan: {e}")
        import traceback
        traceback.print_exc()


def watch_continuous():
    """Continuously watch and scan folders"""
    print("🚀 Report Watcher started!\n")
    
    # Initial scan
    scan_and_process()
    
    # Continuous scanning
    while True:
        print(f"\n⏳ Next scan in {SCAN_INTERVAL_SECONDS} seconds ({SCAN_INTERVAL_SECONDS//60} minutes)...")
        print("   Press Ctrl+C to stop\n")
        
        try:
            time.sleep(SCAN_INTERVAL_SECONDS)
            scan_and_process()
        except KeyboardInterrupt:
            print("\n\n👋 Stopping Report Watcher...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            time.sleep(60)  # Wait 1 minute before retry


if __name__ == "__main__":
    try:
        watch_continuous()
    except KeyboardInterrupt:
        print("\n\n✓ Report Watcher stopped")

