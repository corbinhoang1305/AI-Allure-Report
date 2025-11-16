# 📊 Logic Phân Loại Test Results - Passed, Flaky, Failed

## 🎯 Vấn Đề

**Trước đây:** Khi có retry, tổng số test results != tổng số test cases thực tế, dẫn đến thống kê không chính xác.

**Ví dụ:**
```
Test A: Run 1 FAILED → Run 2 PASSED (retry)
Test B: Run 1 PASSED (no retry)
Test C: Run 1 FAILED (no retry)

❌ Logic cũ:
- Total results: 4 (đếm cả retry!)
- Passed: 2
- Failed: 2
- → Sai! Thực tế chỉ có 3 test cases

✅ Logic mới:
- Total test cases: 3 (unique tests)
- Passed: 1 (Test B - chạy 1 lần passed)
- Flaky: 1 (Test A - passed sau khi retry)
- Failed: 1 (Test C - failed)
```

---

## 🔄 Logic Mới

### Định Nghĩa

#### 1. **Passed (Ổn định)**
- Test chạy **1 lần duy nhất** và **PASSED**
- Không có retry
- Test hoạt động ổn định

```python
if num_runs == 1 and final_status == PASSED:
    → PASSED
```

#### 2. **Flaky (Không ổn định)**
- Test **có retry** (chạy nhiều hơn 1 lần)
- Kết quả cuối cùng là **PASSED**
- Test không ổn định nhưng cuối cùng vẫn pass

```python
if num_runs > 1 and final_status == PASSED:
    → FLAKY
```

**Ví dụ Flaky:**
```
Run 1: FAILED (0.8s)
Run 2: PASSED (1.6s)
→ FLAKY (passed sau retry)
```

#### 3. **Failed (Thất bại)**
- **Trường hợp 1:** Test chạy 1 lần và FAILED
- **Trường hợp 2:** Test có retry nhưng vẫn FAILED
- Test thực sự có vấn đề

```python
if final_status in [FAILED, BROKEN]:
    → FAILED
```

**Ví dụ Failed:**
```
# Trường hợp 1: No retry
Run 1: FAILED
→ FAILED

# Trường hợp 2: Failed sau retry
Run 1: FAILED
Run 2: FAILED
Run 3: FAILED
→ FAILED (thật sự broken)
```

---

## 🔍 Cách Xác Định

### Bước 1: Group theo Test Case ID

Sử dụng `history_id`, `testCaseId`, hoặc `fullName` để group các results của cùng 1 test case:

```python
# Group all results for each unique test case
test_cases_by_date[date][test_key] = [
    result1,  # Run 1
    result2,  # Run 2 (retry)
    ...
]
```

### Bước 2: Đếm Số Lần Chạy

```python
num_runs = len(results_list)
```

### Bước 3: Lấy Status Cuối Cùng

```python
# Sort by created_at để có thứ tự chạy
results_list.sort(key=lambda x: x.created_at)

# Lấy kết quả cuối cùng
final_status = results_list[-1].status
```

### Bước 4: Phân Loại

```python
if num_runs == 1:
    if final_status == PASSED:
        → PASSED (ổn định)
    elif final_status == FAILED:
        → FAILED (thất bại)
else:  # num_runs > 1 (có retry)
    if final_status == PASSED:
        → FLAKY (pass sau retry)
    elif final_status == FAILED:
        → FAILED (fail dù có retry)
```

---

## 📊 Historical Trend Chart

### Data Structure

```typescript
{
  date: "2025-11-14",
  total: 71,        // Unique test cases (không đếm retry)
  passed: 66,       // Chạy 1 lần và passed
  flaky: 4,         // Có retry nhưng passed cuối cùng
  failed: 1,        // Failed (với hoặc không retry)
  pass_rate: 98.6   // (passed + flaky) / total * 100
}
```

### Chart Display

```
┌─────────────────────────────────────┐
│  Historical Trends (30 days)       │
├─────────────────────────────────────┤
│                                     │
│     🟢 Passed (Ổn định)            │
│     🟠 Flaky (Retry thành công)    │
│     🔴 Failed (Thất bại)           │
│                                     │
│  70│                              🟢│
│  60│                          🟢  🟢│
│  50│                      🟠  🟢  🟢│
│  40│                  🟠  🟠  🟢  🟢│
│  30│              🔴  🟠  🟠  🟢  🟢│
│  20│          🔴  🔴  🟠  🟠  🟢  🟢│
│  10│      🔴  🔴  🔴  🟠  🟠  🟢  🟢│
│   0└──────────────────────────────┘ │
│     D1  D2  D3  D4  D5  D6  D7     │
└─────────────────────────────────────┘
```

---

## 💻 Implementation

### Backend: Analytics Service

**File:** `backend/services/analytics-service/app/main.py`

#### 1. **get_trends() Function**

```python
async def get_trends(project_id, period, db):
    # Group by history_id
    test_cases_by_date[date][test_key] = []
    
    # Collect ALL results for each test case
    for test_result in results:
        test_key = test_result.history_id
        test_cases_by_date[date][test_key].append(test_result)
    
    # Analyze each test case
    for test_key, results_list in test_cases.items():
        results_list.sort(key=lambda x: x.created_at)
        
        num_runs = len(results_list)
        final_status = results_list[-1].status
        
        if num_runs == 1:
            if final_status == PASSED:
                passed_count += 1
            elif final_status == FAILED:
                failed_count += 1
        else:
            if final_status == PASSED:
                flaky_count += 1
            elif final_status == FAILED:
                failed_count += 1
    
    return {
        "date": date,
        "total": passed + flaky + failed,
        "passed": passed,
        "flaky": flaky,
        "failed": failed,
        "pass_rate": (passed + flaky) / total * 100
    }
```

