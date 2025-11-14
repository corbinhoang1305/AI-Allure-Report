# 🔍 PHÂN TÍCH CHỨC NĂNG ROOT CAUSE ANALYSIS (RCA)

## 📋 TỔNG QUAN

**Root Cause Analysis (RCA)** là một chức năng AI-powered quan trọng trong hệ thống QUALIFY.AI, tự động phân tích các test failures để xác định nguyên nhân gốc rễ và đưa ra các khuyến nghị khắc phục.

---

## 🏗️ KIẾN TRÚC VÀ CÁC THÀNH PHẦN

### 1. **Backend Components**

#### 1.1. RootCauseAnalyzer Class (`backend/services/ai-analysis-service/app/analyzers/rca.py`)

**Chức năng chính:**
- Phân tích test failures sử dụng OpenAI API
- So sánh với historical failures để tìm patterns
- Tạo executive summaries cho management

**Các phương thức:**

```python
async def analyze_failure(
    test_name: str,
    error_message: str,
    stack_trace: str,
    test_description: str = "",
    historical_failures: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]
```

**Input:**
- `test_name`: Tên test case
- `error_message`: Thông báo lỗi từ test failure
- `stack_trace`: Full stack trace
- `test_description`: Mô tả test (optional)
- `historical_failures`: Danh sách các failures trước đó của cùng test

**Output:**
```json
{
    "root_cause": "detailed explanation",
    "confidence": 85,
    "category": "Code Bug",
    "similar_patterns": ["pattern1", "pattern2"],
    "recommended_actions": ["action1", "action2", "action3"],
    "technical_details": "deeper technical analysis",
    "analysis_model": "gpt-4",
    "tokens_used": 1234
}
```

#### 1.2. API Endpoint (`backend/services/ai-analysis-service/app/main.py`)

**Endpoint:** `POST /api/ai/analyze/rca`

**Request:**
```json
{
    "test_result_id": "uuid"
}
```

**Luồng xử lý:**
1. Lấy test result từ database
2. Query historical failures (5 failures gần nhất của cùng test)
3. Gọi `RootCauseAnalyzer.analyze_failure()`
4. Lưu kết quả vào `ai_analyses` table
5. Return analysis result

#### 1.3. Database Schema (`backend/shared/models.py`)

**Table: `ai_analyses`**
```python
class AIAnalysis(Base):
    id: UUID
    test_result_id: UUID (FK -> test_results)
    analysis_type: Enum (ROOT_CAUSE, FLAKY_DETECTION, etc.)
    result: JSONB  # Full analysis result
    confidence: Float (0.0 - 1.0)
    prompt_used: Text
    model_used: String
    similar_issues: JSONB
    created_at: DateTime
```

---

## 🔄 LUỒNG XỬ LÝ CHI TIẾT

### **Step 1: Trigger Analysis**
```
User clicks "Analyze Root Cause" on failed test
    ↓
Frontend calls: POST /api/ai/analyze/rca
    ↓
Backend receives request with test_result_id
```

### **Step 2: Data Collection**
```
Backend queries database:
    ↓
1. Get test_result by ID
   - test_name
   - error_message
   - error_trace (stack trace)
   - description
   - history_id
    ↓
2. Get historical failures
   - Query test_results WHERE history_id = same
   - Filter: status IN ('failed', 'broken')
   - Order by: created_at DESC
   - Limit: 5 failures
    ↓
3. Prepare historical context
   - Format: Date, Error message (truncated)
```

### **Step 3: AI Analysis**
```
RootCauseAnalyzer.analyze_failure():
    ↓
1. Prepare prompt template với:
   - Test information
   - Failure details (error + stack trace)
   - Historical context
    ↓
2. Call OpenAI API:
   - Model: gpt-4 (configurable)
   - Temperature: 0.7 (configurable)
   - Response format: JSON
   - System prompt: "Expert QA engineer"
    ↓
3. Parse JSON response:
   - root_cause
   - confidence
   - category
   - similar_patterns
   - recommended_actions
   - technical_details
```

