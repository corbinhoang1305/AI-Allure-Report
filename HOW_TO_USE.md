# 🎯 HƯỚNG DẪN SỬ DỤNG QUALIFY.AI

## 📂 ĐẶT DỮ LIỆU JSON VÀO ĐÂU?

### **Cấu trúc folder:**

```
D:\allure-reports\
└── [dd-MM-yyyy]\           ← Folder theo ngày (VD: 13-11-2025)
    └── *.json              ← Tất cả Allure result JSON files
```

### **Ví dụ:**

```
D:\allure-reports\
├── 13-11-2025\             ← Ngày 13/11/2025
│   ├── test-001.json
│   ├── test-002.json
│   └── test-003.json
│
├── 14-11-2025\             ← Ngày 14/11/2025  
│   └── test-004.json
│
└── 15-11-2025\             ← Ngày 15/11/2025
    └── test-005.json
```

---

## ⚡ CÁCH HOẠT ĐỘNG:

1. **Bạn đặt JSON files** vào `D:\allure-reports\[ngày-hôm-nay]\`
2. **Report Watcher Service** tự động quét **mỗi 5 phút**
3. **Data tự động** xuất hiện trên Dashboard
4. **Dashboard auto-refresh** mỗi 5 phút

---

## 🚀 CHẠY SERVICE:

### **Start Report Watcher (Terminal 1):**

```powershell
cd D:\practice\AI-Allure-Report
.\scripts\start-watcher.bat
```

### **Dashboard đã chạy sẵn (Terminal 2):**

http://localhost:3000/dashboard

---

## ✨ THÊM DATA MỖI NGÀY:

```powershell
# Tạo folder cho hôm nay
$today = Get-Date -Format "dd-MM-yyyy"
New-Item -ItemType Directory -Path "D:\allure-reports\$today"

# Copy Allure results vào
Copy-Item "path/to/allure-results/*.json" "D:\allure-reports\$today\"

# Watcher tự động import trong 5 phút!
```

---

## 🎯 TÓM TẮT:

| Việc | Cách thực hiện |
|------|----------------|
| **Đặt data** | `D:\allure-reports\dd-MM-yyyy\*.json` |
| **Quét tự động** | Mỗi 5 phút |
| **Xem kết quả** | http://localhost:3000/dashboard |
| **Check status** | `curl http://localhost:8005/scan/status` |

---

**ĐƠN GIẢN VẬY THÔI! 🎉**

