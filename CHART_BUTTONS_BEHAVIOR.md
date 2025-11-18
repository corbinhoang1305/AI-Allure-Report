# Historical Chart - Filter Buttons Behavior

## 🎯 Behavior Mới (Simple Toggle)

### Click để Hide
```
[Sáng] → Click → [Mờ]
```
- Button làm mờ (opacity 30%)
- Icon grayscale
- Text gạch ngang + màu xám
- Series biến mất khỏi chart

### Click để Show
```
[Mờ] → Click → [Sáng]
```
- Button sáng lại (opacity 100%)
- Icon màu gốc
- Text bình thường + màu series
- Series hiển thị trên chart

## ✨ Features

### 1. Toggle Tự Do
- ✅ Click bất kỳ button nào → Toggle
- ✅ Không có ràng buộc
- ✅ Không có button bị disabled

### 2. Hide Tất Cả (Cho Phép)
```
Bước 1: [Sáng] [Sáng] [Sáng]
         ↓ click ↓ click ↓ click
Bước 2: [Mờ]   [Mờ]   [Mờ]
```
- Chart trống
- **NHƯNG** tất cả buttons vẫn clickable
- Click bất kỳ button mờ → Show lại

### 3. Back Lại TrạngÁi (Không Reload)
```
Hide tất cả: [Mờ] [Mờ] [Mờ]
              ↓ click các button mờ
Show lại:    [Sáng] [Sáng] [Sáng]
```
- Không cần refresh page
- Click để toggle từng button

## 🎨 Visual States

### Active (Sáng) ✨
- Background: `bg-gray-800/50`
- Opacity: `100%`
- Icon: Màu gốc
- Text: Màu series (green/orange/red)
- Shadow: Có
- Hover: Scale up + background tối hơn

### Hidden (Mờ) 😶‍🌫️
- Background: `bg-gray-800/20`
- Opacity: `30%`
- Icon: Grayscale + opacity 50%
- Text: Line-through + màu xám (#666)
- Shadow: Không
- Hover: Opacity tăng lên 50%

## 💡 Use Cases

### UC1: Focus vào một loại test
```
Tôi chỉ muốn xem Failed tests
→ Click Passed → [Mờ]
→ Click Flaky → [Mờ]
→ Chart chỉ hiển thị Failed (đỏ)
```

### UC2: So sánh 2 loại
```
Tôi muốn so sánh Passed vs Failed
→ Click Flaky → [Mờ]
→ Chart hiển thị Passed (xanh) và Failed (đỏ)
```

### UC3: Xem tất cả
```
Tôi đã hide một số, giờ muốn xem tất cả
→ Click các button mờ
→ Tất cả sáng lại
```

### UC4: Tạm ẩn chart
```
Tôi không muốn thấy chart này lúc này
→ Click cả 3 buttons
→ Chart trống
→ Sau đó click lại để show
```

## 🔄 Comparison

| Feature | Old Behavior | New Behavior |
|---------|--------------|--------------|
| Toggle | Có ràng buộc | ✅ Tự do |
| Hide all | Không được | ✅ Được |
| Disabled state | Có | ✅ Không |
| Back to default | Reload | ✅ Click buttons |
| Complexity | High | ✅ Low |

## 📝 Summary

**Principle:** Simple Toggle - Complete Freedom

- ✅ Click = Hide/Show (no rules)
- ✅ Tất cả buttons luôn clickable
- ✅ Visual feedback rõ ràng (mờ 30%)
- ✅ Không bao giờ stuck
- ✅ Không cần reload

**Result:** UX đơn giản, trực quan, dễ sử dụng! 🎉