### **Step 4: Store Results**
```
Create AIAnalysis record:
    ↓
- test_result_id
- analysis_type: ROOT_CAUSE
- result: Full JSON analysis
- confidence: 0.0 - 1.0
- model_used: "gpt-4"
- prompt_used: "RCA analysis prompt"
    ↓
Save to database
    ↓
Return to frontend
```

---

## 📊 CÁC LOẠI PHÂN TÍCH

### **1. Root Cause Identification**
AI phân tích để xác định nguyên nhân gốc rễ:
- **Code Bug**: Lỗi logic trong code
- **Infrastructure**: Vấn đề về môi trường, network, database
- **Test Flakiness**: Test không ổn định
- **Configuration**: Cấu hình sai
- **Data Issue**: Dữ liệu test không đúng

### **2. Confidence Level**
- **0-100%**: Mức độ tin cậy của phân tích
- Dựa trên:
  - Độ rõ ràng của error message
  - Stack trace có đầy đủ không
  - Historical patterns có match không

### **3. Similar Patterns**
So sánh với historical failures để tìm:
- Cùng error message
- Cùng stack trace pattern
- Cùng test case đã fail trước đó
- Similarity score > 70%

### **4. Recommended Actions**
AI đưa ra các bước cụ thể để fix:
- Ví dụ: "Check database connection", "Verify API endpoint", etc.

---

## 🎯 PROMPT ENGINEERING

### **System Prompt:**
```
"You are an expert QA engineer specializing in root cause analysis."
```

### **User Prompt Template:**
```
Test Information:
- Test Name: {test_name}
- Description: {test_description}

Failure Details:
- Error Message: {error_message}
- Stack Trace: 
{stack_trace}

Historical Context:
{historical_context}

Please analyze this test failure and provide:
1. Root Cause: The most likely underlying issue causing the failure
2. Confidence Level: Your confidence in this analysis (0-100%)
3. Similar Issues: Any patterns matching known issues
4. Recommended Actions: Specific steps to resolve the issue
5. Category: Classify as (Infrastructure/Code Bug/Test Flakiness/Configuration/Data Issue)

Provide your analysis in JSON format:
{
    "root_cause": "detailed explanation",
    "confidence": 85,
    "category": "category name",
    "similar_patterns": ["pattern1", "pattern2"],
    "recommended_actions": ["action1", "action2", "action3"],
    "technical_details": "deeper technical analysis"
}
```

---

## ✅ ĐIỂM MẠNH

1. **Tự động hóa**: Không cần manual analysis
2. **Historical Context**: Sử dụng dữ liệu lịch sử để cải thiện độ chính xác
3. **Structured Output**: JSON format dễ parse và hiển thị
4. **Confidence Score**: Giúp đánh giá độ tin cậy
5. **Category Classification**: Phân loại giúp prioritize fixes
6. **Similar Pattern Detection**: Tìm các failures tương tự
7. **Actionable Recommendations**: Đưa ra các bước cụ thể để fix

---

## ⚠️ ĐIỂM YẾU VÀ HẠN CHẾ

### **1. Phụ thuộc vào OpenAI API**
- Cần API key và có chi phí
- Có thể bị rate limit
- Cần internet connection

### **2. Chất lượng phụ thuộc vào dữ liệu đầu vào**
- Error message không rõ ràng → phân tích kém
- Stack trace thiếu → confidence thấp
- Không có historical data → mất context

### **3. Similarity Detection đơn giản**
```python
def _calculate_similarity(...) -> float:
    # Simple word overlap similarity
    # Chưa dùng embeddings hoặc advanced NLP
```
- Chỉ dùng word overlap, chưa dùng semantic similarity
- Có thể miss các patterns tương tự nhưng khác cách diễn đạt

### **4. Chưa tích hợp với Frontend**
- Backend đã có nhưng frontend chưa có UI
- Chưa có button "Analyze Root Cause" trong TestDetailsDialog
- Chưa hiển thị RCA results

