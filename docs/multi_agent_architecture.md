# PROPOSAL: COSMETICS CHATBOT ASSISTANT (Tư vấn son môi AI)

## 1. High-Level Architecture (Kiến trúc tổng quan)

Dự án sử dụng mô hình **Orchestrator-Workers (Nhạc trưởng - Nhạc công)** để quản lý luồng hội thoại phức tạp, kết hợp giữa tìm kiếm chính xác (SQL) và tìm kiếm ngữ nghĩa (Vector).

### Sơ đồ luồng dữ liệu (Data Flow)

```{mermaid}
graph TD
    User[User Interface] --> API[Backend API]
    API --> Router(🤖 ORCHESTRATOR / ROUTER)

    subgraph "Shared Memory (State)"
        State[Chat History + Context + Active Product IDs]
    end

    Router <--> State

    Router -- "Thiếu thông tin" --> AskUser[Hỏi lại User]
    AskUser --> User

    Router -- "Tiêu chí rõ ràng" --> AgentSQL(🤖 SEARCH AGENT)
    Router -- "Cảm xúc/Nhu cầu" --> AgentRAG(🤖 CONSULTANT AGENT)
    Router -- "Hỏi sâu về SP" --> AgentExpert(🤖 PRODUCT EXPERT)

    AgentSQL --> DB[(PostgreSQL)]
    AgentRAG --> DB
    AgentExpert --> DB

    AgentSQL & AgentRAG & AgentExpert --> Response[Tổng hợp câu trả lời] --> Router
```

Tuyệt vời. Đây là bản cập nhật đầy đủ cho file **`DESIGN.md`**.

Tôi đã lồng ghép chi tiết Database (ERD, SQL, Giải thích) mà bạn vừa cung cấp vào cấu trúc tổng thể, đồng thời thực hiện **2 điều chỉnh nhỏ** để khớp với phần ETL Script chúng ta vừa làm xong:

1. Đổi `highlights` từ `JSONB` sang **`TEXT`** (Vì script Python đã chuyển list thành chuỗi "Clean, Vegan...").
2. Thêm cột **`embedding vector(1536)`** vào bảng `products` (Bắt buộc cho tính năng AI Consultant).
3. Giữ lại 4 bảng về User/Order để đảm bảo hệ thống hoàn chỉnh (7 bảng).

Bạn hãy lưu nội dung dưới đây vào file `DESIGN.md` nhé:

---

# DESIGN DOCUMENT: COSMETICS CHATBOT ASSISTANT

## 1. High-Level Architecture (Kiến trúc tổng quan)

Dự án sử dụng mô hình **Orchestrator-Workers** để quản lý luồng hội thoại, kết hợp giữa tìm kiếm chính xác (SQL) và tìm kiếm ngữ nghĩa (Vector Search).

### Sơ đồ luồng dữ liệu (Data Flow)

Đoạn mã

```
graph TD
    User[User Interface] --> Router(🤖 ORCHESTRATOR)
    Router <--> State[Shared Memory]

    Router -- "Tiêu chí rõ ràng" --> AgentSQL(🤖 SEARCH AGENT)
    Router -- "Cảm xúc/Nhu cầu" --> AgentRAG(🤖 CONSULTANT AGENT)
    Router -- "Hỏi sâu SP" --> AgentExpert(🤖 PRODUCT EXPERT)

    AgentSQL & AgentRAG & AgentExpert --> DB[(PostgreSQL)]
    DB --> Response
```

---

## 2. Database Design (Thiết kế Cơ sở dữ liệu)

### 2.1. Mô hình Quan hệ (ERD Concept)

Chúng ta tách dữ liệu sản phẩm thành 3 bảng chính theo mô hình phân cấp:

- **Brands (Thương hiệu)** 1 ---- N **Products (Dòng son)**
- **Products (Dòng son)** 1 ---- N **Product Variants (Biến thể)**

> **Logic:** Một Thương hiệu có nhiều Dòng son. Một Dòng son có nhiều Màu sắc/Biến thể cụ thể.

### 2.2. Thiết kế chi tiết (Physical Schema)

Hệ thống sử dụng **PostgreSQL 15** với extension `pgvector`. Tổng cộng 7 bảng chia làm 3 domain.

#### A. Domain Sản phẩm (Product Catalog)

