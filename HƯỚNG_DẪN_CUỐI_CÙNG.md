# 🎯 HƯỚNG DẪN SỬ DỤNG QUALIFY.AI - PHIÊN BẢN CUỐI CÙNG

## ✅ HIỆN TRẠNG:

- ✅ **Frontend:** Đang chạy tại http://localhost:3000
- ✅ **Data:** 2 ngày (10/11 và 13/11) với 151 tests
- ✅ **Auto-refresh:** Dashboard tự động reload mỗi 1 phút

---

## 📂 NƠI ĐẶT DỮ LIỆU:

```
D:\allure-reports\
├── 10-11-2025\      ← 80 tests (64 passed, 16 failed)
├── 13-11-2025\      ← 71 tests (71 passed, 0 failed)
└── [dd-MM-yyyy]\    ← Thêm folder mới vào đây
```

**Format folder:** `dd-MM-yyyy` (VD: `14-11-2025`, `01-12-2025`)

---

## 🔄 QUY TRÌNH TỰ ĐỘNG:

### **Option 1: AUTO-SCAN (Mỗi 5 phút)**

#### **Start Watcher (Terminal riêng):**

```powershell
cd D:\practice\AI-Allure-Report
.\scripts\auto-watcher.ps1
```

**KHÔNG ĐÓNG terminal này!** Để chạy liên tục.

#### **Workflow:**

```
1. Watcher quét D:\allure-reports\ mỗi 5 phút
   ↓
2. Tìm folders dd-MM-yyyy
   ↓  
3. Parse tất cả *-result.json
   ↓
4. Update trend-data.json & all-results.json
   ↓
5. Dashboard auto-refresh (1 phút)
   ↓
6. Data mới hiển thị!
```

**Thời gian:** Tối đa 6 phút (5 min scan + 1 min refresh)

---

### **Option 2: MANUAL UPDATE (Ngay lập tức)**

#### **Khi thêm data mới:**

```powershell
# Chạy lệnh này:
cd D:\practice\AI-Allure-Report
.\scripts\update-trend-data.ps1

# Rồi refresh browser (F5)
```

**Thời gian:** Vài giây!

---

## 🎬 VÍ DỤ SỬ DỤNG:

### **Scenario: Thêm data ngày 14/11**

#### **Bước 1: Tạo folder**

```powershell
mkdir "D:\allure-reports\14-11-2025"
```

#### **Bước 2: Copy Allure results**

```powershell
# Sau khi chạy Playwright tests
copy "allure-results\*-result.json" "D:\allure-reports\14-11-2025\"
```

#### **Bước 3a: Nếu Watcher đang chạy**

- ⏰ Đợi tối đa 6 phút
- 🔄 Dashboard tự động cập nhật
- ✨ Data 14/11 xuất hiện!

#### **Bước 3b: Hoặc update ngay**

```powershell
.\scripts\update-trend-data.ps1
# Refresh browser (F5)
```

---

## 📊 DASHBOARD SẼ HIỂN THỊ:

### **Biểu đồ Trend:**

```
Tests
  ↑
 80│    ●                    ●
    │  10/11               13/11
 60│   (64)                (71)
    │
 40│
    │
 20│    ● (16 failed)       ● (0 failed)
    │
  0└──────────────────────────────────→
   14/10 ... 10/11 11/11 12/11 13/11
   
   2 điểm data THẬT từ 2 ngày có files
```

### **Overall Health:**

- Pass Rate: **89.4%**
- Total Tests: **151**
- Passed: **135**
- Failed: **16**

---

## 🎯 KIỂM TRA WATCHER ĐANG CHẠY:

### **Xem logs trong terminal:**

```
==================================================
Scanning at 15:50:00
==================================================

Found 2 date folders

Processing 10-11-2025: 80 files
  64 passed, 16 failed
Processing 13-11-2025: 71 files  
  71 passed, 0 failed

==================================================
SUCCESS!
==================================================

Total Tests: 151
Pass Rate: 89.4%

Next scan in 5 minutes...
Waiting...
```

---

## ⚡ LỆNH QUAN TRỌNG:

```powershell
# Start auto-watcher (mỗi 5 phút)
.\scripts\auto-watcher.ps1

# Update manual (ngay lập tức)
.\scripts\update-trend-data.ps1

# View dashboard
http://localhost:3000/dashboard

# Stop watcher
Ctrl + C (trong terminal đang chạy watcher)
```

---

## 🐛 TROUBLESHOOTING:

### **Dashboard không update sau 6 phút?**

Kiểm tra:
1. ✅ Watcher đang chạy? (Xem terminal logs)
2. ✅ Files mới đã add vào folder?
3. ✅ Format folder đúng `dd-MM-yyyy`?
4. ✅ Frontend auto-refresh? (Xem console: `🔄 Auto-refreshing...`)

### **Chạy manual để test ngay:**

```powershell
.\scripts\update-trend-data.ps1
# Refresh browser (F5)
```

---

## 📋 TÓM TẮT:

### **2 Cách sử dụng:**

| Cách | Thời gian | Ưu điểm |
|------|-----------|---------|
| **Auto-watcher** | 6 phút | Tự động, không cần làm gì |
| **Manual script** | Vài giây | Nhanh, kiểm soát được |

### **Khuyến nghị:**

- 🚀 **Development:** Dùng manual script (nhanh)
- 🤖 **Production:** Dùng auto-watcher (tự động)

---

## 🎉 HOÀN TẤT!

**Backend đã sửa xong và hoạt động!**

**Start watcher:**
```powershell
.\scripts\auto-watcher.ps1
```

**Dashboard:**
http://localhost:3000/dashboard

---

**HỆ THỐNG ĐÃ SẴN SÀNG! 🚀**

