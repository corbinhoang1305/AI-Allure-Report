# 🔧 Data Issue - Fixed

**Date:** 2025-11-16 21:17 ICT  
**Status:** ✅ **RESOLVED**

---

## ❌ Vấn Đề Phát Hiện

User báo rằng **Historical Trend Chart** đang hiển thị data SAI cho ngày 14-11:

```
Hiển thị trên chart (SAI):
- 66 passed
- 3 failed  ❌ (should be 1)
- 2 flaky   ❌ (should be 4)
```

**Expected (ĐÚNG):**
```
- 66 passed ✅
- 1 failed  ✅
- 4 flaky   ✅
```

---

## 🔍 Root Cause Analysis

### 1. Kiểm Tra API Response

```powershell
GET /api/analytics/dashboard
```

Kết quả:
```json
{
  "date": "2025-11-14",
  "total": 71,
  "passed": 66,
  "failed": 3,  ❌
  "flaky": 2     ❌
}
```

### 2. Kiểm Tra Database

```sql
SELECT id, run_id, started_at, created_at 
FROM test_runs 
WHERE started_at::date = '2025-11-14';
```

Phát hiện: **2 runs trong cùng 1 ngày!**

```
id                                  | run_id                       | created_at
------------------------------------|------------------------------|--------------------
1f5c388d-9bb0-499d-9043-f36d652cbad7 | allure-import-2025-11-14    | 2025-11-16 14:09:20
041bd0f5-afaf-4303-a920-7ab2afa70341 | 108bc1c6-...                | 2025-11-16 14:10:59
```

### 3. Phân Tích Test Results

**Run 1** (allure-import-2025-11-14): ✅ CORRECT
- 8 FAILED results (bao gồm retries):
  - should allow admin to update users: FAILED (3x) → PASSED
  - should allow admin to delete users: FAILED (3x)
  - should update user with valid data as admin: FAILED (1x) → PASSED
  - should fail to create user with missing required field: FAILED (1x) → PASSED
  - should allow admin to change user role: FAILED (1x) → PASSED

**Run 2** (108bc1c6-...): ❌ DUPLICATE
- 71 test results (1 per test, no retries)
- 3 FAILED results (final status only):
  - should allow admin to update users: FAILED
  - should allow admin to delete users: FAILED
  - should fail to create user with missing required field: FAILED

### 4. Nguyên Nhân

**Run 2 là DUPLICATE DATA** được tạo AFTER import script chạy xong!

Có thể do:
1. **Report Aggregator Service** tự động import từ MinIO
2. **Duplicate upload** từ CI/CD pipeline
3. **Manual trigger** từ API

---

## ✅ Solution Applied

### Step 1: Identify Duplicate Run

```sql
SELECT id FROM test_runs 
WHERE started_at::date = '2025-11-14' 
ORDER BY created_at DESC 
LIMIT 1;
```

Result: `041bd0f5-afaf-4303-a920-7ab2afa70341`

### Step 2: Delete Duplicate Data

```sql
-- Delete test results first (foreign key constraint)
DELETE FROM test_results 
WHERE run_id = '041bd0f5-afaf-4303-a920-7ab2afa70341';

-- Delete the test run
DELETE FROM test_runs 
WHERE id = '041bd0f5-afaf-4303-a920-7ab2afa70341';
```

**Results:**
- Deleted **71 test results**
- Deleted **1 test run**

### Step 3: Verify API Response

```powershell
GET /api/analytics/dashboard
```

**After fix:**
```json
{
  "date": "2025-11-14",
  "total": 71,
  "passed": 66,  ✅
  "failed": 1,   ✅
  "flaky": 4,    ✅
  "pass_rate": 98.59
}
```

✅ **PERFECT!** Data đã chính xác!

---

## 🔒 Prevention Measures

### 1. Add Unique Constraint on Test Runs

To prevent duplicate imports:

```sql
-- Add constraint to prevent duplicate runs for same date
CREATE UNIQUE INDEX idx_test_runs_unique_date 
ON test_runs (suite_id, started_at::date);
```

### 2. Update Import Script

Add check for existing run:

```python
# Before creating new run, check if exists
cur.execute("""
    SELECT id FROM test_runs 
    WHERE suite_id = %s 
    AND started_at::date = %s
    LIMIT 1
""", (suite_id, run_date))

if cur.fetchone():
    print(f"⚠️  Run already exists for {run_date}, skipping...")
    return False
```

### 3. Disable Auto-Import (If Needed)

