# 🔄 HƯỚNG DẪN AUTO-UPDATE DATA

## ⚠️ HIỆN TRẠNG:

**Report Watcher Service (quét tự động mỗi 5 phút) CHƯA CHẠY!**

Hiện tại đang dùng **cách thủ công** - phải chạy script để update.

---

## 🎯 CÓ 2 CÁCH:

### **CÁCH 1: Thủ công (Đang dùng - Đơn giản)**

#### **Khi thêm data mới:**

1. Đặt JSON files vào folder:
```
D:\allure-reports\10-11-2025\  ← Ví dụ bạn vừa thêm
```

2. Chạy script update:
```powershell
cd D:\practice\AI-Allure-Report
.\scripts\update-trend-data.ps1
```

3. Refresh Dashboard (F5)

**Ưu điểm:** ✅ Đơn giản, không cần backend  
**Nhược điểm:** ❌ Phải chạy script mỗi lần có data mới

---

### **CÁCH 2: Tự động (Auto-scan mỗi 5 phút)**

#### **Setup:**

**Bước 1: Start Database**
```powershell
cd D:\practice\AI-Allure-Report\infrastructure\docker-compose
docker-compose up -d postgres redis
```

**Bước 2: Start Report Watcher**
```powershell
cd D:\practice\AI-Allure-Report
.\scripts\start-watcher.bat
```

**Bước 3: Update Frontend để load từ API**

Sửa `frontend/app/dashboard/page.tsx`:
```typescript
// Thay vì load từ file, gọi API:
const response = await fetch('http://localhost:8004/dashboard');
const data = await response.json();
```

#### **Sau đó:**

1. Đặt JSON files vào `D:\allure-reports\[dd-MM-yyyy]\`
2. **Đợi 5 phút** (hoặc trigger manual scan)
3. Dashboard **TỰ ĐỘNG** refresh và hiển thị!

**Ưu điểm:** ✅ Hoàn toàn tự động, không cần làm gì  
**Nhược điểm:** ❌ Cần setup Docker, backend services

---

## 📊 DATA HIỆN TẠI CỦA BẠN:

```
D:\allure-reports\
├── 10-11-2025\     → 80 files (64 passed, 16 failed)
└── 13-11-2025\     → 71 files (71 passed, 0 failed)

TOTAL: 151 tests
Pass Rate: 89.4%
```

**Đã update vào:**
```
frontend/public/real-data/
├── all-results.json      → 151 tests total
└── trend-data.json       → 2 ngày: 10/11 và 13/11
```

---

## 🎨 BIỂU ĐỒ BÂY GIỜ:

```
Tests
  ↑
 80│    ●                          ●
    │   (64)                      (71)
 60│
    │
 40│
    │
 20│
    │
  0└────────────────────────────────────→
   14/10  ...  10/11  ...  13/11
   
   2 điểm data: 10/11 và 13/11
```

---

## 🔄 QUY TRÌNH HIỆN TẠI (Thủ công):

```
1. Thêm data mới vào folder
   D:\allure-reports\10-11-2025\

2. Chạy script
   .\scripts\update-trend-data.ps1

3. Script sẽ:
   ✓ Quét TẤT CẢ folders dd-MM-yyyy
   ✓ Parse JSON files
   ✓ Tạo trend-data.json
   ✓ Dashboard load file này

4. Refresh browser (F5)
```

**Thời gian:** Vài giây (không phải 5 phút!)

---

## ⚡ ĐỂ UPDATE NGAY LẬP TỨC:

```powershell
# Mỗi khi thêm data mới, chỉ cần:
cd D:\practice\AI-Allure-Report
.\scripts\update-trend-data.ps1

# Rồi refresh browser (F5)
# KHÔNG CẦN ĐỢI 5 phút!
```

---

## 🤖 NẾU MUỐN AUTO-SCAN (5 phút):

### **Cần setup backend đầy đủ:**

1. **Start Database:**
```powershell
cd infrastructure/docker-compose
docker-compose up -d postgres redis
```

2. **Start Report Watcher:**
```powershell
cd backend/services/report-watcher
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8005
```

3. **Config:**
Tạo file `backend/services/report-watcher/.env`:
```env
ALLURE_REPORTS_PATH=D:/allure-reports
SCAN_INTERVAL_MINUTES=5
DATABASE_URL=postgresql+asyncpg://qualify:qualify_password@localhost:5432/qualify_db
```

**Sau đó:** Watcher sẽ tự động quét mỗi 5 phút!

---

## 📋 TÓM TẮT:

### **Hiện tại (Cách thủ công):**
- ✅ Thêm data → Chạy script → Refresh
- ✅ Nhanh (vài giây)
- ✅ Không cần backend

### **Nếu dùng Auto-scan:**
- ✅ Thêm data → Đợi 5 phút → Tự động update
- ❌ Cần backend + database

---

## 🚀 KHUYẾN NGHỊ:

**Để test nhanh:** Dùng cách thủ công (chạy script)

**Khi deploy production:** Setup auto-scan với backend

---

## ✨ UPDATE NGAY DATA 10/11:

```powershell
cd D:\practice\AI-Allure-Report
.\scripts\update-trend-data.ps1
```

**Rồi refresh:** http://localhost:3000/dashboard **(F5)**

**Bạn sẽ thấy:**
- ✅ 2 điểm trên chart: 10/11 và 13/11
- ✅ Pass rate: 89.4%
- ✅ Total: 151 tests

---

**CHẠY SCRIPT NGAY ĐỂ CẬP NHẬT! 🚀**

