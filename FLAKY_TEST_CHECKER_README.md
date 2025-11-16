# 🔍 Flaky Test Detector

Script Python để phát hiện **Flaky Tests** từ Allure Reports.

## 📋 Yêu Cầu

### 1. Cài đặt Python
- **Tải về:** https://www.python.org/downloads/
- **Phiên bản:** Python 3.7 trở lên
- ⚠️ **Lưu ý:** Khi cài đặt, nhớ chọn "**Add Python to PATH**"

### 2. Kiểm tra Python đã cài đặt
```powershell
python --version
```
Hoặc:
```powershell
python3 --version
```

---

## 🚀 Cách Sử Dụng

### Cách 1: Chạy với folder mặc định (14-11-2025)
```powershell
python check_flaky_tests.py
```

### Cách 2: Chỉ định folder cụ thể
```powershell
python check_flaky_tests.py "D:\allure-reports\14-11-2025"
```

### Cách 3: Không export file JSON
```powershell
python check_flaky_tests.py "D:\allure-reports\14-11-2025" --no-export
```

---

## 📊 Flaky Test Là Gì?

**Flaky Test** là test có kết quả không ổn định:
- Đôi khi **PASS** ✅
- Đôi khi **FAIL** ❌
- Mà không có thay đổi code

### Ví dụ:
```
Run 1: test_login() → PASSED ✅
Run 2: test_login() → FAILED ❌
Run 3: test_login() → PASSED ✅
Run 4: test_login() → BROKEN 💔
```
→ Đây là **FLAKY TEST**!

---

## 🔍 Script Làm Gì?

Script sẽ:

1. **Quét tất cả file JSON** trong folder `14-11-2025`
2. **Phân tích kết quả** của mỗi test
3. **Group tests** theo:
   - `testCaseId`
   - `historyId` 
   - `fullName`
4. **Phát hiện flaky tests** - Tests có nhiều lần chạy với status khác nhau
5. **Báo cáo chi tiết**:
   - Tổng quan thống kê
   - Danh sách flaky tests
   - Chi tiết mỗi lần chạy
6. **Export ra file JSON** để phân tích sau

---

## 📄 Output

### 1. Console Output

```
================================================================================
🔍 FLAKY TEST DETECTOR - Allure Reports Analyzer
================================================================================
🔍 Đang quét folder: D:\allure-reports\14-11-2025
================================================================================
✅ Đã load 71 file JSON result

🔬 Đang phân tích test results...
🔄 Đang tìm kiếm flaky tests...

================================================================================
📊 TỔNG QUAN THỐNG KÊ
================================================================================
📁 Folder: D:\allure-reports\14-11-2025
📄 Tổng số test results: 71
✅ Passed: 66
❌ Failed: 1
💔 Broken: 0
⏭️  Skipped: 0
❓ Unknown: 0

🔄 Tổng số FLAKY TESTS phát hiện: 4

================================================================================
⚠️  DANH SÁCH FLAKY TESTS
================================================================================

────────────────────────────────────────────────────────────────────────────────
🔄 Flaky Test #1
────────────────────────────────────────────────────────────────────────────────
📝 Test Name: should handle rate limiting correctly
📍 Full Name: api-tests/rate-limit.spec.ts#Rate Limiting should handle rate limiting correctly
🆔 Identifier (testCaseId): abc123def456
📊 Số lần xuất hiện: 3
⚡ Các trạng thái khác nhau: failed, passed

   Chi tiết các lần chạy:
   Run 1: ✅ PASSED   | Duration: 1.23s | File: abc-123-result.json
   Run 2: ❌ FAILED   | Duration: 5.67s | File: def-456-result.json
   Run 3: ✅ PASSED   | Duration: 1.45s | File: ghi-789-result.json

────────────────────────────────────────────────────────────────────────────────
```

### 2. JSON Report File

File được tạo: `flaky_tests_report_YYYYMMDD_HHMMSS.json`

```json
{
  "folder": "D:\\allure-reports\\14-11-2025",
  "scan_time": "2025-11-15T21:30:00",
  "statistics": {
    "total": 71,
    "passed": 66,
    "failed": 1,
    "flaky_count": 4
  },
  "flaky_tests": [
    {
      "test_name": "should handle rate limiting correctly",
      "full_name": "api-tests/rate-limit.spec.ts#...",
      "identifier": "abc123def456",
      "identifier_type": "testCaseId",
      "occurrences": 3,
      "statuses": ["passed", "failed"],
      "runs": [
        {
          "status": "passed",
          "file": "abc-123-result.json",
          "duration_ms": 1230
        },
        {
          "status": "failed",
          "file": "def-456-result.json",
          "duration_ms": 5670
        }
      ]
    }
  ]
}
```

