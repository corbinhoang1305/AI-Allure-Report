# 📂 NƠI ĐẶT DỮ LIỆU ALLURE JSON

## ✅ HIỆN TẠI:

**Dashboard đang load data THẬT từ:**
```
frontend/public/real-data/all-results.json
```

**Chứa:** 30 Playwright API tests thật

**Auto-refresh:** Mỗi 5 phút

---

## 🔄 ĐỂ UPDATE DATA MỚI:

### **Cách 1: Tự động (Report Watcher - Khuyến nghị)**

#### Đặt file vào:
```
D:\allure-reports\
└── [dd-MM-yyyy]\           ← VD: 13-11-2025, 14-11-2025
    └── *.json              ← Allure result files
```

#### Start Watcher:
```powershell
cd D:\practice\AI-Allure-Report
.\scripts\start-watcher.bat
```

Service tự động:
- 🔍 Quét folder mỗi 5 phút
- 📊 Parse JSON files
- 💾 Import vào database
- 🔄 Dashboard auto-refresh

---

### **Cách 2: Thủ công (Không cần backend)**

#### Copy files mới:
```powershell
# Merge tất cả JSON thành 1 file
$files = Get-ChildItem "D:\allure-reports\your-folder" -Filter "*-result.json"
$allResults = @()
foreach($file in $files) {
    $content = Get-Content $file.FullName -Raw | ConvertFrom-Json
    $allResults += $content
}
$allResults | ConvertTo-Json -Depth 10 | Out-File "D:\practice\AI-Allure-Report\frontend\public\real-data\all-results.json" -Encoding utf8
```

#### Refresh Dashboard:
- Mở http://localhost:3000/dashboard
- Bấm F5

---

## 📊 DATA FLOW:

```
Allure JSON files
    ↓
D:\allure-reports\dd-MM-yyyy\
    ↓
[Option 1] Report Watcher → Database → API → Frontend
    hoặc
[Option 2] Manual copy → public/real-data/ → Frontend
    ↓
Dashboard hiển thị data thật!
```

---

## 🎯 TÓM TẮT:

**Hiện tại:** Dashboard đang show data THẬT từ 30 tests

**Để thêm data mới:**
1. Đặt JSON vào `D:\allure-reports\[ngày]\`
2. Chạy Watcher HOẶC copy thủ công
3. Dashboard tự động update

**File data thật:** `frontend/public/real-data/all-results.json`

---

**REFRESH DASHBOARD NGAY ĐỂ XEM DATA THẬT! 🚀**

http://localhost:3000/dashboard (Bấm F5)