### **5. Batch Analysis chưa tối ưu**
- `analyze_batch()` gọi tuần tự từng test
- Chưa parallel processing
- Có thể chậm với nhiều tests

### **6. Chưa có Caching**
- Mỗi lần analyze lại gọi API
- Không cache kết quả cho cùng test failure
- Tốn chi phí và thời gian

---

## 🚀 ĐỀ XUẤT CẢI THIỆN

### **1. Frontend Integration**

#### **A. Thêm RCA Button vào TestDetailsDialog**
```typescript
// Trong TestDetailsDialog.tsx
{isFailed && (
  <Button
    onClick={handleAnalyzeRCA}
    disabled={analyzing}
    className="bg-qualify-teal"
  >
    {analyzing ? 'Analyzing...' : 'Analyze Root Cause'}
  </Button>
)}
```

#### **B. Hiển thị RCA Results**
```typescript
// Component mới: RCAResults.tsx
interface RCAResultsProps {
  analysis: {
    root_cause: string;
    confidence: number;
    category: string;
    similar_patterns: string[];
    recommended_actions: string[];
    technical_details: string;
  };
}
```

#### **C. RCA Panel trong Dashboard**
- Hiển thị top failed tests đã được analyze
- Show confidence scores
- Quick actions để fix

### **2. Cải thiện Similarity Detection**

#### **A. Sử dụng Embeddings**
```python
from openai import Embeddings

def _calculate_similarity_with_embeddings(error1, trace1, error2, trace2):
    # Generate embeddings
    emb1 = get_embedding(error1 + trace1)
    emb2 = get_embedding(error2 + trace2)
    
    # Cosine similarity
    return cosine_similarity(emb1, emb2)
```

#### **B. Pattern Extraction**
- Extract common patterns từ stack traces
- Classify error types (NullPointerException, TimeoutError, etc.)
- Match patterns thay vì chỉ text similarity

### **3. Caching Strategy**

#### **A. Cache Analysis Results**
```python
# Redis cache
cache_key = f"rca:{test_result_id}:{error_hash}"
cached_result = await redis.get(cache_key)

if cached_result:
    return json.loads(cached_result)

# Analyze and cache
result = await analyze_failure(...)
await redis.setex(cache_key, 3600, json.dumps(result))  # 1 hour TTL
```

#### **B. Smart Caching**
- Cache dựa trên error message hash
- Nếu cùng error → reuse analysis
- Invalidate khi test code thay đổi

### **4. Batch Processing Optimization**

#### **A. Parallel Processing**
```python
import asyncio

async def analyze_batch_parallel(failures: List[Dict]):
    tasks = [
        analyze_failure(**failure) 
        for failure in failures
    ]
    return await asyncio.gather(*tasks)
```

#### **B. Rate Limiting**
- Implement rate limiting cho OpenAI API
- Queue system cho batch requests
- Retry logic với exponential backoff

### **5. Enhanced Prompt Engineering**

#### **A. Few-shot Learning**
```python
prompt_template = """
Here are examples of good RCA analyses:

Example 1:
Test: test_user_login
Error: ConnectionTimeout
Root Cause: Database connection pool exhausted
Category: Infrastructure
Confidence: 90%

Example 2:
...

Now analyze this failure:
{test_info}
"""
```

#### **B. Domain-specific Prompts**
- Different prompts cho different test types (API, UI, Integration)
- Include domain knowledge (e.g., common API errors)

### **6. Integration với External Systems**

#### **A. JIRA Integration**
```python
# Auto-create JIRA ticket với RCA results
jira_ticket = {
    "summary": f"Test Failure: {test_name}",
    "description": analysis["root_cause"],
    "labels": [analysis["category"]],
    "priority": calculate_priority(analysis["confidence"])
}
```

#### **B. Slack/Teams Notifications**
- Auto-notify team khi có high-confidence RCA
- Include recommended actions

