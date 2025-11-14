# Hướng dẫn đưa dữ liệu Allure Report vào QUALIFY.AI

## 📋 Tổng quan

QUALIFY.AI hỗ trợ 3 cách để load dữ liệu Allure Report:

1. **Upload qua UI** (Đơn giản nhất - Không cần backend)
2. **Đặt trong thư mục public** (Cho demo)
3. **Upload qua Backend API** (Production-ready)

---

## 🎯 Cách 1: Upload qua UI (Được khuyến nghị cho demo)

### Bước 1: Chuẩn bị dữ liệu Allure

Allure Report có cấu trúc như sau:

```
allure-results/
├── abc123-result.json          # Test result
├── def456-result.json          # Test result
├── ghi789-container.json       # Suite container
├── jkl012-attachment.png       # Screenshot
└── categories.json             # (Optional)
```

### Bước 2: Mở Dashboard

1. Truy cập: http://localhost:3000/dashboard
2. Bạn sẽ thấy card "Upload Allure Report" ở đầu trang

### Bước 3: Upload dữ liệu

**Option A: Upload từng file**
- Click "Click to upload JSON files"
- Chọn các file `*-result.json` từ thư mục `allure-results`
- Click Open

**Option B: Upload cả folder**
- Click "Click to upload folder"
- Chọn thư mục `allure-results`
- Click Select Folder

### Bước 4: Xem kết quả

- Dashboard sẽ tự động parse dữ liệu
- Các metrics sẽ được tính toán và hiển thị:
  - Pass Rate
  - Total Tests
  - Historical Trends
  - Test Suites/Projects

---

## 🗂️ Cách 2: Đặt trong thư mục public

### Bước 1: Copy files vào public

```bash
# Tạo thư mục
mkdir frontend/public/sample-data

# Copy Allure results
cp path/to/allure-results/*.json frontend/public/sample-data/
```

### Bước 2: Load data trong code

Update file `frontend/app/dashboard/page.tsx`:

```typescript
import { loadAllureResultsFromPublic, aggregateAllureResults } from "@/lib/allure-parser";

useEffect(() => {
  async function loadData() {
    // Load từ public folder
    const results = await loadAllureResultsFromPublic('/sample-data/results.json');
    const dashboardData = aggregateAllureResults(results);
    setDashboardData(dashboardData);
    setLoading(false);
  }
  
  loadData();
}, []);
```

---

## 🚀 Cách 3: Upload qua Backend API (Production)

### Bước 1: Start Backend Services

```bash
cd infrastructure/docker-compose
docker-compose up -d
```

### Bước 2: Upload qua API

```bash
# Zip Allure results
cd path/to/allure-results
zip -r allure-results.zip *.json

# Upload via API
curl -X POST http://localhost:8000/api/reports/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@allure-results.zip" \
  -F "project_id=YOUR_PROJECT_ID" \
  -F "suite_id=YOUR_SUITE_ID" \
  -F "environment=staging" \
  -F "build_number=123"
```

### Bước 3: Dashboard tự động load

Dashboard sẽ fetch data từ backend API:

```typescript
// Frontend tự động call API
const response = await fetch('http://localhost:8000/api/analytics/dashboard');
const data = await response.json();
```

---

## 📊 Format dữ liệu Allure

### File *-result.json

```json
{
  "uuid": "abc123-def456-ghi789",
  "name": "test_user_login",
  "fullName": "tests.auth.test_user_login",
  "status": "passed",
  "statusDetails": {
    "message": "",
    "trace": ""
  },
  "start": 1699900000000,
  "stop": 1699900005000,
  "labels": [
    {
      "name": "suite",
      "value": "Authentication Tests"
    },
    {
      "name": "severity",
      "value": "critical"
    },
    {
      "name": "tag",
      "value": "smoke"
    }
  ],
  "parameters": [
    {
      "name": "username",
      "value": "testuser"
    }
  ],
  "attachments": [
    {
      "name": "Screenshot",
      "source": "abc123-attachment.png",
      "type": "image/png"
    }
  ],
  "steps": [
    {
      "name": "Open login page",
      "status": "passed",
      "start": 1699900000000,
      "stop": 1699900002000
    },
    {
      "name": "Enter credentials",
      "status": "passed",
      "start": 1699900002000,
      "stop": 1699900004000
    }
  ]
}
```