---

## 🎯 Cách Phát Hiện Flaky Tests

Script sử dụng 3 cách để group tests:

### 1. **Theo testCaseId** (Ưu tiên cao nhất)
- Mỗi test có một `testCaseId` duy nhất
- Nếu cùng `testCaseId` mà khác `status` → Flaky!

### 2. **Theo historyId**
- Allure tracking test history qua `historyId`
- Nếu cùng `historyId` mà khác `status` → Flaky!

### 3. **Theo fullName** (Fallback)
- Nếu không có ID, dùng `fullName`
- Nếu cùng `fullName` mà khác `status` → Flaky!

---

## 📁 Cấu Trúc File

```
D:\allure-reports\14-11-2025\
├── abc-123-result.json          # Test result 1
├── def-456-result.json          # Test result 2
├── ghi-789-result.json          # Test result 3
└── ...
```

Mỗi file JSON chứa:
```json
{
  "uuid": "abc-123-...",
  "testCaseId": "unique-test-id",
  "historyId": "history-id",
  "name": "Test name",
  "fullName": "path/to/test#Test name",
  "status": "passed",  // hoặc "failed", "broken", "skipped"
  "start": 1234567890,
  "stop": 1234567899,
  "labels": [...],
  "steps": [...]
}
```

---

## 🔧 Tùy Chỉnh Script

### Thay đổi folder mặc định:

Mở file `check_flaky_tests.py`, tìm dòng:
```python
default_folder = r"D:\allure-reports\14-11-2025"
```

Thay đổi thành:
```python
default_folder = r"D:\allure-reports\YOUR_FOLDER"
```

### Thêm status mới:

Trong hàm `print_report()`, thêm icon mới:
```python
status_icon = {
    'passed': '✅',
    'failed': '❌',
    'broken': '💔',
    'skipped': '⏭️',
    'your_status': '🎯'  # Thêm status mới
}.get(test['status'], '❓')
```

---

## 📚 Ví Dụ Thực Tế

### Scenario: Bạn có 71 test results

```
66 tests: PASSED ✅
1 test:  FAILED ❌
4 tests: Có kết quả thay đổi (FLAKY)
```

Chạy script:
```powershell
python check_flaky_tests.py
```

Kết quả:
- Script sẽ liệt kê **4 flaky tests**
- Hiển thị chi tiết từng lần chạy
- Export ra file JSON để lưu trữ

---

## ⚠️ Lưu Ý

### 1. File phải có format đúng
- Chỉ quét file có tên: `*-result.json`
- Bỏ qua file `*-attachment.zip`

### 2. Cần ít nhất 2 lần chạy
- Để phát hiện flaky, cần test chạy ít nhất 2 lần
- Nếu test chỉ chạy 1 lần → Không thể xác định flaky

### 3. Status hợp lệ
- `passed`: Test thành công
- `failed`: Test thất bại  
- `broken`: Test bị lỗi
- `skipped`: Test bị bỏ qua

---

## 🐛 Khắc Phục Sự Cố

### Lỗi: Python không được tìm thấy
```
Python was not found...
```

**Giải pháp:**
1. Tải Python: https://www.python.org/downloads/
2. Cài đặt và chọn "Add Python to PATH"
3. Restart terminal/PowerShell
4. Kiểm tra: `python --version`

### Lỗi: Folder không tồn tại
```
❌ Lỗi: Folder không tồn tại: ...
```

**Giải pháp:**
1. Kiểm tra đường dẫn folder
2. Đảm bảo folder có file JSON
3. Chỉ định đúng đường dẫn:
   ```powershell
   python check_flaky_tests.py "D:\path\to\your\folder"
   ```

### Lỗi: Không có file JSON
```
❌ Không tìm thấy file JSON nào để phân tích!
```

**Giải pháp:**
1. Kiểm tra folder có file `*-result.json`
2. Đảm bảo file không bị corrupt
3. Thử folder khác

---

## 📞 Support

Nếu gặp vấn đề, kiểm tra:
1. ✅ Python đã cài đặt
2. ✅ Đường dẫn folder đúng
3. ✅ Có file JSON trong folder
4. ✅ File JSON format hợp lệ

---

## 🎉 Kết Luận

Script này giúp bạn:
- ✅ Tự động phát hiện flaky tests
- ✅ Tiết kiệm thời gian debug
- ✅ Cải thiện chất lượng test suite
- ✅ Export báo cáo để phân tích

**Sử dụng ngay:** 
```powershell
python check_flaky_tests.py
```

---

**Happy Testing!** 🚀


