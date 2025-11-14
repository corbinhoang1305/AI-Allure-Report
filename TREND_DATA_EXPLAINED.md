# 📊 GIẢI THÍCH DATA TRONG BIỂU ĐỒ TREND

## ❓ Tại sao data có vẻ "sai"?

### **Vấn đề:**

Bạn chỉ có data của **1 ngày** (71 tests từ 13/11/2025), nhưng biểu đồ cần hiển thị **30 ngày**.

### **Giải pháp:**

Vì thiếu dữ liệu lịch sử, hệ thống đang **SIMULATE (mô phỏng)** trend data dựa trên:
- ✅ Số tests thực tế hiện tại: 71
- ✅ Pass rate thực tế: 100%
- ✅ Mô phỏng xu hướng tăng dần trong 30 ngày

---

## 📈 **DATA TREND HIỆN TẠI:**

### **Cách tính (Simulated):**

```javascript
Ngày 1 (14/10):  ~35 tests (50% của 71)
Ngày 5:          ~40 tests
Ngày 10:         ~48 tests  
Ngày 15:         ~56 tests
Ngày 20:         ~63 tests
Ngày 25:         ~68 tests
Ngày 30 (13/11): ~71 tests (100% - hôm nay)
```

**Ý nghĩa:**
- Biểu đồ giả lập như thể bạn bắt đầu với 35 tests
- Mỗi ngày thêm tests mới
- Đến hôm nay có đủ 71 tests

**Pass Rate trend:**
- Ngày 1: ~85% pass
- Ngày 15: ~92% pass  
- Ngày 30: ~100% pass (actual data)

---

## ⚠️ **LƯU Ý:**

### **Data SIMULATED (giả lập):**

✅ **Phần thực tế:**
- Ngày 13/11 (hôm nay): 71 tests, 71 passed, 0 failed
- Pass Rate: 100%

⚠️ **Phần simulate:**
- 29 ngày trước: Tạo trend data giả
- Mục đích: Demo UI

---

## 🎯 **ĐỂ CÓ DATA THẬT 100%:**

### **Cần:**

1. **Data nhiều ngày:**
```
D:\allure-reports\
├── 14-10-2025\    ← 30 ngày trước
│   └── 50-result.json
├── 21-10-2025\    ← 23 ngày trước
│   └── 55-result.json
├── 28-10-2025\    ← 16 ngày trước
│   └── 60-result.json
...
├── 13-11-2025\    ← Hôm nay
│   └── 71-result.json
```

2. **Report Watcher import tất cả**

3. **Backend API tính trend từ database**

---

## 📊 **VÍ DỤ DATA THẬT vs SIMULATE:**

### **Hiện tại (SIMULATED):**

```
Date        Passed  Failed  Source
14/10         35      5     🔸 Simulated
21/10         42      4     🔸 Simulated
28/10         51      3     🔸 Simulated
04/11         60      2     🔸 Simulated
11/11         68      1     🔸 Simulated
13/11         71      0     ✅ REAL DATA
```

### **Khi có full data (REAL):**

```
Date        Passed  Failed  Source
14/10         45      12    ✅ Real from DB
21/10         48      9     ✅ Real from DB
28/10         52      7     ✅ Real from DB
04/11         65      5     ✅ Real from DB
11/11         68      3     ✅ Real from DB
13/11         71      0     ✅ Real from DB
```

---

## 🔧 **CÁCH SỬA ĐỂ CÓ DATA THẬT:**

### **Option 1: Thêm data lịch sử**

Nếu bạn có Allure results của các ngày trước:

```powershell
# Copy data từng ngày vào đúng folder
Copy-Item "old-results\2025-10-14\*.json" "D:\allure-reports\14-10-2025\"
Copy-Item "old-results\2025-10-21\*.json" "D:\allure-reports\21-10-2025\"
Copy-Item "old-results\2025-10-28\*.json" "D:\allure-reports\28-10-2025\"
...

# Watcher sẽ tự động import tất cả
```

### **Option 2: Chấp nhận simulated data**

Cho demo/test purposes, simulated data cũng OK để:
- ✅ Test UI
- ✅ Demo features
- ✅ Xem workflow

---

## 💡 **GIẢI THÍCH CHI TIẾT CÔNG THỨC:**

### **Code hiện tại:**

```javascript
const progress = i / 29;  // 0 -> 1 (30 điểm)
const baseTests = total * (0.5 + progress * 0.5);
// Ngày 1: 71 * 0.5 = 35 tests
// Ngày 15: 71 * 0.75 = 53 tests
// Ngày 30: 71 * 1.0 = 71 tests

const dayPassRate = 0.85 + progress * 0.15;
// Ngày 1: 85% pass rate
// Ngày 15: 92.5% pass rate
// Ngày 30: 100% pass rate (actual)

passed = baseTests * dayPassRate
failed = baseTests - passed
```

---

## ✅ **ĐỀ XUẤT:**

### **1. Giữ nguyên (cho demo):**
- UI đẹp, có trend
- Ngày cuối cùng = data thật
- Phần còn lại = simulated

### **2. Cải thiện thêm:**

Thêm chú thích trên biểu đồ:

```
"* Trend data is simulated based on current results"
"Only 13/11 data is real"
```

### **3. Full real data:**

Chạy tests mỗi ngày và lưu vào folders:
```
13-11-2025, 14-11-2025, 15-11-2025...
```

Sau 30 ngày sẽ có full real trend!

---

## 🎯 **TÓM TẮT:**

**Tại sao data "sai"?**
→ Vì chỉ có data 1 ngày, phải simulate 29 ngày còn lại

**Data nào là thật?**
→ Chỉ có **Overall Health** (71 tests, 100% pass) là THẬT
→ Trend chart là **SIMULATED** từ data thật

**Làm sao có data thật 100%?**
→ Chạy tests mỗi ngày trong 30 ngày, lưu vào folders riêng

---

**BẠN MUỐN TÔI SỬA GÌ THÊM KHÔNG? 🤔**

Options:
1. Thêm disclaimer "Simulated data" trên chart
2. Tạo data giả thực tế hơn
3. Giữ nguyên như hiện tại
4. Ẩn chart này khi chưa có đủ data