```
-- 1. Bảng Thương hiệu (Lookup Table)
-- Mục đích: Chuẩn hóa brand_name, tránh lặp lại text.
CREATE TABLE brands (
    brand_id SERIAL PRIMARY KEY,
    brand_name VARCHAR(255) UNIQUE NOT NULL
);

-- 2. Bảng Dòng sản phẩm (Master Data)
-- Chứa thông tin chung, TĨNH, không thay đổi theo màu sắc.
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY, -- ID gốc từ CSV
    brand_id INT REFERENCES brands(brand_id),
    product_name VARCHAR(255) NOT NULL,
    description TEXT, -- Context chính cho AI học
    ingredients TEXT,
    highlights TEXT,
    embedding vector(1536), -- Vector 1536 chiều (OpenAI) phục vụ Semantic Search
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Bảng Biến thể (Transactional/Inventory Data)
-- Chứa thông tin ĐỘNG, cụ thể từng thỏi son.
CREATE TABLE product_variants (
    uniq_id VARCHAR(50) PRIMARY KEY,
    product_id VARCHAR(50) REFERENCES products(product_id) ON DELETE CASCADE,
    color VARCHAR(255), -- Tên màu (Đã làm sạch dấu phẩy)
    size VARCHAR(50),
    price DECIMAL(10, 2), -- Dùng cho lọc giá (Filter)
    availability VARCHAR(50),
    primary_image_url TEXT,
    metadata JSONB
);
```

#### B. Domain Người dùng (User Context)

```
-- 4. Hồ sơ khách hàng
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    platform_user_id VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    skin_profile JSONB, -- Lưu: {"tone": "warm", "problem": "dry"}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Phiên hội thoại
CREATE TABLE chat_sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    current_intent VARCHAR(50),
    context_data JSONB -- Lưu giỏ hàng tạm, sản phẩm đang xem
);
```

#### C. Domain Giao dịch (Orders)

```
-- 6. Đơn hàng tổng
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    total_amount DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Chi tiết đơn hàng
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id),
    variant_id VARCHAR(50) REFERENCES product_variants(uniq_id),
    quantity INT DEFAULT 1,
    unit_price DECIMAL(10, 2)
);
```

### 2.3. Design Rationale (Tại sao thiết kế như vậy?)

#### A. Chuẩn hóa dữ liệu (Normalization - 3NF)

- **Vấn đề:** File CSV gốc lặp lại thông tin mô tả ("Mac Matte Lipstick") hàng trăm lần cho các màu khác nhau.
- **Giải pháp:** Tách ra bảng `products`.
- **Lợi ích:**
  - **Tiết kiệm dung lượng:** Mô tả dài (`description`, `ingredients`) chỉ lưu 1 lần duy nhất.
  - **Dễ bảo trì:** Sửa mô tả dòng son chỉ cần update 1 dòng thay vì update hàng loạt.

#### B. Tách biệt "Thông tin Tĩnh" và "Thông tin Động"

- **Bảng `products` (Tĩnh):** Đóng vai trò là **Knowledge Base**. AI dùng bảng này để trả lời các câu hỏi về kiến thức ("Son này có chì không?", "Công dụng là gì?").
- **Bảng `product_variants` (Động):** Đóng vai trò là **Inventory**. AI dùng bảng này để kiểm tra tồn kho, giá bán và màu sắc ("Màu đỏ còn hàng không?", "Giá bao nhiêu?").

---

## 3. Multi-Agent Design (Chi tiết các Agents)

Hệ thống bao gồm 4 Agents chuyên biệt:

### 🤖 1. The Orchestrator (Agent Điều phối)

- **Vai trò:** Quản lý, Gác cổng (Gatekeeper), Điều hướng.
- **Input:** Tin nhắn mới nhất + Lịch sử chat.
- **Nhiệm vụ chính:**
  1. **Intent Classification:** Xác định User muốn gì (Tìm kiếm, Tư vấn, hay Hỏi chi tiết?).
  2. **Slot Filling (Quan trọng):** Kiểm tra xem User đã cung cấp đủ thông tin chưa (Giá, Màu, Loại da...).
     - _Nếu thiếu:_ Sinh câu hỏi để khai thác thêm thông tin (Clarification Question).
     - _Nếu đủ:_ Chuyển tiếp sang Worker Agent.
  3. **State Management:** Cập nhật Context (ví dụ: User đang xem thỏi son nào) vào Shared State.

### 🤖 2. The Search Specialist (Agent Tìm kiếm)

