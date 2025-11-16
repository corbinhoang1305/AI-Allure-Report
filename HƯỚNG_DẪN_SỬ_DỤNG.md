# 🎉 QUALIFY.AI - Đã Setup Thành Công!

## ✅ Trạng Thái Hiện Tại

**TẤT CẢ SERVICES ĐANG CHẠY!** 🚀

### 📋 Danh Sách Services

| Service | Trạng Thái | Port | URL |
|---------|-----------|------|-----|
| **Frontend Dashboard** | ✅ Running | 3000 | http://localhost:3000 |
| **API Gateway** | ✅ Running | 8000 | http://localhost:8000 |
| **Auth Service** | ✅ Running | 8001 | http://localhost:8001/docs |
| **Report Aggregator** | ✅ Running | 8002 | http://localhost:8002/docs |
| **AI Analysis** | ✅ Running | 8003 | http://localhost:8003/docs |
| **Analytics Service** | ✅ Running | 8004 | http://localhost:8004/docs |
| **MinIO Console** | ✅ Running | 9001 | http://localhost:9001 |
| **PostgreSQL** | ✅ Running | 5432 | localhost:5432 |
| **Redis** | ✅ Running | 6379 | localhost:6379 |

---

## 🌐 Truy Cập Web

### 🎯 Dashboard Chính
**URL:** **http://localhost:3000**

Giao diện này hiển thị:
- 📊 Tổng quan test results
- 📈 Biểu đồ xu hướng (trends)
- ❌ Danh sách failed tests
- 🎯 Quality health metrics
- 🤖 AI insights và root cause analysis
- 📋 Recent test runs

### 📚 API Documentation
Các backend services đều có Swagger UI documentation:
- **Auth API:** http://localhost:8001/docs
- **Report Aggregator API:** http://localhost:8002/docs
- **AI Analysis API:** http://localhost:8003/docs
- **Analytics API:** http://localhost:8004/docs

### 🗄️ MinIO Storage Console
- **URL:** http://localhost:9001
- **Username:** `minioadmin`
- **Password:** `minioadmin123`

---

## 📤 Upload Allure Reports

### Cách 1: Tự động (Khuyến nghị)

Report Aggregator service sẽ tự động quét và import reports:

1. **Đặt Allure reports vào thư mục:**
   ```
   D:\allure-reports\
   ```

2. **Cấu trúc thư mục:**
   ```
   D:\allure-reports\
   ├── project-1\
   │   ├── build-123\
   │   │   └── allure-results\
   │   │       ├── xxx-result.json
   │   │       ├── yyy-result.json
   │   │       └── ...
   │   └── build-124\
   │       └── allure-results\
   └── project-2\
       └── build-456\
           └── allure-results\
   ```

3. **Service sẽ tự động:**
   - Quét thư mục mỗi 2 phút
   - Parse tất cả test results
   - Lưu vào database
   - Cập nhật dashboard

### Cách 2: Manual Upload qua API

```bash
curl -X POST http://localhost:8002/api/reports/upload \
  -F "file=@path/to/allure-report.zip"
```

---

## 🎮 Các Lệnh Quan Trọng

### ✅ Kiểm Tra Trạng Thái
```powershell
.\show-status.ps1
```

### 🔄 Quản Lý Backend (Docker)

#### Xem logs:
```powershell
cd infrastructure\docker-compose

# Xem logs tất cả services
docker compose logs -f

# Xem logs một service cụ thể
docker compose logs -f report-aggregator
docker compose logs -f ai-analysis
```

#### Restart services:
```powershell
cd infrastructure\docker-compose

# Restart tất cả
docker compose restart

# Restart một service
docker compose restart report-aggregator
```

#### Dừng services:
```powershell
cd infrastructure\docker-compose
docker compose down
```

#### Start lại services:
```powershell
cd infrastructure\docker-compose
docker compose up -d
```

### 🖥️ Quản Lý Frontend

#### Dừng frontend:
- Đóng cửa sổ cmd đang chạy
- Hoặc nhấn `Ctrl+C` trong terminal

#### Start frontend:
```powershell
.\start-frontend.bat
```

---

## 🛠️ Scripts Hữu Ích

### 1. `show-status.ps1`
Kiểm tra trạng thái tất cả services

```powershell
.\show-status.ps1
```

### 2. `start-frontend.bat`
Khởi động frontend development server

```powershell
.\start-frontend.bat
```

### 3. `start-backend-docker.bat`
Khởi động tất cả backend services

```powershell
.\start-backend-docker.bat
```

---

## 💡 Sử Dụng Dashboard

### 1. Xem Tổng Quan
- Mở http://localhost:3000
- Dashboard hiển thị tổng quan về:
  - Total tests
  - Pass/Fail/Skip counts
  - Pass rate percentage
  - Quality health score

### 2. Phân Tích Failed Tests
- Click vào "Failed Tests" section
- Xem chi tiết lỗi, stack trace
- Xem history của test
- AI sẽ tự động phân tích root cause

### 3. Xem Trends
- Biểu đồ hiển thị xu hướng theo thời gian
- So sánh giữa các builds
- Nhận diện patterns

### 4. AI Insights
- Root Cause Analysis tự động
- Flaky test detection
- Recommendations để cải thiện

