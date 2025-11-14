# Hướng dẫn Auto-Scan Allure Reports

## 🎯 Tổng quan

Report Watcher Service tự động quét folder chứa Allure reports và import data vào database mỗi 5 phút.

## 📁 Cấu trúc Folder

```
D:\allure-reports\              # Base folder
├── 13-11-2025\                 # Date folder (dd-mm-yyyy)
│   ├── result-001.json         # Allure result files
│   ├── result-002.json
│   └── result-003.json
├── 14-11-2025\
│   ├── result-001.json
│   └── result-002.json
└── 15-11-2025\
    └── result-001.json
```

**Quy tắc:**
- Folder tên theo format: `dd-mm-yyyy` (VD: `13-11-2025`, `01-12-2025`)
- File JSON đặt trực tiếp trong folder ngày
- File JSON có format Allure standard

## 🚀 Cách sử dụng

### Bước 1: Tạo folder structure

#### Option A: Tự động (dùng script)

```bash
# Tạo sample reports
scripts\create-sample-reports.bat
```

Script sẽ tạo:
- Folder `D:\allure-reports\`
- Subfolder với tên ngày hôm nay
- Sample JSON file

#### Option B: Thủ công

```bash
# Tạo folder
mkdir D:\allure-reports
mkdir D:\allure-reports\13-11-2025

# Copy Allure JSON files vào
copy path\to\allure-results\*.json D:\allure-reports\13-11-2025\
```

### Bước 2: Cấu hình

Tạo file `.env` trong `backend/services/report-watcher/`:

```env
# Path to reports folder
ALLURE_REPORTS_PATH=D:/allure-reports

# Scan interval (minutes)
SCAN_INTERVAL_MINUTES=5

# Database
DATABASE_URL=postgresql+asyncpg://qualify:qualify_password@localhost:5432/qualify_db
REDIS_URL=redis://localhost:6379/0
```

### Bước 3: Start Service

#### Option A: Standalone (Development)

```bash
# Windows
scripts\start-watcher.bat

# Linux/Mac
cd backend/services/report-watcher
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8005
```

#### Option B: Docker (Production)

Update `docker-compose.yml`:

```yaml
services:
  report-watcher:
    build:
      context: ../../
      dockerfile: backend/services/report-watcher/Dockerfile
    container_name: qualify-watcher
    environment:
      ALLURE_REPORTS_PATH: /reports
      SCAN_INTERVAL_MINUTES: 5
      DATABASE_URL: postgresql+asyncpg://qualify:qualify_password@postgres:5432/qualify_db
    volumes:
      - D:/allure-reports:/reports
    ports:
      - "8005:8005"
    depends_on:
      - postgres
    restart: unless-stopped
```

```bash
docker-compose up -d report-watcher
```

### Bước 4: Verify

Kiểm tra service đang chạy:

```bash
# Health check
curl http://localhost:8005/health

# Xem status
curl http://localhost:8005/scan/status