- **Vai trò:** Tìm kiếm chính xác (Hard Filtering).
- **Kích hoạt khi:** User đưa ra tiêu chí cụ thể (Brand, Price range, Color name)
- **Công nghệ:** Text-to-SQL.
- **Logic:**
  - Input: `{"color": "red", "brand": "MAC", "price_max": 20}`
  - Action: `SELECT ... FROM product_variants ... WHERE ...`
  - Output: Danh sách sản phẩm khớp 100%.

### 🤖 3. The Consultant (Agent Tư vấn)

- **Vai trò:** Tư vấn theo ngữ nghĩa/cảm xúc (Semantic Search).
- **Kích hoạt khi:** User mô tả vấn đề (khô môi, thâm môi) hoặc hoàn cảnh (đi tiệc, đi làm, tặng quà).
- **Công nghệ:** Vector Search (Cosine Similarity).
- **Logic:**
  - Input: "Tìm son cho môi khô nứt nẻ"
  - Action: Embed query -> Search HNSW index trên bảng `products`.
  - Output: Top sản phẩm có thành phần dưỡng ẩm cao nhất.

### 🤖 4. The Product Expert (Agent Chi tiết)

- **Vai trò:** Trả lời sâu (Deep Dive) về sản phẩm.
- **Kích hoạt khi:** User hỏi về một sản phẩm **đã tìm thấy trước đó**.
- **Công nghệ:** Contextual RAG (Retrieval-Augmented Generation).
- **Logic:**
  - Input: "Thỏi này có chì không?" + `current_product_id` (từ Context).
  - Action: Lấy text `ingredients`, `description` của ID đó -> Đưa vào LLM để phân tích.
  - Output: Câu trả lời chi tiết (Yes/No/Explanation).

---

## 4. Use Cases & Edge Cases Coverage

### ✅ Main Use Cases (Luồng chính)

#### UC1: Direct Search (Tìm kiếm trực tiếp)

- **User:** "Tìm son đỏ hãng Revlon dưới 15 đô."
- **Flow:** Orchestrator -> **Search Agent** -> SQL Query -> Trả về list variants.

#### UC2: Advisory (Tư vấn nhu cầu)

- **User:** "Môi mình hay bị khô, tư vấn loại nào dùng hàng ngày."
- **Flow:** Orchestrator -> **Consultant Agent** -> Vector Search (tìm keyword "moisturizing", "hydrating") -> Trả về list products.

#### UC3: Product Detail (Hỏi chi tiết)

- **User:** (Sau khi bot gợi ý son A) "Cây này dùng có bị bóng không?"
- **Flow:** Orchestrator (nhận diện context là son A) -> **Product Expert** -> Đọc description của son A -> Trả lời.

#### UC4: Comparison (So sánh)

- **User:** "So sánh giá và độ lì của cây Revlon và cây MAC vừa rồi."
- **Flow:** Orchestrator -> **Product Expert** -> Lấy info cây Revlon + cây MAC -> LLM so sánh -> Trả bảng so sánh.

#### **UC5: Simple Purchase (Mua đơn giản)**

**User Flow:**

1. "Tôi muốn mua cây số 2" (sau khi xem recommend)
2. Bot: "Dạ để em thêm vào giỏ. Anh cần gì thêm không ạ?"
3. User: "Không, thanh toán luôn"
4. **→ Sales Agent kích hoạt**
5. Bot: "Dạ tổng cộng $25.99. Anh cho em tên và địa chỉ nhận hàng ạ?"
6. User: "Nguyễn Văn A, 123 Lê Lợi, Q1, TP.HCM"
7. Bot: "Đã đặt hàng thành công. Mã đơn #12345"

#### **UC6: Multi-item Purchase (Mua nhiều món)**

**User:** "Thêm cây số 1 và số 3 vào giỏ" **Handling:**

- Sales Agent parse ra 2 variant_ids
- Add vào `cart_items` trong STM
- Bot: "Đã thêm 2 sản phẩm. Tổng $48.5. Tiếp tục mua hay thanh toán ạ?"

#### **UC7: Modify Cart (Sửa giỏ hàng)**

**User:** "Bỏ cây số 1 đi, chỉ lấy cây số 3 thôi" **Handling:**

- Sales Agent remove item từ `cart_items`
- Tính lại tổng tiền
- Bot: "Đã xóa. Còn lại $25.99"

### ⚠️ Edge Cases (Luồng ngoại lệ)

#### EC1: Vague Input (Thiếu thông tin)

- **User:** "Tư vấn mua son tặng bạn gái."
- **Handling:**
  - Orchestrator phát hiện Intent = `ADVISE` nhưng thiếu `Budget`, `Style`.
  - **Action:** KHÔNG gọi Agent nào. Trả lời: _"Dạ anh dự kiến ngân sách bao nhiêu và bạn gái thích tông màu nào ạ?"_

