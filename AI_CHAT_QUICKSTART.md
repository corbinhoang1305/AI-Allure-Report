# AI-Chat Quick Start 🚀

## Vấn đề
Chức năng **Natural Language Query (AI-Chat)** trên Dashboard không hoạt động vì backend chưa được khởi động.

## Giải pháp nhanh

### Option 1: Dùng script tự động (Khuyến nghị) ⭐

```powershell
# Chạy script setup
.\scripts\setup-ai-chat.ps1
```

Script sẽ:
- ✅ Kiểm tra Docker
- ✅ Yêu cầu nhập OpenAI API key (nếu chưa có)
- ✅ Tạo file .env
- ✅ Khởi động tất cả backend services
- ✅ Kiểm tra services đã sẵn sàng

### Option 2: Setup thủ công

#### 1. Tạo file `.env`

```powershell
# Tạo file infrastructure/docker-compose/.env
@"
OPENAI_API_KEY=sk-proj-your-actual-key-here
"@ | Out-File -FilePath infrastructure\docker-compose\.env -Encoding utf8
```

**Lấy OpenAI API key:** https://platform.openai.com/api-keys

#### 2. Khởi động services

```powershell
cd infrastructure\docker-compose
docker-compose up -d
```

#### 3. Kiểm tra

```powershell
# Xem services đang chạy
docker ps

# Test API
curl http://localhost:8000/api/ai/health
```

## Sử dụng AI-Chat

1. Mở browser: **http://localhost:3000**
2. Vào **Dashboard**
3. Tìm panel "**Natural Language Query (AI-Chat)**"
4. Nhập câu hỏi, ví dụ:
   - "How many tests failed today?"
   - "Show me flaky tests in the last week"
   - "What is the pass rate for Gocoin project?"
5. Click **AI-Chat** hoặc nhấn **Enter**

## Services cần thiết

| Service | Port | Mô tả |
|---------|------|-------|
| postgres | 5432 | Database |
| redis | 6379 | Cache |
| **ai-analysis** | 8003 | **AI features (bắt buộc)** |
| **nginx** | 8000 | **API Gateway (bắt buộc)** |
| analytics | 8004 | Analytics |
| report-aggregator | 8002 | Report processing |

## Troubleshooting

### ❌ Lỗi: "Sorry, I could not process your question"

**Nguyên nhân:**
- Backend chưa chạy
- OpenAI API key không hợp lệ
- Hết quota OpenAI

**Giải pháp:**
```powershell
# Kiểm tra logs
docker logs qualify-ai

# Restart AI service
docker-compose restart ai-analysis
```

### ❌ Lỗi: Connection refused / Network error

**Nguyên nhân:** Nginx gateway chưa chạy

**Giải pháp:**
```powershell
# Kiểm tra nginx
docker ps | findstr nginx

# Restart nginx
docker-compose restart nginx
```

### ❌ Lỗi: API key not configured

**Giải pháp:**
1. Kiểm tra file `.env` có tồn tại: `Test-Path infrastructure\docker-compose\.env`
2. Kiểm tra API key trong file: `Get-Content infrastructure\docker-compose\.env`
3. Restart service: `docker-compose restart ai-analysis`

## Tính năng AI khác

Backend còn hỗ trợ các tính năng AI khác (cần OpenAI API key):

- 🔍 **Root Cause Analysis (RCA)** - Phân tích nguyên nhân test fail
- 🎲 **Flaky Test Detection** - Phát hiện tests không ổn định  
- ⚡ **Test Optimization** - Đề xuất cải thiện tests

## Commands hữu ích

```powershell
# Xem logs realtime
docker-compose logs -f ai-analysis

# Stop tất cả services
docker-compose down

# Restart một service cụ thể
docker-compose restart ai-analysis

# Xem resource usage
docker stats

# Rebuild service sau khi đổi code
docker-compose up -d --build ai-analysis
```

## Cần hỗ trợ?

📖 Xem chi tiết: [SETUP_AI_CHAT.md](./SETUP_AI_CHAT.md)

---

**Note:** Frontend đã được cập nhật với đầy đủ chức năng AI-Chat. Bạn chỉ cần khởi động backend services là có thể sử dụng ngay! ✨

