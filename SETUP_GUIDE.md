# 🚀 Hướng Dẫn Setup QUALIFY.AI

## ✅ Đã Hoàn Thành

1. ✅ **Frontend dependencies đã được cài đặt**

## 📋 Yêu Cầu Hệ Thống

Để chạy đầy đủ ứng dụng, bạn cần cài đặt:

### 1. **Docker Desktop** (Khuyến nghị - Dễ nhất)
- Tải về: https://www.docker.com/products/docker-desktop/
- Docker sẽ cung cấp PostgreSQL, Redis, MinIO và các backend services

### 2. **Hoặc cài đặt riêng lẻ:**

#### Python 3.11+
- Tải về: https://www.python.org/downloads/
- Đảm bảo chọn "Add Python to PATH" khi cài đặt

#### PostgreSQL 15+
- Tải về: https://www.postgresql.org/download/windows/
- Hoặc sử dụng Docker

#### Redis
- Tải về: https://github.com/microsoftarchive/redis/releases
- Hoặc sử dụng Docker

## 🎯 Cách Setup (Chọn 1 trong 2)

### **Option 1: Sử dụng Docker (Khuyến nghị)**

#### Bước 1: Cài Docker Desktop
Tải và cài đặt Docker Desktop từ https://www.docker.com/products/docker-desktop/

#### Bước 2: Tạo file .env
Tạo file `infrastructure/docker-compose/.env` với nội dung:

```env
OPENAI_API_KEY=your-openai-api-key-here
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
```

#### Bước 3: Start Backend Services
```powershell
cd infrastructure\docker-compose
docker compose up -d
```

#### Bước 4: Start Frontend
```powershell
cd frontend
npm run dev
```

#### Bước 5: Truy cập
- Frontend: http://localhost:3000
- API Gateway: http://localhost:8000
- MinIO Console: http://localhost:9001 (admin/minioadmin123)

---

### **Option 2: Setup thủ công (Không dùng Docker)**

#### Bước 1: Cài đặt Python và PostgreSQL

#### Bước 2: Setup Backend
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

#### Bước 3: Tạo file .env
Tạo file `.env` trong thư mục `backend`:

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

#### Bước 4: Start Database Services
- Start PostgreSQL
- Start Redis

#### Bước 5: Run Migrations
```powershell
cd backend\shared
alembic upgrade head
```

#### Bước 6: Start Backend Services
Mở 4 terminal windows và chạy:

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

#### Bước 7: Start Frontend
```powershell
cd frontend
npm run dev
```

---

## 🎉 Sau Khi Setup

1. Truy cập http://localhost:3000 để xem dashboard
2. Backend services sẽ chạy trên:
   - Auth: http://localhost:8001
   - Report Aggregator: http://localhost:8002
   - AI Analysis: http://localhost:8003
   - Analytics: http://localhost:8004

## ⚠️ Lưu Ý

- Nếu không có Docker, bạn cần cài đặt Python, PostgreSQL và Redis riêng
- File `.env` cần được tạo với các giá trị phù hợp
- OpenAI API Key là bắt buộc cho các tính năng AI



