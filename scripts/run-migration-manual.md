# Hướng dẫn chạy Migration thủ công

## Vấn đề
Python không có trong PATH của hệ thống.

## Giải pháp

### Cách 1: Sử dụng Virtual Environment (Nếu đã có)

Nếu bạn đã có virtual environment ở đâu đó:

```powershell
# Activate venv
cd backend\services\report-watcher
.\venv\Scripts\activate

# Install alembic nếu chưa có
pip install alembic

# Chạy migration
cd ..\..\shared
alembic upgrade head

# Backfill UUID
cd ..\..
python scripts\backfill-allure-uuid.py
```

### Cách 2: Cài đặt Python

1. Tải Python từ https://www.python.org/downloads/
2. Cài đặt và chọn "Add Python to PATH"
3. Restart PowerShell
4. Chạy lại script: `.\scripts\run-migration-and-backfill.ps1`

### Cách 3: Sử dụng Docker (Nếu có Docker)

```powershell
# Chạy migration trong Docker container
docker-compose -f infrastructure/docker-compose/docker-compose.yml exec postgres psql -U qualify -d qualify_db -c "ALTER TABLE test_results ADD COLUMN IF NOT EXISTS allure_uuid VARCHAR(255);"
docker-compose -f infrastructure/docker-compose/docker-compose.yml exec postgres psql -U qualify -d qualify_db -c "CREATE INDEX IF NOT EXISTS ix_test_results_allure_uuid ON test_results(allure_uuid);"
```

### Cách 4: Chạy SQL trực tiếp

Nếu bạn có quyền truy cập database trực tiếp:

```sql
-- Thêm cột allure_uuid
ALTER TABLE test_results ADD COLUMN IF NOT EXISTS allure_uuid VARCHAR(255);

-- Tạo index
CREATE INDEX IF NOT EXISTS ix_test_results_allure_uuid ON test_results(allure_uuid);
```

Sau đó chạy backfill script khi có Python:
```powershell
python scripts\backfill-allure-uuid.py
```

## Kiểm tra Migration đã chạy

```sql
-- Kiểm tra cột đã được thêm chưa
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'test_results' AND column_name = 'allure_uuid';
```

## Sau khi Migration

1. Refresh browser (Ctrl+F5)
2. Kiểm tra UUID hiển thị đúng chưa
3. Nếu vẫn sai, chạy backfill script để update UUID từ JSON files