### Status values

- `"passed"` - Test thành công
- `"failed"` - Test thất bại
- `"broken"` - Test bị lỗi (exception)
- `"skipped"` - Test bị bỏ qua

### Labels thường dùng

- `suite` - Tên test suite
- `severity` - blocker, critical, normal, minor, trivial
- `feature` - Feature name
- `story` - User story
- `tag` - Tags (smoke, regression, etc.)

---

## 🔍 Ví dụ thực tế

### Ví dụ 1: Upload file từ Pytest + Allure

```bash
# Run tests với Allure
pytest tests/ --alluredir=allure-results

# Upload vào QUALIFY.AI
# Option 1: Via UI
# - Mở http://localhost:3000/dashboard
# - Click "Upload Allure Report"
# - Chọn thư mục allure-results

# Option 2: Via API (khi có backend)
zip -r results.zip allure-results/
curl -X POST http://localhost:8000/api/reports/upload \
  -F "file=@results.zip" \
  -F "project_id=PROJECT_ID" \
  -F "suite_id=SUITE_ID"
```

### Ví dụ 2: Load từ CI/CD

```yaml
# .gitlab-ci.yml or .github/workflows/test.yml
test:
  script:
    - pytest --alluredir=allure-results
    - zip -r allure-results.zip allure-results/
    # Upload to QUALIFY.AI
    - |
      curl -X POST $QUALIFY_API/api/reports/upload \
        -H "Authorization: Bearer $API_TOKEN" \
        -F "file=@allure-results.zip" \
        -F "project_id=$PROJECT_ID" \
        -F "suite_id=$SUITE_ID" \
        -F "build_number=$CI_PIPELINE_ID"
```

---

## ⚙️ Configuration

### Frontend Configuration

Tạo file `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_FILE_UPLOAD=true
NEXT_PUBLIC_MAX_FILE_SIZE=100000000
```

### Tùy chỉnh Parser

Nếu cần custom parser, edit `frontend/lib/allure-parser.ts`:

```typescript
export function parseAllureResult(result: AllureResult) {
  // Thêm logic custom của bạn
  return {
    // ... custom fields
  };
}
```

---

## 🐛 Troubleshooting

### Lỗi: "No valid Allure result files found"

**Nguyên nhân:** File không đúng format hoặc bị corrupt

**Giải pháp:**
1. Kiểm tra file có đuôi `-result.json`
2. Validate JSON format: `cat file.json | jq .`
3. Đảm bảo file có đủ các trường bắt buộc

### Lỗi: "Failed to parse JSON"

**Nguyên nhân:** JSON không hợp lệ

**Giải pháp:**
```bash
# Validate JSON
jsonlint file.json

# Or using jq
jq empty file.json
```

### Dashboard không hiển thị data

**Kiểm tra:**
1. Mở Browser Console (F12)
2. Xem tab Network để check API calls
3. Xem tab Console để check JavaScript errors
4. Verify data format trong DevTools

---

## 📚 Resources

- [Allure Framework Documentation](https://docs.qameta.io/allure/)
- [Allure Report Format](https://github.com/allure-framework/allure2/blob/master/docs/test-result-format.adoc)
- [QUALIFY.AI API Documentation](./API.md)

---

## 💡 Tips

1. **Batch Upload:** Upload nhiều files cùng lúc để tiết kiệm thời gian
2. **Naming Convention:** Đặt tên rõ ràng cho projects và suites
3. **Regular Upload:** Upload kết quả test thường xuyên để theo dõi trends
4. **Use Labels:** Sử dụng labels để phân loại tests tốt hơn
5. **Include Attachments:** Upload screenshots và logs để RCA dễ dàng hơn

---

**Happy Testing! 🚀**