# Xem files đã process
curl http://localhost:8005/scan/processed
```

## 🔄 Workflow

```
┌─────────────────────────────────────────────────┐
│  1. Service starts                              │
│     - Initial scan immediately                  │
│     - Schedule recurring scans (every 5 min)    │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│  2. Scan folder structure                       │
│     - Look for folders: dd-mm-yyyy              │
│     - Find *.json files in each folder          │
│     - Skip already processed files              │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│  3. Load & Parse JSON                           │
│     - Read Allure JSON format                   │
│     - Extract test results                      │
│     - Calculate statistics                      │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│  4. Save to Database                            │
│     - Create/Get Project                        │
│     - Create/Get Test Suite                     │
│     - Create Test Run                           │
│     - Save Test Results                         │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│  5. Frontend Auto-Refresh                       │
│     - Dashboard loads data from DB              │
│     - Shows latest test results                 │
│     - Updates automatically                     │
└─────────────────────────────────────────────────┘
```

## 📊 Dashboard Integration

### Frontend tự động load data

Update `frontend/app/dashboard/page.tsx`:

```typescript
useEffect(() => {
  // Fetch from API instead of mock data
  async function loadRealData() {
    const response = await fetch('http://localhost:8000/api/analytics/dashboard');
    const data = await response.json();
    setDashboardData(data);
  }
  
  loadRealData();
  
  // Auto-refresh every 5 minutes
  const interval = setInterval(loadRealData, 5 * 60 * 1000);
  return () => clearInterval(interval);
}, []);
```

## 🎮 API Endpoints

### GET /scan/status
Xem trạng thái scanner

```bash
curl http://localhost:8005/scan/status
```

Response:
```json
{
  "status": "running",
  "watch_folder": "D:/allure-reports",
  "scan_interval_minutes": 5,
  "processed_files_count": 42,
  "next_scan": "2025-11-13T12:35:00"
}
```

### POST /scan/trigger
Trigger scan thủ công

```bash
curl -X POST http://localhost:8005/scan/trigger
```

### GET /scan/processed
Xem files đã xử lý

```bash
curl http://localhost:8005/scan/processed
```

### DELETE /scan/reset
Reset danh sách files đã xử lý (để scan lại)

```bash
curl -X DELETE http://localhost:8005/scan/reset
```

## 📝 Ví dụ thực tế

### Scenario 1: CI/CD Integration

```yaml
# .gitlab-ci.yml
test:
  script:
    - pytest --alluredir=allure-results
    - |
      # Create date folder
      DATE=$(date +%d-%m-%Y)
      mkdir -p /mnt/reports/$DATE
      
      # Copy results
      cp allure-results/*.json /mnt/reports/$DATE/
      
      # Report Watcher will auto-scan within 5 minutes
```

### Scenario 2: Nightly Test Runs

```bash
# cron job (chạy lúc 2 AM)
0 2 * * * /opt/run-tests.sh

# run-tests.sh
#!/bin/bash
DATE=$(date +%d-%m-%Y)
REPORT_DIR=/allure-reports/$DATE

mkdir -p $REPORT_DIR
cd /tests
pytest --alluredir=$REPORT_DIR
```

### Scenario 3: Multiple Projects

```
D:\allure-reports\
├── project-a\
│   ├── 13-11-2025\
│   │   └── *.json
│   └── 14-11-2025\
│       └── *.json
└── project-b\
    └── 13-11-2025\
        └── *.json
```

Update config để scan multiple folders hoặc chạy multiple instances.

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ALLURE_REPORTS_PATH` | `D:/allure-reports` | Base folder chứa reports |
| `SCAN_INTERVAL_MINUTES` | `5` | Thời gian giữa các lần scan |
| `DATABASE_URL` | - | PostgreSQL connection string |
| `REDIS_URL` | - | Redis connection string |

### Thay đổi scan interval

Trong file `.env`:
```env
SCAN_INTERVAL_MINUTES=10  # Scan mỗi 10 phút
```

Hoặc trong code:
```python
scheduler.add_job(
    scan_and_process,
    'interval',
    minutes=10,  # Change here
    ...
)
```

## 🐛 Troubleshooting

### Service không scan

**Kiểm tra:**
```bash
# Xem logs
curl http://localhost:8005/scan/status

# Check folder exists
ls D:\allure-reports

# Check permissions
```

### Files không được process

**Nguyên nhân:**
- Folder name không đúng format `dd-mm-yyyy`
- JSON không hợp lệ
- File đã được process rồi

**Giải pháp:**
```bash
# Reset processed files
curl -X DELETE http://localhost:8005/scan/reset

# Trigger manual scan
curl -X POST http://localhost:8005/scan/trigger
```

### Dashboard không hiển thị data

**Kiểm tra:**
1. Backend services đang chạy
2. Database có data
3. Frontend đang gọi đúng API

```bash
# Check database
psql -U qualify -d qualify_db -c "SELECT COUNT(*) FROM test_results;"

# Check API
curl http://localhost:8000/api/analytics/dashboard
```

## 📈 Performance

### Optimization Tips

1. **Large folders:** Service xử lý async, có thể handle hàng trăm files
2. **Database:** Index trên `created_at`, `history_id` để query nhanh
3. **Memory:** Service track processed files in memory, restart để clear

### Monitoring

```bash
# Watch logs
tail -f logs/report-watcher.log

# Check metrics
curl http://localhost:8005/metrics
```

## 🎯 Best Practices

1. ✅ **Naming Convention:** Dùng format `dd-mm-yyyy` đúng chuẩn
2. ✅ **File Organization:** Một folder cho một ngày
3. ✅ **Cleanup:** Xóa folders cũ sau 30-90 ngày
4. ✅ **Backup:** Backup database thường xuyên
5. ✅ **Monitoring:** Setup alerts nếu scan fails

## 🚀 Next Steps

1. Start Report Watcher Service
2. Add Allure JSON files vào folder
3. Wait 5 minutes (hoặc trigger manual scan)
4. Refresh Dashboard để xem data

---

**Happy Auto-Scanning! 🎉**

