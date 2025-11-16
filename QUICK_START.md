# 🚀 QUALIFY.AI - Quick Start

## ✅ Đã Setup Xong! 

Tất cả services đang chạy và sẵn sàng sử dụng.

---

## 🌐 Truy Cập Ngay

### **Dashboard Chính**
👉 **http://localhost:3000**

### API Gateway
👉 http://localhost:8000

### MinIO Console
👉 http://localhost:9001
- Username: `minioadmin`
- Password: `minioadmin123`

---

## 🎯 Scripts Nhanh

### Kiểm tra trạng thái
```powershell
.\show-status.ps1
```

### Start tất cả services
```cmd
START-ALL.bat
```

### Stop tất cả services
```cmd
STOP-ALL.bat
```

### Xem logs backend
```powershell
cd infrastructure\docker-compose
docker compose logs -f
```

---

## 📁 Upload Test Reports

Đặt Allure reports vào:
```
D:\allure-reports\
```

Service sẽ tự động import mỗi 2 phút.

---

## 📚 Tài Liệu Đầy Đủ

Xem chi tiết tại: **`HƯỚNG_DẪN_SỬ_DỤNG.md`**

---

## 🆘 Cần Trợ Giúp?

### Services không chạy?
```powershell
.\show-status.ps1
```

### Restart tất cả
```cmd
STOP-ALL.bat
START-ALL.bat
```

### Xem logs lỗi
```powershell
cd infrastructure\docker-compose
docker compose logs -f [service-name]
```

---

**Built with ❤️ for Quality Engineering**