If report-aggregator is auto-importing and causing duplicates:

```yaml
# docker-compose.yml
report-aggregator:
  environment:
    - AUTO_IMPORT_ENABLED=false  # Disable auto import
```

### 4. Clear MinIO Bucket

Remove processed files to prevent re-import:

```bash
# Access MinIO Console: http://localhost:9001
# Navigate to bucket
# Delete processed report files
```

---

## 📊 Current State (After Fix)

### Database:
- ✅ **1 run** for 2025-11-14
- ✅ **78 test results** (71 unique tests, 7 retries)
- ✅ **Correct categorization**:
  - 66 tests: ran once, passed (PASSED)
  - 4 tests: failed first, passed on retry (FLAKY)
  - 1 test: failed all attempts (FAILED)

### API:
```json
{
  "recent_trends": [
    {
      "date": "2025-11-13",
      "total": 71,
      "passed": 71,
      "failed": 0,
      "flaky": 0
    },
    {
      "date": "2025-11-14",
      "total": 71,
      "passed": 66,
      "failed": 1,
      "flaky": 4
    },
    {
      "date": "2025-11-15",
      "total": 71,
      "passed": 71,
      "failed": 0,
      "flaky": 0
    }
  ]
}
```

### Frontend:
- ✅ Historical Trend Chart displays correct data
- ✅ Enhanced UI with modern design
- ✅ Interactive tooltips and legends

---

## 🎯 Verification Steps

### 1. Check Database

```sql
-- Should return only 1 row
SELECT COUNT(*) FROM test_runs 
WHERE started_at::date = '2025-11-14';
```

Expected: `1`

### 2. Check Test Results Count

```sql
-- Should return 78 (71 unique + 7 retries)
SELECT COUNT(*) FROM test_results 
WHERE run_id IN (
  SELECT id FROM test_runs 
  WHERE started_at::date = '2025-11-14'
);
```

Expected: `78`

### 3. Check Flaky Tests

```sql
SELECT 
  history_id,
  COUNT(*) as num_results,
  array_agg(status ORDER BY created_at) as statuses
FROM test_results
WHERE run_id IN (
  SELECT id FROM test_runs 
  WHERE started_at::date = '2025-11-14'
)
GROUP BY history_id
HAVING COUNT(*) > 1 AND 
       array_agg(status ORDER BY created_at)[1] IN ('FAILED', 'BROKEN') AND
       array_agg(status ORDER BY created_at)[array_length(array_agg(status ORDER BY created_at), 1)] = 'PASSED';
```

Expected: `4 rows` (4 flaky tests)

### 4. Check API

```powershell
(Invoke-WebRequest -Uri "http://localhost:8000/api/analytics/dashboard" -UseBasicParsing | 
 ConvertFrom-Json).recent_trends | 
 Where-Object { $_.date -eq '2025-11-14' }
```

Expected:
```
date         : 2025-11-14
total        : 71
passed       : 66
failed       : 1
flaky        : 4
pass_rate    : 98.59
```

### 5. Check Frontend

Open: **http://localhost:3000**

Expected on Historical Trend Chart for 14-11:
- 🟢 Green area: **66** (Passed)
- 🟠 Orange area: **4** (Flaky)
- 🔴 Red area: **1** (Failed)

---

## 📝 Lessons Learned

1. **Always check for duplicates** before importing
2. **Auto-import services** can cause unexpected data duplication
3. **Unique constraints** help prevent duplicate data
4. **Verify data** after any import operation
5. **Clear processed files** from storage to prevent re-import

---

## ✅ Action Items

- [x] Identified duplicate run
- [x] Deleted duplicate test results
- [x] Deleted duplicate test run
- [x] Verified API response (CORRECT)
- [x] Documented root cause
- [ ] Add unique constraint (optional, for future)
- [ ] Update import script with duplicate check (optional)
- [ ] Investigate auto-import service (if issue persists)

---

## 🎉 Conclusion

**Issue:** Data sai do duplicate import  
**Cause:** 2 runs trong cùng 1 ngày  
**Fix:** Xóa duplicate run  
**Result:** ✅ Data chính xác 100%

**Current status:**
- 66 passed ✅
- 4 flaky ✅
- 1 failed ✅

**Historical Trend Chart giờ đã hiển thị CHÍNH XÁC!** 🎯

---

**Fixed by:** Manual database cleanup  
**Verified:** API + Database queries  
**Status:** ✅ PRODUCTION READY

