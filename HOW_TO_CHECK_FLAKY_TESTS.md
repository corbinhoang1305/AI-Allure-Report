# 🚀 Cách Kiểm Tra Flaky Tests - Quick Guide

## ⚡ Cách Nhanh Nhất (Không Cần Python)

### Chạy Script PowerShell:

```powershell
.\check-flaky-tests-quick.ps1
```

**Kết quả:** Script sẽ:
- ✅ Quét tất cả file JSON trong folder `14-11-2025`
- ✅ Phát hiện tests có kết quả không ổn định
- ✅ Hiển thị báo cáo chi tiết trên console
- ✅ Tạo file CSV: `flaky_tests_report_YYYYMMDD_HHMMSS.csv`

---

## 🐍 Cách Dùng Python (Đầy Đủ Tính Năng)

### 1. Cài Python (Nếu chưa có)
- Tải: https://www.python.org/downloads/
- ⚠️ **Nhớ chọn:** "Add Python to PATH"

### 2. Chạy Script:

```powershell
python check_flaky_tests.py
```

**Kết quả:** Script sẽ:
- ✅ Phân tích chi tiết hơn
- ✅ Export file JSON với thông tin đầy đủ
- ✅ Có thể tùy chỉnh nhiều hơn

---

## 📁 Kiểm Tra Folder Khác

### PowerShell:
```powershell
.\check-flaky-tests-quick.ps1 -FolderPath "D:\allure-reports\15-11-2025"
```

### Python:
```powershell
python check_flaky_tests.py "D:\allure-reports\15-11-2025"
```

---

## 📊 Kết Quả Folder 14-11-2025

### Tìm thấy: **4 Flaky Tests** ⚠️

1. ❌ `should allow admin to update users` (3 runs: 2 failed, 1 passed)
2. ❌ `should fail to create user with missing required field` (2 runs: 1 failed, 1 passed)
3. ❌ `should allow admin to change user role` (2 runs: 1 failed, 1 passed)
4. ❌ `should update user with valid data as admin` (2 runs: 1 failed, 1 passed)

### Xem chi tiết: `FLAKY_TESTS_RESULT.md`

---

## 🎯 Files Quan Trọng

| File | Mô Tả |
|------|-------|
| `check-flaky-tests-quick.ps1` | ⚡ Script PowerShell (Không cần Python) |
| `check_flaky_tests.py` | 🐍 Script Python (Đầy đủ tính năng) |
| `check-flaky-tests.bat` | 📦 Batch file (Double-click để chạy) |
| `FLAKY_TEST_CHECKER_README.md` | 📚 Hướng dẫn chi tiết đầy đủ |
| `FLAKY_TESTS_RESULT.md` | 📊 Kết quả phân tích chi tiết |

---

## 💡 Flaky Test Là Gì?

Test có kết quả **không ổn định**:
- Lần 1: ✅ PASS
- Lần 2: ❌ FAIL
- Lần 3: ✅ PASS
- → **FLAKY!**

---

## ✅ Next Steps

1. **Xem báo cáo:** `FLAKY_TESTS_RESULT.md`
2. **Fix tests:** Theo khuyến nghị trong báo cáo
3. **Re-run:** Kiểm tra lại sau khi fix
4. **Mục tiêu:** 0 flaky tests! 🎯

---

**Quick Start:** `.\check-flaky-tests-quick.ps1` 🚀