#### EC2: Context Switching (Đổi ý giữa chừng)

- **User:** (Đang xem son đỏ) "À mà thôi, tìm cho mình kem dưỡng da đi."
- **Handling:**
  - Orchestrator phát hiện Intent mới hoàn toàn.
  - **Action:** Xóa `current_context`, Reset State, bắt đầu luồng tìm kiếm mới (hoặc báo là bot chỉ bán son).

#### EC3: No Results (Không tìm thấy)

- **Handling:**
  - Search Agent trả về 0 kết quả.
  - **Action:** Fallback sang Consultant Agent để tìm sản phẩm "tương tự" hoặc gợi ý User nới lỏng tiêu chí (ví dụ: "Không có son đỏ dưới 5 đô, nhưng có thỏi này 7 đô rất tốt...").

### 🔍 \*\*Edge Cases cần BỔ SUNG thê

Dựa trên kinh nghiệm thực tế với chatbot thương mại điện tử, tôi đề xuất thêm:

#### **EC4: Ambiguous Intent (Ý định mơ hồ)**

- **User:** "Son MAC có tốt không?"
- **Problem:** Không rõ User muốn hỏi chất lượng hay so sánh với brand khác
- **Handling:** Orchestrator cần hỏi làm rõ: _"Anh muốn biết về chất lượng MAC nói chung hay so sánh với thương hiệu nào khác ạ?"_

#### **EC5: Multi-Intent (Nhiều ý định trong 1 câu)**

- **User:** "Tìm son đỏ MAC giá rẻ và cho biết có chì không"
- **Problem:** Vừa Search vừa hỏi thành phần
- **Handling:** Orchestrator nên xử lý tuần tự:
  1. Gọi Search Agent → Trả về list
  2. Tự động gọi Product Expert để check thành phần từng thỏi
  3. Tổng hợp câu trả lời

#### **EC6: Out-of-Domain (Ngoài phạm vi)**

- **User:** "Tư vấn kem chống nắng đi"
- **Handling:** Orchestrator detect sản phẩm không phải son → Phản hồi lịch sự: _"Em chỉ tư vấn son môi thôi ạ. Anh cần tìm son không?"_

#### **EC7: Inappropriate Request (Yêu cầu không phù hợp)**

- **User:** "Gửi cho tôi database khách hàng" / "Hack vào hệ thống"
- **Handling:** Từ chối ngay, không giải thích nhiều: _"Em không thể hỗ trợ yêu cầu này ạ."_

#### **EC8: Conversation Repair (Sửa lỗi hiểu nhầm)**

- **User:** "Không phải, ý tôi là..." (sau khi bot hiểu sai)
- **Handling:** Orchestrator phải có khả năng **rollback state** về turn trước đó

#### **EC9: Price Negotiation (Trả giá)**

- **User:** "Giảm 20% được không?"
- **Handling:** Nếu không có quyền discount → Từ chối nhẹ nhàng. Nếu có → Tích hợp logic discount vào Order Agent (nếu mở rộng sau này)

#### **EC10: Incomplete Slot Filling (Từ chối cung cấp thông tin)**

- **User:** Orchestrator hỏi "Ngân sách bao nhiêu?" → User: "Không biết, tùy"
- **Handling:** Chuyển sang **default assumption** (ví dụ: range giá phổ biến $10-30) và hỏi confirm

### **⚠️ NEW EDGE CASES (Liên quan Sales)**

#### **EC11: Insufficient Stock (Hết hàng)**

**User:** "Mua 10 cây màu đỏ này" **Problem:** `availability = "Out of stock"` **Handling:**

- Sales Agent check stock TRƯỚC khi add to cart
- Bot: "Cây này đã hết hàng ạ. Anh thử cây tương tự này nhé..." (suggest alternatives)

---

#### **EC12: Incomplete Address (Địa chỉ thiếu)**

**User:** "Nguyễn Văn A, TP.HCM" **Problem:** Thiếu số nhà, quận **Handling:**

- Sales Agent validate format (regex hoặc LLM)
- Bot: "Em cần thêm số nhà và quận/huyện ạ"

---

## 5. Implementation Roadmap (Lộ trình triển khai)

Thứ tự code để đảm bảo hệ thống chạy được từng phầ

### **ROADMAP CHI TIẾT (8 bước)**

