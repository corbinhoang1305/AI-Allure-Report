# 🔍 Kết Quả Phân Tích Flaky Tests - Folder 14-11-2025

## 📊 Tổng Quan

- **Folder phân tích:** `D:\allure-reports\14-11-2025`
- **Tổng số test results:** 78 files
- **Ngày phân tích:** 15/11/2025

### Thống Kê

| Trạng Thái | Số Lượng | Phần Trăm |
|-----------|----------|-----------|
| ✅ Passed | 70 | 89.7% |
| ❌ Failed | 8 | 10.3% |
| 💔 Broken | 0 | 0% |
| ⏭️ Skipped | 0 | 0% |
| **🔄 Flaky Tests** | **4** | **5.1%** |

---

## ⚠️ Danh Sách 4 Flaky Tests Phát Hiện

### 1️⃣ Flaky Test #1: Admin Update Users

**📝 Test Name:**
```
should allow admin to update users
```

**📍 Full Path:**
```
users/users.permissions.spec.ts#Users - Permission Tests Admin Role Privileges 
should allow admin to update users
```

**🆔 Test Case ID:**
```
9db43693583994d37eb2e3ddcb9f60d3
```

**📊 Số lần xuất hiện:** 3 lần

**⚡ Các trạng thái:** `failed`, `passed`

**Chi tiết:**
| Run | Status | Duration | File |
|-----|--------|----------|------|
| 1 | ❌ FAILED | 0.81s | 6a05a4bd-f91b-4c66-9ac2-9a3837d123b2-result.json |
| 2 | ✅ PASSED | 1.68s | 9cf839eb-4718-47ce-b8f1-458c237fd4dc-result.json |
| 3 | ❌ FAILED | 1.79s | d38bef4f-f781-489e-8311-d8155f2f6dd9-result.json |

**📌 Nhận xét:**
- Test này flaky với tỷ lệ fail 2/3 (66.7%)
- Duration của failed runs ngắn hơn passed run
- Có thể liên quan đến timing/race condition

---

### 2️⃣ Flaky Test #2: Create User Missing Field

**📝 Test Name:**
```
should fail to create user with missing required field
```

**📍 Full Path:**
```
users/users.crud.spec.ts#Users - CRUD Operations Create User 
should fail to create user with missing required field
```

**🆔 Test Case ID:**
```
eef530b7628cb26cf2444870d4c5bf6b
```

**📊 Số lần xuất hiện:** 2 lần

**⚡ Các trạng thái:** `passed`, `failed`

**Chi tiết:**
| Run | Status | Duration | File |
|-----|--------|----------|------|
| 1 | ✅ PASSED | 1.38s | 728e925f-e70a-4989-a6ae-43b515d754d4-result.json |
| 2 | ❌ FAILED | 0.07s | b7ee92bc-8dbd-4425-8b7e-a985f16b3508-result.json |

**📌 Nhận xét:**
- Failed run chỉ mất 0.07s → Có thể fail ngay lập tức
- Passed run mất 1.38s → Chạy bình thường
- Nghi ngờ validation hoặc error handling không ổn định

---

### 3️⃣ Flaky Test #3: Admin Change User Role

**📝 Test Name:**
```
should allow admin to change user role
```

**📍 Full Path:**
```
users/users.permissions.spec.ts#Users - Permission Tests Cross-Role Scenarios 
should allow admin to change user role
```

**🆔 Test Case ID:**
```
3ab4b135fdf28ab8ac44ff8eaef9ffc2
```

**📊 Số lần xuất hiện:** 2 lần

**⚡ Các trạng thái:** `failed`, `passed`

**Chi tiết:**
| Run | Status | Duration | File |
|-----|--------|----------|------|
| 1 | ❌ FAILED | 0.79s | 753dfc45-33d7-4059-82e4-87298ddf6726-result.json |
| 2 | ✅ PASSED | 1.74s | 900eadc7-a422-41cb-ad74-c1c954f17228-result.json |

**📌 Nhận xét:**
- Failed run nhanh hơn nhiều (0.79s vs 1.74s)
- Tỷ lệ flaky 50%
- Permission test có thể bị ảnh hưởng bởi state của các test khác

---

### 4️⃣ Flaky Test #4: Update User Valid Data

**📝 Test Name:**
```
should update user with valid data as admin
```

**📍 Full Path:**
```
users/users.crud.spec.ts#Users - CRUD Operations Update User 
should update user with valid data as admin
```

**🆔 Test Case ID:**
```
5d2deda4f86b9b1e9b338bfb98ce76a8
```

**📊 Số lần xuất hiện:** 2 lần

**⚡ Các trạng thái:** `failed`, `passed`

**Chi tiết:**
| Run | Status | Duration | File |
|-----|--------|----------|------|
| 1 | ❌ FAILED | 0.70s | 87d02b98-3710-4d68-b82a-05a39497b676-result.json |
| 2 | ✅ PASSED | 1.86s | a40f1906-f08a-47dc-8f46-337fe2a8d1ac-result.json |

**📌 Nhận xét:**
- Pattern giống Flaky Test #3
- Failed run nhanh hơn (0.70s vs 1.86s)
- CRUD operation có thể bị ảnh hưởng bởi database state

---

## 🔍 Phân Tích Tổng Quan

### Pattern Chung