#### 2. **get_overall_health() Function**

```python
async def get_overall_health(project_id, db):
    # Similar logic to get_trends
    # Group by history_id → Analyze → Return stats
    
    return {
        "total_tests": passed + flaky + failed,
        "passed": passed_count,
        "failed": failed_count,
        "flaky": flaky_count,
        "pass_rate": (passed + flaky) / total * 100
    }
```

### Frontend: TrendChart Component

**File:** `frontend/components/dashboard/TrendChart.tsx`

```typescript
interface TrendChartProps {
  data: Array<{
    date: string;
    passed: number;
    failed: number;
    flaky: number;  // ← Thêm flaky
  }>;
}

// Chart areas
<Area dataKey="passed" stroke="#00D9B5" fill="url(#colorPassed)" />
<Area dataKey="flaky" stroke="#FFA500" fill="url(#colorFlaky)" />
<Area dataKey="failed" stroke="#FF6B6B" fill="url(#colorFailed)" />
```

**Colors:**
- 🟢 **Passed:** `#00D9B5` (Green)
- 🟠 **Flaky:** `#FFA500` (Orange)
- 🔴 **Failed:** `#FF6B6B` (Red)

---

## 📈 Pass Rate Calculation

### Logic

```
pass_rate = (passed + flaky) / total * 100
```

**Lý do:**
- Flaky tests cuối cùng vẫn PASSED
- Pass rate nên tính cả tests passed sau retry
- Chỉ có Failed tests mới thực sự "không pass"

### Ví dụ

```
Total: 71 tests
- Passed: 66 (93.0%)
- Flaky: 4 (5.6%)
- Failed: 1 (1.4%)

Pass Rate = (66 + 4) / 71 * 100 = 98.6%
```

---

## 🎯 Lợi Ích

### 1. **Chính Xác Hơn**
- Đếm đúng số lượng test cases thực tế
- Không bị duplicate khi có retry

### 2. **Phát Hiện Flaky Tests**
- Nhìn thấy rõ tests không ổn định
- Track flaky tests theo thời gian

### 3. **Better Decision Making**
- Passed: Tests ổn định, không cần action
- Flaky: Cần fix để improve stability
- Failed: Cần fix ngay lập tức

### 4. **Trend Analysis**
```
Week 1: Passed 60 | Flaky 8 | Failed 3
Week 2: Passed 65 | Flaky 4 | Failed 2
Week 3: Passed 70 | Flaky 1 | Failed 0
→ Quality đang improve! ✅
```

---

## 📊 Real Data Example

### Ngày 14-11-2025

**Raw Results:** 78 test results

**Analyzed:**
```
Total unique tests: 71
├─ Passed: 66 (chạy 1 lần passed)
├─ Flaky: 4 (có retry, cuối cùng passed)
│  ├─ Test 1: admin update users (3 runs: F→P→F→P)
│  ├─ Test 2: create user missing field (2 runs: P→F)
│  ├─ Test 3: admin change role (2 runs: F→P)
│  └─ Test 4: update user valid data (2 runs: F→P)
└─ Failed: 1 (failed không retry hoặc retry vẫn failed)

Pass Rate: (66 + 4) / 71 = 98.6%
```

**Insight:**
- 92.9% tests ổn định (passed ngay lần đầu)
- 5.6% tests flaky (cần fix để improve stability)
- 1.4% tests failed (cần fix urgent)

---

## 🔧 Testing Logic

### Test Cases

```python
def test_passed_logic():
    results = [create_result(status=PASSED, created_at=now)]
    assert categorize(results) == PASSED

def test_flaky_logic():
    results = [
        create_result(status=FAILED, created_at=now),
        create_result(status=PASSED, created_at=now + 1s)
    ]
    assert categorize(results) == FLAKY

def test_failed_with_retry():
    results = [
        create_result(status=FAILED, created_at=now),
        create_result(status=FAILED, created_at=now + 1s)
    ]
    assert categorize(results) == FAILED

def test_failed_no_retry():
    results = [create_result(status=FAILED, created_at=now)]
    assert categorize(results) == FAILED
```

---

## 🚀 Deployment

### 1. Backend Changes
```bash
cd infrastructure/docker-compose
docker compose up -d --build analytics
```

### 2. Frontend Changes
```bash
# Frontend tự động rebuild khi save file
# Hoặc restart:
cd frontend
npm run dev
```

### 3. Verify
```bash
# Check API response
curl http://localhost:8004/trends?period=7d

# Response should include:
{
  "data_points": [
    {
      "date": "2025-11-14",
      "total": 71,
      "passed": 66,
      "flaky": 4,     ← Thêm field này!
      "failed": 1,
      "pass_rate": 98.6
    }
  ]
}
```

---

## 📚 Summary

| Aspect | Old Logic | New Logic |
|--------|-----------|-----------|
| **Total** | Count all results (with retries) | Count unique test cases |
| **Passed** | All passed results | Passed on first run only |
| **Failed** | All failed results | Failed (with or without retry) |
| **Flaky** | ❌ Not tracked | ✅ **Passed after retry** |
| **Pass Rate** | passed / total | (passed + flaky) / total |
| **Accuracy** | ❌ Inflated by retries | ✅ Accurate test case count |

---

## 🎓 Key Takeaways

1. ✅ **Total = Unique test cases** (không đếm retry)
2. ✅ **Passed = Chạy 1 lần và passed** (ổn định)
3. ✅ **Flaky = Có retry nhưng passed cuối cùng** (không ổn định)
4. ✅ **Failed = Failed cuối cùng** (có hoặc không retry)
5. ✅ **Pass Rate = (Passed + Flaky) / Total** (vì flaky vẫn pass)

---

**Updated:** 16/11/2025  
**Version:** 2.0 - With Flaky Detection

