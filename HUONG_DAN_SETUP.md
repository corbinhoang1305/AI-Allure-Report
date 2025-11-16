# 🚀 Hướng Dẫn Setup và Chạy QUALIFY.AI

## ✅ Trạng Thái Hiện Tại

- ✅ **Frontend dependencies đã được cài đặt**
- ✅ **Frontend đang chạy trên http://localhost:3000**

## 📋 Yêu Cầu

Để chạy đầy đủ ứng dụng (bao gồm backend), bạn cần:

### Phương án 1: Docker (Khuyến nghị - Dễ nhất)
- **Docker Desktop**: https://www.docker.com/products/docker-desktop/
- Docker sẽ tự động cài đặt PostgreSQL, Redis, MinIO và các backend services

### Phương án 2: Cài đặt thủ công
- **Python 3.11+**: https://www.python.org/downloads/
- **PostgreSQL 15+**: https://www.postgresql.org/download/windows/
- **Redis**: https://github.com/microsoftarchive/redis/releases

## 🎯 Cách Chạy

### Bước 1: Chạy Frontend (Đã sẵn sàng!)

Frontend đã được cài đặt và đang chạy. Bạn có thể:

- Truy cập: **http://localhost:3000**
- Hoặc chạy lại bằng: `start-frontend.bat` (double-click file này)

### Bước 2: Chạy Backend

#### Nếu bạn có Docker:

1. **Chạy file:** `start-backend-docker.bat` (double-click)
   
   Hoặc chạy thủ công:
   ```powershell
   cd infrastructure\docker-compose
   docker compose up -d
   ```

2. **Cấu hình .env:**
   - Mở file `infrastructure\docker-compose\.env`
   - Thêm OpenAI API Key của bạn:
     ```
     OPENAI_API_KEY=sk-your-actual-key-here
     SECRET_KEY=your-secret-key-min-32-chars
     ```

3. **Kiểm tra services:**
   ```powershell
   docker compose ps
   ```

#### Nếu bạn KHÔNG có Docker:

1. **Cài đặt Python, PostgreSQL, Redis** (xem link ở trên)

2. **Setup Backend:**
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Tạo file .env** trong thư mục `backend`:
   ```env
   DATABASE_URL=postgresql+asyncpg://qualify:qualify_password@localhost:5432/qualify_db
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY=your-secret-key-change-in-production-min-32-chars
   OPENAI_API_KEY=your-openai-api-key-here
   MINIO_ENDPOINT=localhost:9000
   MINIO_ACCESS_KEY=minioadmin
   MINIO_SECRET_KEY=minioadmin123
   ALLURE_REPORTS_PATH=D:/allure-reports
   ```

4. **Start Database:**
   - Start PostgreSQL service
   - Start Redis service

5. **Run Migrations:**
   ```powershell
   cd backend\shared
   alembic upgrade head
   ```

6. **Start Backend Services:**
   
   Mở 4 terminal windows và chạy từng service:
   
   ```powershell
   # Terminal 1 - Auth Service
   cd backend\services\auth-service
   uvicorn app.main:app --reload --port 8001
   
   # Terminal 2 - Report Aggregator
   cd backend\services\report-aggregator
   uvicorn app.main:app --reload --port 8002
   
   # Terminal 3 - AI Analysis Service
   cd backend\services\ai-analysis-service
   uvicorn app.main:app --reload --port 8003
   
   # Terminal 4 - Analytics Service
   cd backend\services\analytics-service
   uvicorn app.main:app --reload --port 8004
   ```

## 🌐 Truy Cập Ứng Dụng

Sau khi setup xong:

- **Frontend Dashboard**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **Auth Service API**: http://localhost:8001/docs
- **Report Aggregator API**: http://localhost:8002/docs
- **AI Analysis API**: http://localhost:8003/docs
- **Analytics API**: http://localhost:8004/docs
- **MinIO Console**: http://localhost:9001
  - Username: `minioadmin`
  - Password: `minioadmin123`

## 📝 Files Hữu Ích

- `start-frontend.bat` - Chạy frontend
- `start-backend-docker.bat` - Chạy backend với Docker
- `setup-and-run.ps1` - Script PowerShell để kiểm tra và setup
- `SETUP_GUIDE.md` - Hướng dẫn chi tiết (tiếng Anh)

## ⚠️ Lưu Ý Quan Trọng

1. **OpenAI API Key**: Bắt buộc cho các tính năng AI. Lấy tại: https://platform.openai.com/api-keys

2. **Port Conflicts**: Nếu các port đã được sử dụng, bạn cần:
   - Thay đổi port trong `docker-compose.yml` hoặc
   - Dừng các service đang sử dụng port đó

3. **Database**: Nếu dùng Docker, database sẽ tự động được tạo. Nếu setup thủ công, bạn cần tạo database `qualify_db` trong PostgreSQL.

## 🆘 Troubleshooting

### Frontend không kết nối được backend
- Kiểm tra backend services có đang chạy không
- Kiểm tra `NEXT_PUBLIC_API_BASE_URL` trong `frontend/.env.local` (nếu có)

### Docker services không start
- Kiểm tra Docker Desktop có đang chạy không
- Kiểm tra port conflicts: `netstat -ano | findstr :8000`

### Python errors
- Đảm bảo Python 3.11+ đã được cài đặt
- Đảm bảo virtual environment đã được activate
- Kiểm tra dependencies: `pip list`

## 📞 Hỗ Trợ

Xem thêm tài liệu trong thư mục `docs/`:
- `docs/QUICKSTART.md` - Quick start guide
- `docs/DEVELOPMENT.md` - Development guide
- `docs/API.md` - API documentation

---

**Chúc bạn setup thành công! 🎉**



