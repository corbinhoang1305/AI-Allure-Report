# Hướng dẫn Migration và Backfill Allure UUID

## Tổng quan

Để hiển thị đúng Allure UUID từ JSON files trên dashboard, cần:
1. Chạy migration để thêm cột `allure_uuid` vào database
2. Backfill Allure UUID từ JSON files vào database

## Files đã tạo

1. **Migration file**: `backend/shared/migrations/versions/002_add_allure_uuid_to_test_results.py`
   - Thêm cột `allure_uuid` vào bảng `test_results`
   - Tạo index cho cột này

2. **Backfill script**: `scripts/backfill-allure-uuid.py`
   - Đọc JSON files từ folder
   - Map UUID từ JSON vào database dựa trên test name và historyId

3. **Run script**: `scripts/run-migration-and-backfill.ps1`
   - Chạy migration và backfill tự động

## Cách chạy

### Cách 1: Chạy tự động (Khuyến nghị)

```powershell
.\scripts\run-migration-and-backfill.ps1
```

### Cách 2: Chạy từng bước

#### Bước 1: Chạy Migration

```powershell
cd backend\shared
alembic upgrade head
cd ..\..
```

#### Bước 2: Backfill Allure UUID

```powershell
python scripts\backfill-allure-uuid.py
```

Hoặc chỉ định folder cụ thể:

```powershell
python scripts\backfill-allure-uuid.py "D:\allure-reports\14-11-2025"
```

## Kiểm tra kết quả

Sau khi chạy migration và backfill:

1. Refresh browser (Ctrl+F5)
2. Mở test "should fail to create user with missing required field"
3. UUID hiển thị phải là: `b7ee92bc-8dbd-4425-8b7e-a985f16b3508`

## Troubleshooting

### Lỗi: "alembic: command not found"
```powershell
pip install alembic
```

### Lỗi: "Python not found"
- Đảm bảo Python đã được cài đặt và trong PATH
- Hoặc dùng `python3` thay vì `python`

### Lỗi: "Database connection failed"
- Kiểm tra database đang chạy
- Kiểm tra file `backend/shared/config.py` có đúng connection string không

### Migration đã chạy nhưng không có Allure UUID
- Chạy lại backfill script: `python scripts\backfill-allure-uuid.py`
- Kiểm tra JSON files có trong folder không
- Kiểm tra test name và historyId có khớp không

## Lưu ý

- Migration chỉ cần chạy 1 lần
- Backfill có thể chạy nhiều lần để update UUID cho các test mới
- Nếu có test results mới được import, cần chạy lại backfill hoặc đảm bảo import process đã lưu `allure_uuid`