### **7. Analytics & Reporting**

#### **A. RCA Accuracy Tracking**
```python
# Track khi developer confirms RCA
class RCAAccuracy:
    analysis_id: UUID
    confirmed_by: UUID (user_id)
    was_correct: bool
    actual_root_cause: str (if different)
```

#### **B. RCA Dashboard**
- Success rate của RCA analyses
- Most common root causes
- Average time to fix based on RCA

---

## 📈 METRICS & MONITORING

### **Key Metrics:**
1. **Analysis Success Rate**: % analyses completed successfully
2. **Average Confidence**: Mean confidence score
3. **Category Distribution**: Breakdown by category
4. **API Cost**: Tokens used per analysis
5. **Response Time**: Time to complete analysis
6. **Cache Hit Rate**: % requests served from cache

### **Monitoring:**
- Track OpenAI API errors
- Monitor rate limits
- Alert khi confidence thấp (< 50%)
- Track analysis accuracy (nếu có feedback)

---

## 🔧 CONFIGURATION

### **Environment Variables:**
```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
RCA_CACHE_TTL=3600
RCA_MAX_HISTORICAL_FAILURES=5
RCA_SIMILARITY_THRESHOLD=0.7
```

### **Tunable Parameters:**
- `temperature`: 0.0-1.0 (lower = more deterministic)
- `max_historical_failures`: Số failures để analyze (default: 5)
- `similarity_threshold`: Threshold để match similar failures (default: 0.7)
- `cache_ttl`: Thời gian cache (seconds)

---

## 📝 VÍ DỤ SỬ DỤNG

### **Example 1: Simple Failure**
```json
Input:
{
    "test_name": "test_user_login",
    "error_message": "ConnectionTimeout: Unable to connect to database",
    "stack_trace": "at Database.connect()...",
    "historical_failures": []
}

Output:
{
    "root_cause": "Database connection timeout indicates infrastructure issue. Possible causes: database server down, network issues, or connection pool exhausted.",
    "confidence": 85,
    "category": "Infrastructure",
    "similar_patterns": [],
    "recommended_actions": [
        "Check database server status",
        "Verify network connectivity",
        "Review connection pool configuration",
        "Check database logs for errors"
    ],
    "technical_details": "ConnectionTimeout typically occurs when the database server is unreachable or overloaded..."
}
```

### **Example 2: With Historical Context**
```json
Input:
{
    "test_name": "test_checkout_process",
    "error_message": "AssertionError: Expected total $100 but got $105",
    "stack_trace": "...",
    "historical_failures": [
        {
            "date": "2024-01-15",
            "error_message": "AssertionError: Expected total $50 but got $55"
        }
    ]
}

Output:
{
    "root_cause": "Price calculation error appears to be recurring. This test has failed with similar price discrepancies before (Jan 15). Likely a bug in the pricing calculation logic or tax computation.",
    "confidence": 92,
    "category": "Code Bug",
    "similar_patterns": [
        "Previous failure on 2024-01-15 with similar price mismatch"
    ],
    "recommended_actions": [
        "Review pricing calculation code",
        "Check tax computation logic",
        "Verify test data consistency",
        "Compare with previous failure to identify pattern"
    ]
}
```

---

## 🎓 KẾT LUẬN

Root Cause Analysis là một chức năng mạnh mẽ nhưng cần:

1. **✅ Hoàn thiện Frontend Integration**: Thêm UI để trigger và hiển thị RCA
2. **✅ Cải thiện Similarity Detection**: Dùng embeddings thay vì word overlap
3. **✅ Implement Caching**: Giảm chi phí và tăng tốc độ
4. **✅ Batch Optimization**: Parallel processing cho nhiều tests
5. **✅ Enhanced Monitoring**: Track accuracy và success rate

Với những cải thiện này, RCA sẽ trở thành một công cụ cực kỳ hữu ích cho QA teams để nhanh chóng identify và fix test failures.