1. **Timing Issue:**
   - Tất cả failed runs đều có duration ngắn hơn
   - Failed runs thường < 1s
   - Passed runs thường > 1.3s

2. **Test Categories:**
   - **Permission Tests:** 2/4 flaky tests
   - **CRUD Operations:** 2/4 flaky tests

3. **Flaky Rate:**
   - Test #1: 66.7% fail rate (2/3)
   - Test #2: 50% fail rate (1/2)
   - Test #3: 50% fail rate (1/2)
   - Test #4: 50% fail rate (1/2)

### Nguyên Nhân Có Thể

#### 1. **Race Conditions**
- Tests chạy quá nhanh → Không đợi response
- Database operations chưa hoàn tất
- API response delay

#### 2. **Test Dependencies**
- Tests không isolated
- Shared state giữa các tests
- Database cleanup không đúng

#### 3. **Authentication/Permission Issues**
- Token expiration
- Permission cache không consistent
- Session state không ổn định

#### 4. **Database State**
- Test data không được cleanup
- Foreign key constraints
- Unique constraints bị conflict

---

## 💡 Khuyến Nghị Sửa Chữa

### 1. Thêm Wait/Retry Mechanism

```javascript
// Bad
await createUser(userData);
await verifyUserCreated(); // Có thể fail nếu DB chưa commit

// Good
await createUser(userData);
await waitForCondition(() => userExists(userId), { timeout: 5000 });
await verifyUserCreated();
```

### 2. Improve Test Isolation

```javascript
// Before each test
beforeEach(async () => {
  await cleanupDatabase();
  await seedTestData();
  await resetCache();
});

// After each test
afterEach(async () => {
  await cleanupDatabase();
});
```

### 3. Add Explicit Waits

```javascript
// Thay vì
await updateUser(userId, newData);
expect(response.status).toBe(200);

// Nên dùng
await updateUser(userId, newData);
await page.waitForResponse(response => 
  response.url().includes('/users') && response.status() === 200
);
expect(response.status).toBe(200);
```

### 4. Fix Permission Tests

```javascript
// Đảm bảo permissions được load đầy đủ
async function loginAsAdmin() {
  const token = await login(adminCredentials);
  await waitForPermissionsLoaded(token);
  return token;
}
```

### 5. Add Test Retry Logic

```javascript
// playwright.config.ts
export default {
  retries: 2, // Retry failed tests
  timeout: 30000,
  expect: {
    timeout: 5000
  }
}
```

---

## 📁 Files Đã Tạo

### 1. **check_flaky_tests.py**
- Script Python đầy đủ tính năng
- Phân tích chi tiết
- Export JSON report
- Cần Python 3.7+

### 2. **check-flaky-tests-quick.ps1**
- Script PowerShell nhanh
- Không cần Python
- Export CSV report
- Chạy trực tiếp trên Windows

### 3. **check-flaky-tests.bat**
- Batch file để chạy Python script
- Kiểm tra Python installed
- Dễ dàng double-click

### 4. **FLAKY_TEST_CHECKER_README.md**
- Hướng dẫn đầy đủ
- Giải thích flaky test
- Troubleshooting guide

---

## 🎯 Action Items

### Ưu Tiên Cao (Fix Ngay)

- [ ] **Test #1:** `should allow admin to update users` (66.7% fail rate)
  - Thêm explicit waits
  - Kiểm tra permission loading
  - Review database transactions

### Ưu Tiên Trung Bình

- [ ] **Test #2:** `should fail to create user with missing required field`
  - Review validation logic
  - Add retry mechanism
  - Check error handling

- [ ] **Test #3:** `should allow admin to change user role`
  - Isolate permission tests
  - Clear permission cache
  - Add wait for role update

- [ ] **Test #4:** `should update user with valid data as admin`
  - Improve test isolation
  - Add database cleanup
  - Check for race conditions

---

## 📊 Cách Chạy Scripts

### PowerShell Script (Không cần Python)

```powershell
.\check-flaky-tests-quick.ps1
```

Hoặc với folder khác:
```powershell
.\check-flaky-tests-quick.ps1 -FolderPath "D:\allure-reports\15-11-2025"
```

### Python Script (Đầy đủ tính năng)

```powershell
# Cài Python từ: https://www.python.org/downloads/

# Chạy script
python check_flaky_tests.py

# Hoặc với folder khác
python check_flaky_tests.py "D:\allure-reports\15-11-2025"
```

### Batch File (Dễ nhất)

Double-click vào file:
```
check-flaky-tests.bat
```

---

## 📈 Theo Dõi Cải Thiện

Sau khi fix, chạy lại script để verify:

```powershell
# Chạy trên folder mới
.\check-flaky-tests-quick.ps1 -FolderPath "D:\allure-reports\16-11-2025"

# So sánh kết quả
# Mục tiêu: 0 flaky tests!
```

---

## 📞 Support

Nếu cần thêm thông tin, kiểm tra:
- `FLAKY_TEST_CHECKER_README.md` - Hướng dẫn chi tiết
- `flaky_tests_report_*.csv` - Báo cáo CSV
- Log files của từng test trong folder

---

**Kết luận:** Có 4 flaky tests cần được fix, chủ yếu liên quan đến **timing issues** và **test isolation**.

**Priority:** Fix Test #1 trước (fail rate cao nhất)

---

**Generated by:** Flaky Test Detector v1.0  
**Date:** 15/11/2025


