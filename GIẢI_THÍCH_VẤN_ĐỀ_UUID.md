# Giải thích vấn đề UUID

## Vấn đề bạn gặp phải

Bạn thấy test fail "should fail to create user with missing required field" ngày 14/11 có UUID `966f8822-2852-4139-80cd-2d631366abcb` trên dashboard, nhưng khi vào folder ngày 14 không tìm thấy file result.json có chứa UUID này.

## Nguyên nhân

**UUID hiển thị trên dashboard (`966f8822-2852-4139-80cd-2d631366abcb`) là DATABASE UUID**, không phải Allure UUID từ file result.json.

- **Database UUID**: UUID được tự động tạo bởi database khi lưu TestResult (trường `id`)
- **Allure UUID**: UUID từ file result.json gốc (trường `uuid` trong JSON)

Hệ thống trước đây **KHÔNG lưu** Allure UUID vào database, nên không thể map ngược từ database UUID về file result.json.

## Giải pháp đã thực hiện

### 1. Tìm thấy file result.json thực tế

Test failed ngày 14/11 thực tế có:
- **File**: `D:\allure-reports\14-11-2025\b7ee92bc-8dbd-4425-8b7e-a985f16b3508-result.json`
- **Allure UUID**: `b7ee92bc-8dbd-4425-8b7e-a985f16b3508`
- **Status**: `failed`

### 2. Đã thêm trường `allure_uuid` vào database

Đã cập nhật code để:
- Lưu Allure UUID vào database khi import test results
- Trả về cả Database UUID và Allure UUID trong API response
- Có thể map ngược từ Database UUID → Allure UUID → File result.json

## Cách sử dụng

### Tìm file result.json từ Database UUID

1. **Query database** để lấy Allure UUID:
```sql
SELECT allure_uuid, test_name, full_name 
FROM test_results 
WHERE id = '966f8822-2852-4139-80cd-2d631366abcb';
```

2. **Sử dụng script** để tìm file:
```powershell
.\scripts\find-result-by-allure-uuid.ps1 "b7ee92bc-8dbd-4425-8b7e-a985f16b3508"
```

### Tìm file result.json từ test name

```powershell
Get-ChildItem "D:\allure-reports\14-11-2025" -Filter "*-result.json" | 
    ForEach-Object { 
        $content = Get-Content $_.FullName -Raw | ConvertFrom-Json
        if ($content.name -like "*should fail to create user with missing required field*") {
            Write-Host "File: $($_.Name)"
            Write-Host "UUID: $($content.uuid)"
            Write-Host "Status: $($content.status)"
        }
    }
```

## Migration cần thiết

Để áp dụng thay đổi, cần chạy database migration:

```bash
cd backend/shared
alembic revision -m "add_allure_uuid_to_test_results"
# Edit file migration mới tạo
alembic upgrade head
```

Xem chi tiết trong file `MIGRATION_GUIDE_ALLURE_UUID.md`

## Tóm tắt

- ✅ **Đã tìm thấy file**: `D:\allure-reports\14-11-2025\b7ee92bc-8dbd-4425-8b7e-a985f16b3508-result.json`
- ✅ **Đã fix code**: Thêm trường `allure_uuid` để lưu Allure UUID
- ⚠️ **Cần migration**: Chạy database migration để thêm cột mới
- 📝 **Lưu ý**: Các test đã import trước đó sẽ không có `allure_uuid` (NULL)