---

## 📊 Database Access

### PostgreSQL
```bash
Host: localhost
Port: 5432
Database: qualify_db
Username: qualify
Password: qualify_password
```

Kết nối bằng psql:
```bash
psql -h localhost -p 5432 -U qualify -d qualify_db
```

Hoặc dùng GUI tools như:
- pgAdmin
- DBeaver
- DataGrip

### Redis
```bash
Host: localhost
Port: 6379
Database: 0
```

Kết nối bằng redis-cli:
```bash
redis-cli -h localhost -p 6379
```

---

## ⚠️ Khắc Phục Sự Cố

### ❌ Frontend không load?

**Nguyên nhân:** Port 3000 bị chiếm hoặc service chưa start

**Giải pháp:**
```powershell
# Kiểm tra port
Get-NetTCPConnection -LocalPort 3000

# Kill process nếu bị chiếm
Stop-Process -Id <PID> -Force

# Start lại frontend
.\start-frontend.bat
```

### ❌ Backend service lỗi?

**Nguyên nhân:** Container bị crash hoặc configuration sai

**Giải pháp:**
```powershell
cd infrastructure\docker-compose

# Xem logs để tìm lỗi
docker compose logs report-aggregator

# Restart service
docker compose restart report-aggregator

# Hoặc rebuild nếu cần
docker compose up -d --build report-aggregator
```

### ❌ Database connection error?

**Nguyên nhân:** PostgreSQL chưa sẵn sàng

**Giải pháp:**
```powershell
cd infrastructure\docker-compose

# Kiểm tra PostgreSQL
docker compose ps postgres

# Xem logs
docker compose logs postgres

# Restart
docker compose restart postgres
```

### ❌ Reports không được import tự động?

**Nguyên nhân:** 
- Đường dẫn không đúng
- Format file không hợp lệ
- Service chưa chạy

**Giải pháp:**
1. Kiểm tra thư mục: `D:\allure-reports\`
2. Đảm bảo có file `*-result.json`
3. Xem logs của report-aggregator:
   ```powershell
   cd infrastructure\docker-compose
   docker compose logs -f report-aggregator
   ```

---

## 🔐 Bảo Mật

### ⚠️ Lưu Ý Quan Trọng

1. **Secret Key**: 
   - File: `infrastructure/docker-compose/.env`
   - PHẢI thay đổi trong production!
   - Current: `your-secret-key-change-in-production-qualify-ai-2024-min-32-chars`

2. **MinIO Credentials**:
   - Username: `minioadmin`
   - Password: `minioadmin123`
   - PHẢI thay đổi trong production!

3. **Database Password**:
   - Current: `qualify_password`
   - PHẢI thay đổi trong production!

### 🔒 Để Production-Ready

Sửa file `infrastructure/docker-compose/.env`:
```env
OPENAI_API_KEY=sk-your-real-openai-key
SECRET_KEY=generate-a-strong-random-key-at-least-32-characters-long
```

Sửa `docker-compose.yml` để thay đổi passwords.

---

## 🎯 Next Steps

### 1. Thêm OpenAI API Key (Tùy chọn)

Nếu muốn dùng tính năng AI:

1. Lấy API key từ: https://platform.openai.com/api-keys
2. Thêm vào file `.env`:
   ```env
   OPENAI_API_KEY=sk-your-api-key-here
   ```
3. Restart services:
   ```powershell
   cd infrastructure\docker-compose
   docker compose restart
   ```

### 2. Import Test Data

- Copy Allure reports vào `D:\allure-reports\`
- Đợi 2 phút để service tự động import
- Refresh dashboard

### 3. Khám Phá Tính Năng

- ✅ View test results
- ✅ Analyze failure trends
- ✅ Get AI-powered insights
- ✅ Track quality metrics
- ✅ Export reports

---

## 📚 Tài Liệu Thêm

- **README.md**: Tổng quan về project
- **START_WEB.md**: Hướng dẫn chi tiết
- **docs/**: Thư mục documentation đầy đủ

---

## 🆘 Cần Giúp Đỡ?

### Kiểm tra logs:
```powershell
# Backend
cd infrastructure\docker-compose
docker compose logs -f

# Frontend
# Xem trong cửa sổ cmd đang chạy frontend
```

### Restart tất cả:
```powershell
# Stop all
cd infrastructure\docker-compose
docker compose down

# Start all
docker compose up -d

# Start frontend
.\start-frontend.bat
```

---

## ✅ Checklist Hoàn Thành

- [x] Docker Desktop đã cài đặt
- [x] Backend services đang chạy (Docker)
- [x] Frontend đang chạy (port 3000)
- [x] Database (PostgreSQL) đã sẵn sàng
- [x] Cache (Redis) đã sẵn sàng
- [x] Storage (MinIO) đã sẵn sàng
- [x] Có thể truy cập dashboard: http://localhost:3000

---

## 🎉 Chúc Mừng!

Bạn đã setup thành công **QUALIFY.AI**!

**Truy cập ngay:** 🌐 **http://localhost:3000**

Chúc bạn sử dụng hiệu quả! 🚀

---

**Built with ❤️ for Quality Engineering Teams**


