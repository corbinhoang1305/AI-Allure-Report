# 📥 How to Re-import Allure Data with Complete Retry Information

## 🎯 Purpose

This guide explains how to properly import Allure test results into the database so that **flaky tests** are accurately detected and displayed in the dashboard.

## ⚠️ Current Situation

The database currently shows:
- **14-11**: 68 passed, 3 failed, **0 flaky**

But the actual Allure JSON files contain:
- **14-11**: 66 passed, 4 flaky, 1 failed

**Why the difference?**
- Database lost retry information during import
- Each test has only 1 result instead of multiple results for retries
- Without multiple results per test, the system cannot detect flaky tests

## 🔍 What Makes a Test Flaky?

According to our verified logic:

```
Flaky Test = Test that:
  1. Failed on FIRST run
  2. Passed on a RETRY attempt
```

To detect this, we need **multiple test results** for the same test case (same `history_id`).

## 📋 Prerequisites

Before importing, ensure:
1. ✅ Allure JSON files are available (e.g., `D:\allure-reports\14-11-2025\`)
2. ✅ Backend services are running
3. ✅ You have API access credentials

## 🔧 Import Methods

### Option 1: Using Report Watcher Service (Recommended)

The Report Watcher service can automatically import Allure reports.

#### Step 1: Check if Report Watcher is Running

```powershell
docker compose ps report-watcher
```

#### Step 2: Configure Report Watcher

Make sure the service is watching the correct folder:

```yaml
# infrastructure/docker-compose/docker-compose.yml
report-watcher:
  environment:
    - WATCH_PATH=/reports
  volumes:
    - D:/allure-reports:/reports
```

#### Step 3: Trigger Import

The service will automatically detect and import new reports.

### Option 2: Manual API Import

If you need more control, use the API directly.

#### Step 1: Prepare the Data

Make sure each test result is imported **in chronological order** with the same `history_id` for retries.

Example data structure:
```json
{
  "run_name": "Test Run 14-11-2025",
  "started_at": "2025-11-14T00:00:00Z",
  "results": [
    {
      "history_id": "abc123",
      "test_name": "should allow admin to update users",
      "status": "failed",
      "created_at": "2025-11-14T00:01:00Z",
      "duration_ms": 810
    },
    {
      "history_id": "abc123",
      "test_name": "should allow admin to update users",
      "status": "failed",
      "created_at": "2025-11-14T00:02:00Z",
      "duration_ms": 1790
    },
    {
      "history_id": "abc123",
      "test_name": "should allow admin to update users",
      "status": "passed",
      "created_at": "2025-11-14T00:03:00Z",
      "duration_ms": 1680
    }
  ]
}
```

#### Step 2: Send to API

```powershell
$data = Get-Content "import_data.json" -Raw
Invoke-RestMethod -Uri "http://localhost:8000/api/aggregator/import" `
  -Method POST `
  -ContentType "application/json" `
  -Body $data `
  -Headers @{ "Authorization" = "Bearer YOUR_TOKEN" }
```

## 🔄 Complete Re-import Process

### Step 1: Clean Existing Data (Optional)

If you want to start fresh:

```sql
-- Delete test results for specific date
DELETE FROM test_results 
WHERE run_id IN (
  SELECT id FROM test_runs 
  WHERE started_at::date = '2025-11-14'
);

-- Delete the test runs
DELETE FROM test_runs 
WHERE started_at::date = '2025-11-14';
```

Run via Docker:
```powershell
docker exec qualify-postgres psql -U qualify -d qualify_db -c "DELETE FROM test_results WHERE run_id IN (SELECT id FROM test_runs WHERE started_at::date = '2025-11-14');"
docker exec qualify-postgres psql -U qualify -d qualify_db -c "DELETE FROM test_runs WHERE started_at::date = '2025-11-14';"
```

### Step 2: Create Import Script

Create a Python script to parse Allure JSON and import with proper retry grouping:

```python
# import_allure_with_retries.py
import json
import requests
from pathlib import Path
from collections import defaultdict
from datetime import datetime

ALLURE_FOLDER = Path("D:/allure-reports/14-11-2025")
API_URL = "http://localhost:8000/api/aggregator/import"
API_TOKEN = "your_token_here"

def parse_allure_results():
    """Parse all Allure result files and group by history_id"""
    test_cases = defaultdict(list)
    
    for json_file in ALLURE_FOLDER.glob("*-result.json"):
        with open(json_file) as f:
            data = json.load(f)
            
            history_id = data.get('historyId')
            test_case_id = data.get('testCaseId')
            test_key = history_id or test_case_id
            
            if not test_key:
                continue
                
            test_cases[test_key].append({
                'history_id': history_id,
                'test_case_id': test_case_id,
                'full_name': data.get('fullName'),
                'test_name': data.get('name'),
                'status': data.get('status'),
                'start': data.get('start'),
                'stop': data.get('stop'),
                'duration_ms': (data.get('stop', 0) - data.get('start', 0))
            })
    
    return test_cases

def create_import_payload(test_cases):
    """Create API payload with all results including retries"""
    results = []
    
    for test_key, runs in test_cases.items():
        # Sort by start time to maintain chronological order
        runs.sort(key=lambda x: x['start'])
        
        for run in runs:
            results.append({
                'history_id': run['history_id'],
                'test_case_id': run['test_case_id'],
                'full_name': run['full_name'],
                'test_name': run['test_name'],
                'status': run['status'],
                'created_at': datetime.fromtimestamp(run['start'] / 1000).isoformat(),
                'duration_ms': run['duration_ms']
            })
    
    return {
        'run_name': 'Import 14-11-2025 with Retries',
        'started_at': '2025-11-14T00:00:00Z',
        'results': results
    }

def import_to_api(payload):
    """Send data to API"""
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(API_URL, json=payload, headers=headers)
    return response

if __name__ == '__main__':
    print("Parsing Allure results...")
    test_cases = parse_allure_results()
    
    print(f"Found {len(test_cases)} unique test cases")
    total_results = sum(len(runs) for runs in test_cases.values())
    print(f"Total results (including retries): {total_results}")
    
    print("\nCreating import payload...")
    payload = create_import_payload(test_cases)
    
    print(f"\nImporting {len(payload['results'])} results to API...")
    response = import_to_api(payload)
    
    if response.status_code == 200:
        print("✅ Import successful!")
        print(response.json())
    else:
        print(f"❌ Import failed: {response.status_code}")
        print(response.text)
```

### Step 3: Run Import Script

```powershell
python import_allure_with_retries.py
```

### Step 4: Verify Import

Check API to see if flaky tests are now detected:

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/analytics/dashboard" `
  -UseBasicParsing | 
  Select-Object -ExpandProperty Content | 
  ConvertFrom-Json | 
  Select-Object -ExpandProperty recent_trends
```

Expected output for 14-11:
```json
{
  "date": "2025-11-14",
  "total": 71,
  "passed": 66,
  "failed": 1,
  "flaky": 4,
  "pass_rate": 98.59
}
```

## ✅ Verification Checklist

After import, verify:

- [ ] Total test count matches (71 tests)
- [ ] Passed tests count matches (66 passed)
- [ ] Flaky tests are detected (4 flaky)
- [ ] Failed tests count matches (1 failed)
- [ ] Historical trend chart shows flaky data
- [ ] Overall health dashboard shows correct metrics

## 🔍 Troubleshooting

### Issue: Flaky tests still showing as 0

**Possible causes:**
1. Results not imported with same `history_id`
2. Results not in chronological order
3. Duplicate data cleanup removed retry information

**Solution:**
- Check database: `SELECT history_id, COUNT(*) FROM test_results GROUP BY history_id HAVING COUNT(*) > 1`
- Should see tests with multiple results

### Issue: Too many flaky tests

**Possible causes:**
1. Duplicate data imports (same data imported twice)
2. Tests that passed are showing as having retries

**Solution:**
- Check for duplicate runs: `SELECT started_at, COUNT(*) FROM test_runs GROUP BY started_at`
- Delete duplicate runs before re-importing

## 📚 Best Practices

1. **Always preserve retry order** - Import results chronologically
2. **Use consistent history_id** - Same test = same history_id
3. **Avoid duplicate imports** - Check if data already exists
4. **Verify after import** - Always check the results
5. **Document import source** - Note where data came from

## 🎯 Expected Results

After correct import, your dashboard will show:

| Date | Total | Passed | Flaky | Failed | Pass Rate |
|------|-------|--------|-------|--------|-----------|
| 13-11 | 71 | 71 | 0 | 0 | 100.0% |
| 14-11 | 71 | 66 | 4 | 1 | 98.59% |
| 15-11 | 71 | 71 | 0 | 0 | 100.0% |

**Flaky tests identified:**
1. should allow admin to update users (3 attempts)
2. should update user with valid data as admin (2 attempts)
3. should fail to create user with missing required field (2 attempts)
4. should allow admin to change user role (2 attempts)

---

**Need Help?**
- Check logs: `docker compose logs analytics`
- Verify data: Use `analyze-allure-folder.ps1` script
- Contact: System administrator

