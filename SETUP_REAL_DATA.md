# 🚀 Setup QUALIFY.AI với Dữ liệu Thật

## ✅ Những gì đã sẵn sàng:

1. ✅ **Folder Allure Reports:** `D:\allure-reports\13-11-2025\`
2. ✅ **32 JSON files** từ Allure Report thật
3. ✅ **Report Watcher Service** đã được tạo
4. ✅ **Frontend** đang chạy trên http://localhost:3000

---

## 📍 Cấu trúc Folder hiện tại:

```
D:\allure-reports\
└── 13-11-2025\              # Format: dd-MM-yyyy
    ├── 0074fdf0-...-result.json
    ├── 0114d006-...-result.json
    └── ... (32 files total)
```

---

## 🎯 Cách sử dụng dữ liệu:

### **Option 1: Chạy Report Watcher Service (Tự động quét mỗi 5 phút)**

#### Bước 1: Cài đặt Python dependencies

```powershell
cd D:\practice\AI-Allure-Report\backend\services\report-watcher
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

#### Bước 2: Cấu hình (Tạo file .env)

Tạo file `backend/services/report-watcher/.env`:

```env
ALLURE_REPORTS_PATH=D:/allure-reports
SCAN_INTERVAL_MINUTES=5
DATABASE_URL=postgresql+asyncpg://qualify:qualify_password@localhost:5432/qualify_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
```

#### Bước 3: Start PostgreSQL

```powershell
cd D:\practice\AI-Allure-Report\infrastructure\docker-compose
docker-compose up -d postgres redis
```

#### Bước 4: Run Watcher Service

```powershell
cd D:\practice\AI-Allure-Report\backend\services\report-watcher
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8005
```

Service sẽ:
- ✅ Scan `D:\allure-reports` ngay lập tức
- ✅ Tìm folder `13-11-2025`
- ✅ Parse 32 JSON files
- ✅ Lưu vào database
- ✅ Tự động scan lại mỗi 5 phút

---

### **Option 2: Load trực tiếp vào Frontend (Không cần Backend)**

#### Bước 1: Copy data vào public folder

```powershell
# Copy tất cả files vào frontend
Copy-Item "D:\allure-reports\13-11-2025\*.json" "D:\practice\AI-Allure-Report\frontend\public\sample-data\"
```

#### Bước 2: Update Dashboard để load từ public

File: `frontend/app/dashboard/page.tsx`

Thay đổi useEffect:

```typescript
useEffect(() => {
  async function loadRealAllureData() {
    setLoading(true);
    
    // Load all JSON files từ public folder
    const files = [
      '/sample-data/0074fdf0-950f-47b0-84e0-6f60c11e6754-result.json',
      '/sample-data/0114d006-9ae9-4768-8751-9eb3862a8b11-result.json',
      // ... add more files
    ];
    
    const results = [];
    for (const file of files) {
      try {
        const res = await fetch(file);
        const data = await res.json();
        results.push(data);
      } catch (e) {
        console.error(`Error loading ${file}:`, e);
      }
    }
    
    // Aggregate data
    const { aggregateAllureResults } = await import('@/lib/allure-parser');
    const dashboardData = aggregateAllureResults(results);
    setDashboardData(dashboardData);
    setLoading(false);
  }
  
  loadRealAllureData();
}, []);
```

---

## 🎬 Khuyến nghị: Sử dụng Report Watcher (Option 1)

**Ưu điểm:**
- ✅ Tự động quét và import
- ✅ Không cần copy files thủ công
- ✅ Hỗ trợ multiple date folders
- ✅ Lưu lịch sử vào database
- ✅ Có thể query và analyze

**Cách hoạt động:**

```
📂 D:\allure-reports\
   ├── 13-11-2025\  ← Watcher quét folder này
   │   └── *.json   ← Parse tất cả JSON
   │
   ├── 14-11-2025\  ← Ngày mai tự động quét
   │   └── *.json
   │
   └── 15-11-2025\  ← Tiếp tục tự động...
       └── *.json

        ↓ (mỗi 5 phút)

   PostgreSQL Database
        ↓
   
   Frontend Dashboard (real-time data)
```

---

## 🔧 Commands Hữu ích:

```powershell
# Kiểm tra Watcher status
curl http://localhost:8005/scan/status

# Trigger scan thủ công
curl -X POST http://localhost:8005/scan/trigger

# Xem files đã process
curl http://localhost:8005/scan/processed

# Reset để scan lại
curl -X DELETE http://localhost:8005/scan/reset
```

---

## 📊 Kết quả mong đợi:

Sau khi setup xong, Dashboard sẽ hiển thị:

- ✅ **Pass Rate** tính từ 32 test results thật
- ✅ **Historical Trends** theo thời gian
- ✅ **Projects/Suites** từ labels trong JSON
- ✅ **Failed Tests** chi tiết
- ✅ **AI Analysis** có thể chạy trên failures thật

---

## ⚡ Quick Start (Nhanh nhất):

```powershell
# 1. Start Database
cd D:\practice\AI-Allure-Report\infrastructure\docker-compose
docker-compose up -d postgres redis

# 2. Start Watcher (terminal mới)
cd D:\practice\AI-Allure-Report
.\scripts\start-watcher.bat

# 3. Frontend đã chạy rồi tại http://localhost:3000
# Refresh page để xem data!
```

---

## 📂 Tóm tắt:

**Bạn đặt dữ liệu JSON vào đây:**

```
D:\allure-reports\
└── [dd-mm-yyyy]\        # VD: 13-11-2025, 14-11-2025
    └── *.json          # Tất cả Allure result JSON files
```

**Watcher Service sẽ:**
- 🔍 Tự động quét folder mỗi 5 phút
- 📊 Parse tất cả JSON files
- 💾 Lưu vào database
- 🔄 Frontend auto-refresh và hiển thị

---

**Dữ liệu thật của bạn đã sẵn sàng! 🎉**

