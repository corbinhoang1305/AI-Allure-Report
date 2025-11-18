# Hướng dẫn kích hoạt chức năng AI-Chat

## Vấn đề
Chức năng Natural Language Query (AI-Chat) không hoạt động vì backend services chưa được khởi động.

## Giải pháp

### Bước 1: Tạo file .env cho Docker Compose

Tạo file `infrastructure/docker-compose/.env` với nội dung sau:

```bash
# OpenAI API Key - Required for AI features
OPENAI_API_KEY=your-openai-api-key-here
```

**Lưu ý:** Thay `your-openai-api-key-here` bằng OpenAI API key thực của bạn (bắt đầu bằng `sk-proj-...`)

### Bước 2: Khởi động Backend Services

```powershell
# Di chuyển vào thư mục docker-compose
cd infrastructure/docker-compose

# Khởi động tất cả services
docker-compose up -d

# Hoặc chỉ khởi động AI analysis service và dependencies
docker-compose up -d postgres redis ai-analysis nginx
```

### Bước 3: Kiểm tra Services đã chạy

```powershell
# Xem danh sách containers đang chạy
docker ps

# Kiểm tra logs của AI service
docker logs qualify-ai

# Kiểm tra logs của nginx gateway
docker logs qualify-nginx
```

### Bước 4: Test API

```powershell
# Test health check
curl http://localhost:8000/api/ai/health

# Test NL query trực tiếp (sau khi có API key)
curl -X POST http://localhost:8000/api/ai/query/nl `
  -H "Content-Type: application/json" `
  -d '{"query": "How many tests failed today?"}'
```

## Cấu trúc Backend

Backend được tổ chức thành các microservices:

1. **postgres** (port 5432) - Database
2. **redis** (port 6379) - Cache và message queue
3. **minio** (port 9000, 9001) - Object storage
4. **auth-service** (port 8001) - Authentication
5. **report-aggregator** (port 8002) - Thu thập và xử lý reports
6. **ai-analysis** (port 8003) - AI features including NL Query ⭐
7. **analytics** (port 8004) - Analytics và metrics
8. **report-watcher** (port 8005) - Auto-scan Allure reports
9. **nginx** (port 8000) - API Gateway ⭐

## API Endpoints

Frontend gọi đến Nginx gateway tại `http://localhost:8000`, sau đó Nginx route đến service phù hợp:

- `/api/ai/query/nl` → ai-analysis service (port 8003)
- `/api/analytics/*` → analytics service (port 8004)
- `/api/auth/*` → auth-service (port 8001)
- `/api/reports/*` → report-aggregator (port 8002)

## Troubleshooting

### Vấn đề 1: Không có OpenAI API Key

**Triệu chứng:** AI service báo lỗi về API key

**Giải pháp:**
1. Đăng ký OpenAI account tại https://platform.openai.com
2. Tạo API key mới
3. Thêm vào file `.env`
4. Restart services: `docker-compose restart ai-analysis`

### Vấn đề 2: Port đã được sử dụng

**Triệu chứng:** Docker báo lỗi port conflict

**Giải pháp:**
```powershell
# Kiểm tra port nào đang được dùng
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Dừng process hoặc đổi port trong docker-compose.yml
```

### Vấn đề 3: Frontend không kết nối được backend

**Triệu chứng:** Console browser báo CORS error hoặc connection refused

**Kiểm tra:**
1. Backend có đang chạy không: `docker ps`
2. Nginx có đang chạy không: `curl http://localhost:8000/health`
3. NEXT_PUBLIC_API_BASE_URL có đúng không (mặc định: http://localhost:8000)

**Giải pháp:**
```powershell
# Restart nginx
docker-compose restart nginx

# Kiểm tra logs
docker logs qualify-nginx
```

## Development Mode

Nếu muốn chạy chỉ một số services để phát triển:

```powershell
# Chỉ chạy database và redis
docker-compose up -d postgres redis

# Chạy AI service locally (cần Python 3.11+)
cd backend/services/ai-analysis-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8003
```

## Kiểm tra AI-Chat hoạt động

1. Mở browser tại http://localhost:3000
2. Vào Dashboard
3. Tìm panel "Natural Language Query (AI-Chat)"
4. Nhập câu hỏi, ví dụ: "How many tests failed in the last 7 days?"
5. Click "AI-Chat" hoặc nhấn Enter
6. Đợi response từ AI

## Tính năng AI khác

Ngoài Natural Language Query, backend còn hỗ trợ:

- **Root Cause Analysis (RCA):** Phân tích nguyên nhân test fail
- **Flaky Test Detection:** Phát hiện tests không ổn định
- **Test Optimization:** Đề xuất cải thiện test

Tất cả đều cần OpenAI API key và AI analysis service phải chạy.

