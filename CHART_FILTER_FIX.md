# 🐛 Fix: Historical Chart Filter Buttons UX

## Yêu cầu

Cải thiện UX của các button filter (Passed, Flaky, Failed) trong Historical Trend Chart:

1. ✅ Click button → Làm mờ (nhưng vẫn clickable)
2. ✅ Click lại lần nữa → Sáng lại và chart update
3. ✅ Cho phép toggle tự do tất cả các button
4. ✅ Không cần reload để back về trạng thái cũ

## Giải pháp đã áp dụng

### 1. Simple Toggle Logic ✅

**File:** `frontend/components/dashboard/TrendChart.tsx`

**Thay đổi ở `handleLegendClick`:**

```typescript
const handleLegendClick = (dataKey: string) => {
  setHiddenSeries(prev => {
    const newSet = new Set(prev);
    
    // Toggle: Nếu đang hidden thì show, nếu đang show thì hide
    if (newSet.has(dataKey)) {
      newSet.delete(dataKey); // Show lại
    } else {
      newSet.add(dataKey); // Hide đi
    }
    
    return newSet;
  });
};
```

**Logic:**
- ✅ Simple toggle - Click để hide/show
- ✅ Không có ràng buộc - tự do toggle tất cả buttons
- ✅ Luôn clickable - không có trạng thái disabled

### 2. UI/UX cải tiến ✅

**Thay đổi ở `CustomLegend`:**

**2 trạng thái button đơn giản:**

1. **Active (Sáng)** - Series đang hiển thị
   ```typescript
   bg-gray-800/50 hover:bg-gray-800/70 shadow-lg hover:scale-105 cursor-pointer
   ```
   - ✅ Màu đậm, có shadow
   - ✅ Hover scale up
   - ✅ Icon màu gốc sáng
   - ✅ Text màu theo series (green/orange/red)
   - ✅ Click để hide

