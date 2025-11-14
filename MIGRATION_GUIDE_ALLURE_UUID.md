# Migration Guide: Adding Allure UUID Support

## Vấn đề

UUID hiển thị trên dashboard (`966f8822-2852-4139-80cd-2d631366abcb`) là **Database UUID**, không phải **Allure UUID** từ file result.json. Điều này khiến không thể tìm lại file result.json gốc từ UUID hiển thị trên dashboard.

## Giải pháp

Đã thêm trường `allure_uuid` vào model `TestResult` để lưu UUID gốc từ Allure result.json file.

## Thay đổi

### 1. Database Model (`backend/shared/models.py`)
- Thêm trường `allure_uuid` vào `TestResult` model
- Trường này lưu UUID gốc từ Allure result.json file

### 2. Code Updates
- `backend/services/report-aggregator/app/main.py`: Lưu `allure_uuid` khi import test results
- `backend/services/report-watcher/app/main.py`: Lưu `allure_uuid` khi process reports
- `backend/services/analytics-service/app/main.py`: Trả về `allureUuid` trong API response

## Migration Database

Cần tạo migration để thêm cột `allure_uuid` vào bảng `test_results`:

```bash
cd backend/shared
alembic revision -m "add_allure_uuid_to_test_results"
```

Sau đó edit file migration mới tạo:

```python
def upgrade():
    op.add_column('test_results', 
        sa.Column('allure_uuid', sa.String(255), nullable=True))
    op.create_index('ix_test_results_allure_uuid', 'test_results', ['allure_uuid'])

def downgrade():
    op.drop_index('ix_test_results_allure_uuid', 'test_results')
    op.drop_column('test_results', 'allure_uuid')
```

Chạy migration:
```bash
alembic upgrade head
```

## Cách sử dụng

### Tìm file result.json từ Database UUID

1. Query database để lấy `allure_uuid` từ `test_results` table:
```sql
SELECT allure_uuid FROM test_results WHERE id = '966f8822-2852-4139-80cd-2d631366abcb';
```

2. Sử dụng script PowerShell để tìm file:
```powershell
.\scripts\find-result-by-allure-uuid.ps1 "b7ee92bc-8dbd-4425-8b7e-a985f16b3508"
```

### Tìm file result.json từ Allure UUID

Nếu bạn đã biết Allure UUID:
```powershell
.\scripts\find-result-by-allure-uuid.ps1 "b7ee92bc-8dbd-4425-8b7e-a985f16b3508"
```

## Ví dụ thực tế

**Test failed ngày 14/11:**
- Database UUID (hiển thị trên dashboard): `966f8822-2852-4139-80cd-2d631366abcb`
- Allure UUID (từ result.json): `b7ee92bc-8dbd-4425-8b7e-a985f16b3508`
- File location: `D:\allure-reports\14-11-2025\b7ee92bc-8dbd-4425-8b7e-a985f16b3508-result.json`

Sau khi migration, bạn có thể:
1. Query database để lấy `allure_uuid` từ database UUID
2. Tìm file result.json bằng Allure UUID

## Lưu ý

- Các test results đã import trước khi có migration sẽ không có `allure_uuid` (NULL)
- Các test results mới import sau migration sẽ có `allure_uuid`
- Để backfill data cũ, cần re-import các test results từ result.json files

