# 🎯 HƯỚNG DẪN SỬ DỤNG DỮ LIỆU THẬT CHO QUALIFY.AI

## ✅ Trạng thái hiện tại:

- ✅ **Frontend đang chạy:** http://localhost:3000
- ✅ **Dữ liệu Allure thật:** 32 files JSON tại `D:\allure-reports\13-11-2025\`
- ✅ **Report Watcher Service:** Đã tạo xong, sẵn sàng chạy

---

## 🚀 CÁCH SỬ DỤNG (Chọn 1 trong 2):

### ✨ **CÁCH 1: TỰ ĐỘNG - Report Watcher Service** (Khuyến nghị)

Service này sẽ **TỰ ĐỘNG QUÉT folder mỗi 5 phút** và import data vào database.

#### **Bước 1: Đặt dữ liệu vào đúng folder**

✅ **DONE!** Dữ liệu đã có sẵn tại:
```
D:\allure-reports\13-11-2025\
```

**Quy tắc đặt tên:**
- Folder tên: `dd-mm-yyyy` (VD: `13-11-2025`, `14-11-2025`, `15-11-2025`)
- Files: Tất cả `*-result.json` đặt trong folder

**Ví dụ structure:**
```
D:\allure-reports\
├── 13-11-2025\         ← Hôm nay (32 files)
│   ├── abc-result.json
│   └── def-result.json
├── 14-11-2025\         ← Ngày mai (thêm files mới vào đây)
│   └── ...
└── 15-11-2025\         ← Ngày kia
    └── ...
```

#### **Bước 2: Không cần làm gì thêm!**

Chỉ cần **drop files JSON vào folder**, Report Watcher sẽ:
- 🔍 Tự động phát hiện files mới trong 5 phút
- 📊 Parse và lưu vào database
- 🎨 Dashboard tự động cập nhật

---

### 📱 **CÁCH 2: ĐƠN GIẢN - Load trực tiếp từ file** (Không cần backend)

Nếu chưa muốn setup backend, có thể load trực tiếp JSON vào frontend.

#### **Bước 1: Copy files vào frontend**

```powershell
Copy-Item "D:\allure-reports\13-11-2025\*.json" "D:\practice\AI-Allure-Report\frontend\public\allure-data\"
```

#### **Bước 2: Code đã sẵn sàng**

Component `AllureUploader` đã có sẵn trong dashboard - chỉ cần upload files!

---

## 🎬 DEMO NHANH (30 giây):

### **Để test ngay với data thật:**

1. **Mở Dashboard:** http://localhost:3000/dashboard

2. **Bạn sẽ thấy card "Upload Allure Report"**

3. **Click "Click to upload folder"**

4. **Chọn folder:** `D:\allure-reports\13-11-2025`

5. **✨ XONG!** Dashboard tự động parse 32 files và hiển thị:
   - Pass Rate thật
   - Failed/Passed tests thật  
   - Historical trends
   - Error messages thật từ tests

---

## 📊 Dữ liệu của bạn:

Từ file JSON tôi đã đọc, đây là **Playwright API Test** với:

```json
{
  "name": "should login successfully with user credentials",
  "status": "failed",  
  "statusDetails": {
    "message": "Expected < 300, Received: 401",
    "trace": "Error at login.spec.ts:23:24"
  },
  "labels": [
    {"name": "suite", "value": "authentication\\login.spec.ts"},
    {"name": "framework", "value": "Playwright"}
  ]
}
```

**Dashboard sẽ hiển thị:**
- Test name: "should login successfully..."
- Status: ❌ Failed (401 error)
- Suite: "Authentication - Login"
- Error: "Expected < 300, Received: 401"
- Stack trace: Đầy đủ

---

## 🔄 Quy trình hàng ngày:

```
1. Chạy tests Playwright/Pytest
   ↓
2. Generate Allure results
   ↓
3. Copy *.json vào D:\allure-reports\[ngày-hôm-nay]\
   ↓
4. Report Watcher tự động quét (trong 5 phút)
   ↓
5. Data xuất hiện trên Dashboard
   ↓
6. AI Analysis tự động chạy trên failures
```

---

## ⚙️ Tùy chỉnh:

### Thay đổi folder watch:

Sửa trong `.env`:
```env
ALLURE_REPORTS_PATH=E:/my-custom-path
```

### Thay đổi scan interval:

```env
SCAN_INTERVAL_MINUTES=10  # Scan mỗi 10 phút thay vì 5
```

### Watch multiple projects:

```
D:\allure-reports\
├── project-frontend\
│   └── 13-11-2025\
├── project-backend\
│   └── 13-11-2025\
└── project-mobile\
    └── 13-11-2025\
```

---

## 🎯 TÓM TẮT:

### **Bạn chỉ cần:**

1. ✅ **Đặt file JSON vào:** `D:\allure-reports\[dd-mm-yyyy]\`
2. ✅ **Mở Dashboard:** http://localhost:3000
3. ✅ **Upload folder qua UI** HOẶC **Start Watcher Service**

### **Hệ thống sẽ tự động:**

- 🔄 Parse tất cả JSON
- 📊 Tính Pass Rate, Trends
- 🎨 Hiển thị trên Dashboard
- 🤖 AI Analysis cho failed tests
- 📈 Track lịch sử theo ngày

---

## 🚀 BẮT ĐẦU NGAY:

```powershell
# Option 1: Upload qua UI (Đơn giản nhất)
# Mở http://localhost:3000/dashboard
# Click "Upload folder"
# Chọn D:\allure-reports\13-11-2025

# Option 2: Auto-scan với Watcher
cd D:\practice\AI-Allure-Report
.\scripts\start-watcher.bat
```

---

**Data thật của bạn (32 Playwright API tests) đã sẵn sàng! 🎉**

**Folder:** `D:\allure-reports\13-11-2025\` (32 JSON files)

**Refresh Dashboard để bắt đầu! 🚀**