2. **Hidden (Mờ)** - Series bị ẩn
   ```typescript
   bg-gray-800/20 opacity-30 hover:opacity-50 cursor-pointer
   ```
   - ✅ Làm mờ đi (opacity: 30%)
   - ✅ Background nhạt hơn
   - ✅ Icon grayscale + opacity 50%
   - ✅ Text line-through + màu xám (#666)
   - ✅ Hover tăng opacity lên 50%
   - ✅ Click để show lại
   - ✅ **Luôn clickable** (không bao giờ disabled)

#### c. Visual feedback

**Icon:**
```typescript
<span className={`text-lg transition-all ${isHidden ? 'grayscale opacity-50' : ''}`}>
  {icons[entry.dataKey]}
</span>
```
- Hidden: grayscale + mờ 50%
- Active: màu gốc sáng

**Text:**
```typescript
<span 
  className={`text-sm font-semibold transition-all ${
    isHidden ? 'line-through opacity-50' : ''
  }`}
  style={{ color: isHidden ? '#666' : entry.color }}
>
  {entry.value}
</span>
```
- Hidden: gạch ngang + mờ + màu xám (#666)
- Active: màu theo series (green/orange/red)

#### d. Tooltip messages

```typescript
const tooltipText = descriptions[entry.dataKey] + 
  (isHidden ? ' (Click to show)' : ' (Click to hide)');
```

**Hover text mô tả:**
```typescript
<span className="text-xs text-gray-500 hidden group-hover:block">
  {descriptions[entry.dataKey]}
</span>
```

## Behavior Demo

### Scenario 1: Tất cả đang active (mặc định)
```
✅ Passed    ⚠️ Flaky    ❌ Failed
[Sáng]      [Sáng]      [Sáng]
```
- Chart hiển thị cả 3 series
- Click bất kỳ button nào → Làm mờ button đó và hide series

### Scenario 2: Click để hide
```
✅ Passed    ⚠️ Flaky    ❌ Failed
[Sáng]      [Mờ]        [Sáng]
```
- Click Flaky → Button làm mờ (opacity 30%)
- Chart chỉ hiển thị Passed & Failed
- Click Flaky lại → Button sáng lại và show series

### Scenario 3: Hide tất cả (cho phép)
```
✅ Passed    ⚠️ Flaky    ❌ Failed
[Mờ]        [Mờ]        [Mờ]
```
- Có thể hide tất cả 3 series
- Chart trống (nhưng không bị stuck)
- Click bất kỳ button mờ nào → Sáng lại và show series đó

### Scenario 4: Back lại trạng thái cũ
```
Bước 1: Hide Passed & Flaky
✅ Passed    ⚠️ Flaky    ❌ Failed
[Mờ]        [Mờ]        [Sáng]

Bước 2: Click Passed để show lại
✅ Passed    ⚠️ Flaky    ❌ Failed
[Sáng]      [Mờ]        [Sáng]

Bước 3: Click Flaky để show lại
✅ Passed    ⚠️ Flaky    ❌ Failed
[Sáng]      [Sáng]      [Sáng]
→ Back về trạng thái ban đầu!
```

## Testing

### Test Case 1: Simple Toggle ✅
1. Click Passed → Button mờ, series hidden
2. Click Passed lại → Button sáng, series show
3. Repeat → Toggle liên tục

### Test Case 2: Hide All ✅
1. Click Passed → Hide
2. Click Flaky → Hide  
3. Click Failed → Hide
4. Chart trống (tất cả buttons mờ)

### Test Case 3: Show Back (No Reload) ✅
1. Hide tất cả 3 buttons
2. Chart trống
3. Click Passed → Button sáng, chart show Passed
4. Click Flaky → Button sáng, chart show Passed + Flaky
5. Click Failed → Button sáng, chart show tất cả
6. **Đã back về trạng thái ban đầu - không cần reload!**

### Test Case 4: Visual Feedback ✅
1. Hidden button: opacity 30%, grayscale icon, line-through text, màu #666
2. Hover vào hidden button → opacity tăng lên 50%
3. Active button: opacity 100%, màu sáng, shadow, hover scale up
4. Tooltip: "(Click to hide)" hoặc "(Click to show)"

## Improvements

So với code cũ:

| Aspect | Cũ ❌ | Mới ✅ |
|--------|------|-------|
| Hide tất cả | Không được | **Được - tự do hoàn toàn** |
| Chart trống | Bị stuck | **Click để show lại** |
| Disabled state | Có (last active) | **Không có - luôn clickable** |
| Visual feedback | Opacity 40% | **Opacity 30% + grayscale + line-through** |
| Toggle | Có logic phức tạp | **Simple toggle - 1 click hide, 1 click show** |
| Back về trạng thái cũ | Phải reload | **Click buttons là xong** |
| Cursor | Có not-allowed | **Luôn pointer** |
| Ring highlight | Có (confusing) | **Không có (đơn giản hơn)** |
| Hover effect | Scale + opacity | **Scale cho active, opacity cho hidden** |

## Code Changes Summary

- **Lines 91-104:** Logic `handleLegendClick` đơn giản - simple toggle không ràng buộc
- **Lines 106-160:** UI `CustomLegend` với 2 trạng thái rõ ràng (Active/Hidden)
- **Removed:** Logic check "last active", disabled state, ring highlight
- **Simplified:** Tooltip chỉ có 2 trạng thái thay vì 3
- **No breaking changes** - backward compatible
- **No linter errors** ✅

## User Experience

### Before (Code cũ) ❌
- Phức tạp: Có logic "last active must visible"
- Button cuối cùng bị disabled → confusing
- Ring highlight → không rõ ý nghĩa
- Không thể hide tất cả → hạn chế

### After (Code mới) ✅
- **Đơn giản:** Click = toggle (hide/show)
- **Tự do:** Có thể hide/show bất kỳ button nào
- **Không bị stuck:** Chart trống → click button mờ để show lại
- **Không cần reload:** Tất cả thao tác bằng click
- **Visual feedback rõ ràng:** Mờ 30% + grayscale + line-through

---

**Status:** ✅ Fixed and tested  
**Files modified:** `frontend/components/dashboard/TrendChart.tsx`  
**No breaking changes**

