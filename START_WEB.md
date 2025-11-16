# 🚀 QUALIFY.AI - Hướng Dẫn Truy Cập Web

## ✅ Trạng Thái: Tất cả services đang chạy!

### 📱 Truy Cập Ứng Dụng

#### 🌐 **Frontend Dashboard** (Giao diện chính)
- **URL:** http://localhost:3000
- **Mô tả:** Giao diện web chính của QUALIFY.AI
- **Tính năng:** Dashboard, Analytics, AI Insights, Test Reports

#### 📚 **API Gateway** (Nginx)
- **URL:** http://localhost:8000
- **Mô tả:** API Gateway tổng hợp tất cả backend services

#### 🔧 **Backend Services** (API Documentation)
- **Auth Service:** http://localhost:8001/docs
- **Report Aggregator:** http://localhost:8002/docs
- **AI Analysis Service:** http://localhost:8003/docs
- **Analytics Service:** http://localhost:8004/docs

#### 🗄️ **MinIO Console** (Storage Management)
- **URL:** http://localhost:9001
- **Username:** minioadmin
- **Password:** minioadmin123

---

## 🎯 Cách Sử Dụng

### 1. Truy cập Dashboard
Mở trình duyệt và vào: **http://localhost:3000**

### 2. Xem Test Reports
Dashboard sẽ hiển thị:
- Tổng quan về test results
- Failed tests list
- Quality metrics
- Trend charts
- AI insights

### 3. Upload Allure Reports
Đặt Allure reports vào thư mục: `D:\allure-reports\`

Report Aggregator service sẽ tự động:
- Quét thư mục mỗi 2 phút
- Parse và lưu test results vào database
- Cập nhật dashboard

---

## 🛠️ Quản Lý Services

### Xem logs của một service cụ thể:
```powershell
cd infrastructure\docker-compose
docker compose logs -f [service-name]
```

Ví dụ:
```powershell
# Xem logs của Report Aggregator
docker compose logs -f report-aggregator

# Xem logs của AI Analysis Service
docker compose logs -f ai-analysis

# Xem logs tất cả services
docker compose logs -f
```

### Dừng tất cả services:
```powershell
cd infrastructure\docker-compose
docker compose down
```

### Khởi động lại tất cả services:
```powershell
cd infrastructure\docker-compose
docker compose up -d
```

### Dừng frontend:
Đóng cửa sổ cmd đang chạy frontend hoặc nhấn `Ctrl+C`

### Khởi động lại frontend:
```powershell
.\start-frontend.bat
```

---

## 📊 Database Access

### PostgreSQL
- **Host:** localhost
- **Port:** 5432
- **Database:** qualify_db
- **Username:** qualify
- **Password:** qualify_password

Kết nối bằng công cụ như pgAdmin, DBeaver, hoặc psql:
```bash
psql -h localhost -p 5432 -U qualify -d qualify_db
```

### Redis
- **Host:** localhost
- **Port:** 6379
- **Database:** 0

---

## 🔍 Kiểm Tra Trạng Thái Services

Chạy lệnh này để kiểm tra:
```powershell
cd infrastructure\docker-compose
docker compose ps
```

Tất cả services nên có trạng thái "Up"

---

## ⚠️ Khắc Phục Sự Cố

### Frontend không load được?
1. Kiểm tra port 3000 có bị chiếm:
   ```powershell
   Get-NetTCPConnection -LocalPort 3000
   ```
2. Restart frontend:
   ```powershell
   .\start-frontend.bat
   ```

### Backend service bị lỗi?
1. Xem logs:
   ```powershell
   cd infrastructure\docker-compose
   docker compose logs [service-name]
   ```
2. Restart service cụ thể:
   ```powershell
   docker compose restart [service-name]
   ```

### Database connection error?
1. Kiểm tra PostgreSQL container:
   ```powershell
   docker compose ps postgres
   ```
2. Restart PostgreSQL:
   ```powershell
   docker compose restart postgres
   ```

---

## 📝 Cấu Hình

### File .env
Vị trí: `infrastructure/docker-compose/.env`

Các biến quan trọng:
- `OPENAI_API_KEY`: API key cho tính năng AI (tùy chọn)
- `SECRET_KEY`: Secret key cho JWT authentication

### Allure Reports Path
Mặc định: `D:\allure-reports\`

Để thay đổi, sửa trong `docker-compose.yml`:
```yaml
report-aggregator:
  volumes:
    - D:/allure-reports:/app/allure-reports:ro
```

Sau đó restart:
```powershell
docker compose down
docker compose up -d
```

---

## 🎉 Bạn Đã Sẵn Sàng!

**Truy cập ngay:** http://localhost:3000

Chúc bạn sử dụng QUALIFY.AI hiệu quả! 🚀


