# 🚀 QUALIFY.AI - Quick Start với Dữ liệu Thật

## ✅ Đã sẵn sàng:

- ✅ Frontend đang chạy: http://localhost:3000
- ✅ 32 Allure JSON files tại: `D:\allure-reports\13-11-2025\`
- ✅ Report Watcher Service đã được tạo

---

## 📂 NƠI ĐẶT DỮ LIỆU JSON:

### **Cấu trúc folder:**

```
D:\allure-reports\
├── 13-11-2025\              ← Folder hôm nay (NGÀY-THÁNG-NĂM)
│   ├── abc123-result.json   ← Allure result files
│   ├── def456-result.json
│   └── ... (32 files hiện có)
│
├── 14-11-2025\              ← Ngày mai
│   └── [đặt JSON files mới vào đây]
│
└── 15-11-2025\              ← Các ngày tiếp theo
    └── ...
```

### **Quy tắc đặt tên folder:**

- Format: `dd-MM-yyyy` (VD: `13-11-2025`, `01-12-2025`)
- Chữ thường, dùng dấu gạch ngang `-`

---

## 🎯 CÁCH HOẠT ĐỘNG:

### **Report Watcher Service sẽ:**

```
1. Quét folder D:\allure-reports\ mỗi 5 phút
   ↓
2. Tìm các folder dd-MM-yyyy
   ↓
3. Parse tất cả *-result.json trong mỗi folder
   ↓
4. Lưu vào PostgreSQL database
   ↓
5. Frontend tự động refresh mỗi 5 phút
   ↓
6. Dashboard hiển thị data thật!
```

---

## 🚀 CHẠY NGAY (2 bước):

### **Bước 1: Start Database**

```powershell
cd D:\practice\AI-Allure-Report\infrastructure\docker-compose
docker-compose up -d postgres redis
```

Đợi 10 giây để database khởi động.

### **Bước 2: Start Report Watcher**

```powershell
cd D:\practice\AI-Allure-Report
.\scripts\start-watcher.bat
```

**Xong!** Service sẽ:
- 🔍 Quét `D:\allure-reports\13-11-2025\` ngay lập tức
- 📊 Parse 32 JSON files
- 💾 Import vào database
- 🔄 Tiếp tục quét mỗi 5 phút

### **Bước 3: Xem Dashboard**

Frontend tự động refresh:
- URL: http://localhost:3000/dashboard
- Data từ backend API
- Update mỗi 5 phút

---

## 📝 THÊM DATA MỚI MỖI NGÀY:

### **Tự động tạo folder cho hôm nay:**

```powershell
$today = Get-Date -Format "dd-MM-yyyy"
New-Item -ItemType Directory -Path "D:\allure-reports\$today"
```

### **Copy Allure results vào:**

```powershell
# Sau khi chạy tests (Playwright/Pytest)
Copy-Item "path/to/allure-results/*-result.json" "D:\allure-reports\$today\"
```

### **Watcher tự động xử lý:**

- ⏱️ Trong vòng 5 phút, data sẽ xuất hiện trên Dashboard
- 📊 Không cần làm gì thêm!

---

## 🔍 KIỂM TRA STATUS:

### **Watcher Service:**

```powershell
# Xem status
curl http://localhost:8005/scan/status

# Response:
# {
#   "status": "running",
#   "watch_folder": "D:/allure-reports",
#   "scan_interval_minutes": 5,
#   "processed_files_count": 32,
#   "next_scan": "2025-11-13T12:45:00"
# }
```

### **Trigger scan thủ công:**

```powershell
curl -X POST http://localhost:8005/scan/trigger
```

### **Reset để scan lại:**

```powershell
curl -X DELETE http://localhost:8005/scan/reset
```

---

## 🎨 Dashboard Features với Data Thật:

Khi có data thật, Dashboard sẽ hiển thị:

- ✅ **Pass Rate thực tế** từ 32 tests
- ✅ **Failed Tests** với error messages chi tiết
- ✅ **Historical Trends** theo ngày
- ✅ **Test Suites** từ labels (Authentication, Login, etc.)
- ✅ **AI Root Cause Analysis** trên failed tests thật
- ✅ **Flaky Test Detection** khi có đủ lịch sử

---

## 🔧 Configuration:

### **Thay đổi folder watch:**

File: `backend/services/report-watcher/.env`

```env
ALLURE_REPORTS_PATH=E:/my-custom-path
```

### **Thay đổi scan interval:**

```env
SCAN_INTERVAL_MINUTES=10  # Quét mỗi 10 phút
```

---

## 🐛 Troubleshooting:

### **Dashboard vẫn hiển thị mock data?**

**Kiểm tra:**
```powershell
# 1. Database đang chạy?
docker ps | findstr postgres

# 2. Watcher đang chạy?
curl http://localhost:8005/health

# 3. Data đã được import?
curl http://localhost:8005/scan/status
```

### **Watcher không quét?**

**Check:**
- ✅ Folder name đúng format `dd-MM-yyyy`
- ✅ Files có đuôi `-result.json`
- ✅ JSON files hợp lệ

---

## 📋 TÓM TẮT:

### **Đặt data ở đây:**
```
D:\allure-reports\[dd-MM-yyyy]\*.json
```

### **Service quét:**
- ⏰ Mỗi 5 phút
- 🔍 Tự động tìm folders mới
- 📊 Parse và import
- 🔄 Frontend auto-refresh

### **Không cần:**
- ❌ Upload thủ công
- ❌ Click buttons
- ❌ Copy files
- ❌ Restart services

### **Chỉ cần:**
- ✅ Drop JSON files vào folder
- ✅ Wait 5 minutes
- ✅ Refresh Dashboard

---

**ĐÚNG LÀ TỰ ĐỘNG HOÀN TOÀN! 🎉**

**Dữ liệu thật của bạn (32 files) đã sẵn sàng để được scan! 🚀**