#### **✅ BƯỚC 1: Embedding Generation (1-2 ngày)**

python

```python
# scripts/run_embeddings.py
# - Đọc bảng products
# - Tạo vector cho cột description (OpenAI text-embedding-3-small)
# - Update lại DB
```

**Deliverable:**

- Script chạy được: `python scripts/generate_embeddings.py`
- Database có đủ 768 vectors cho tất cả products

---

#### **✅ BƯỚC 2: Service Layer (2-3 ngày)**

Code các service **KHÔNG có LLM**, chỉ xử lý data:

python

```python
# services/search_service.py
def filter_products(brand: str, price_max: float, color: str) -> List[Dict]:
    # SQL query logic

# services/vector_service.py
def semantic_search(query_text: str, top_k: int) -> List[Dict]:
    # Vector similarity search using pgvector

# services/product_service.py
def get_product_details(product_id: str) -> Dict:
    # Get full product + variants info
```

**Test:** Viết unit tests cho từng service

---

#### **✅ BƯỚC 3: Tools Layer (1 ngày)**

Wrap services thành tools cho Agents:

python

```python
# tools/search_tool.py
@tool
def search_products(filters: SearchFilters) -> str:
    results = search_service.filter_products(**filters)
    return json.dumps(results)
```

**Test:** Gọi thử từng tool độc lập

---

#### **✅ BƯỚC 4: Build SEARCH AGENT trước (2 ngày)**

**Lý do ưu tiên:**

- Đơn giản nhất (Text-to-SQL)
- Không cần vector search
- Test được ngay UC1

python

```python
# agents/search_agent.py
class SearchAgent(BaseAgent):
    def run(self, user_input: str, context: dict) -> dict:
        # Extract filters from user_input
        # Call search_tool
        # Return formatted results
```

**Test:** Input: "Tìm son đỏ MAC" → Output: List 5 products

---

#### **✅ BƯỚC 5: Build CONSULTANT AGENT (2-3 ngày)**

python

```python
# agents/consultant_agent.py
class ConsultantAgent(BaseAgent):
    def run(self, user_query: str, context: dict) -> dict:
        # Embed query
        # Call consultant_tool (vector search)
        # Return top recommendations
```

**Test:** Input: "Tư vấn son cho môi khô" → Output: Products có keywords "moisturizing"

---

#### **✅ BƯỚC 6: Build PRODUCT EXPERT AGENT (2 ngày)**

python

```python
# agents/expert_agent.py
class ExpertAgent(BaseAgent):
    def run(self, question: str, product_id: str) -> str:
        # Get product details
        # Use LLM to answer question based on description/ingredients
        # Return answer
```

**Test:** Input: "Thỏi A có chì không?" → Output: "Không, thành phần không chứa chì"

---

#### **✅ BƯỚC 7: Build ORCHESTRATOR (3-4 ngày - PHỨC TẠP NHẤT)**

python

```python
# agents/orchestrator.py + state/graph.py
# - Intent classification
# - Slot filling validation
# - Route to correct agent
# - Handle edge cases (EC1-EC10)
```

**Test:**

- UC1: Direct search flow
- UC2: Advisory flow
- EC1: Vague input handling
- EC5: Multi-intent handling

---

#### **✅ BƯỚC 8: API + Persistence (Memory) (2-3 ngày)**

Cực kỳ quan trọng để Agent "cắt đuôi" quên lãng và nhớ được khách hàng cũ.

```python
# services/chat_history_service.py
# - Load/Save session context từ DB (bảng chat_sessions)
# - Convert DB JSON -> LangChain Messages

# api/chat.py
@router.post("/chat")
async def chat(request: ChatRequest):
    # 1. Load context từ DB
    # 2. Run Graph (Orchestrator)
    # 3. Save response & new context xuống DB
    # 4. Return response
```

**Test:**

- Chat 1 câu, tắt Server, bật lại chat tiếp -> Agent vẫn nhớ câu trước.

---

#### **✅ BƯỚC 9: Build SALES AGENT (Nâng cao - 2 ngày)**

Chuyên trách việc chốt đơn như user yêu cầu.

```python
# agents/sales_agent.py
# - Xác nhận sản phẩm user muốn mua
# - Hỏi địa chỉ, SĐT (Slot Filling)
# - Tính tổng tiền
# - Tạo Order vào DB (bảng orders)
```

**Test:** Quy trình chốt đơn trọn vẹn từ "Mua thỏi này" -> "Đơn hàng #123 đã tạo".
