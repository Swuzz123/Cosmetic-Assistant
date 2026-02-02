### 1. 🔍 Direct Search & Filtering (Tìm kiếm chính xác)

Đây là use case bạn đã biết. Khách hàng đã biết họ muốn gì, họ chỉ cần tìm đúng sản phẩm đó.

- **Câu hỏi mẫu:** _"Tìm cho tôi son hãng Revlon màu đỏ", "Son nào giá dưới 10 đô?", "Shop có bán son lì (Matte) không?"_
- **Kỹ thuật xử lý:** Dùng **SQL Query** thuần túy vào Database.
- **Dữ liệu dùng:** `brand_name`, `color`, `price`, `product_name`.

### 2. 💡 Contextual Recommendation (Gợi ý theo ngữ cảnh/nhu cầu)

Đây là use case bạn cũng đã nhắc tới. Khách hàng không biết mua gì, họ đưa ra một vấn đề hoặc mong muốn trừu tượng.

- **Câu hỏi mẫu:** _"Môi mình hay bị khô nứt nẻ thì dùng loại nào?", "Sắp đi tiệc cưới buổi tối, tư vấn màu nào sang chảnh chút?", "Tìm loại son nào ăn uống không trôi."_
- **Kỹ thuật xử lý:** Dùng **Vector Search (Semantic Search)**. AI sẽ hiểu "khô nứt nẻ" tương đồng với "moisturizing", "hydrating" trong cột `description`.
- **Dữ liệu dùng:** `description`, `highlights`, `ingredients`.

---

### 👉 3. 🧠 Product Understanding & Q/A (Hỏi đáp thông tin sản phẩm) - _Use Case Mới_

Đây là use case cực kỳ quan trọng để "chốt sale". Sau khi tìm được sản phẩm, khách hàng sẽ soi kỹ và hỏi chi tiết về sản phẩm đó. Đây không phải là tìm kiếm sản phẩm mới, mà là **đào sâu thông tin**.

- **Câu hỏi mẫu:**
  - _"Thỏi Revlon này có chì không?"_ (Check `ingredients`)
  - _"Son này là thuần chay (Vegan) hả?"_ (Check `highlights`)
  - _"Cách đánh son này sao cho đẹp?"_ (Check `how_to_use`)
  - _"Chất son này lên môi có bị bóng không hay là lì?"_ (Check `description`)
- **Tại sao cần tách riêng?** Vì lúc này context cuộc hội thoại đang dính vào **1 sản phẩm cụ thể**. Bạn không cần search lại toàn bộ database, mà chỉ cần query thông tin của đúng `product_id` đó để trả lời.

### 👉 4. ⚖️ Comparison (So sánh) - _Use Case Nâng cao_

Khách hàng phân vân giữa 2-3 lựa chọn. Chatbot cần có khả năng so sánh để giúp khách ra quyết định.

- **Câu hỏi mẫu:**
  - _"So sánh thỏi MAC với thỏi Revlon kia, cái nào rẻ hơn?"_
  - _"Giữa dòng Matte và Satin của hãng này thì dòng nào dưỡng nhiều hơn?"_
- **Kỹ thuật xử lý:** Lấy thông tin của 2 `product_id`, so sánh các trường tương ứng (`price` vs `price`, `description` vs `description`) và nhờ LLM (Gemini/GPT) tổng hợp sự khác biệt.

---

### Phần 1: Case nào cần Embedding (Vector)? Case nào không?

Trong 4 use cases mình đề xuất, thực tế chỉ có **Case 2** là bắt buộc phải dùng Embedding mạnh mẽ nhất. Các case còn lại thiên về Logic và SQL.

| **Use Case**                                               | **Embedding (Vector)?** | **Công nghệ chính**                                                       | **Lý do**                                                                                                                                                                            |
| ---------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **1. Find Product**<br><br> <br><br>_(Tìm kiếm chính xác)_ | **KHÔNG**               | **SQL Query**<br><br> <br><br>(`WHERE price < 20`, `WHERE color = 'red'`) | Khi khách nói "giá dưới 20 đô", đó là con số chính xác. Vector search (tìm kiếm tương đồng) có thể trả về giá 21 đô hoặc 19 đô lung tung. SQL chính xác tuyệt đối.                   |
| **2. Advise Product**<br><br> <br><br>_(Tư vấn/Gợi ý)_     | **CÓ (Rất cần)**        | **Vector Search**<br><br> <br><br>(Cosine Similarity)                     | Khách nói "môi khô nứt nẻ". SQL không thể `WHERE description = 'môi khô'`, nhưng Vector hiểu "nứt nẻ" gần nghĩa với "hydrating", "moisturizing" trong vector space.                  |
| **3. Get Info**<br><br> <br><br>_(Hỏi sâu về SP)_          | **KHÔNG** (Hoặc ít)     | **SQL + LLM (RAG)**                                                       | Khi khách hỏi về 1 sản phẩm cụ thể, bạn đã có ID. Chỉ cần dùng SQL lấy toàn bộ text `description` của ID đó quăng cho LLM đọc và trả lời. Text ngắn nên không cần Vector để cắt nhỏ. |
| **4. Compare**<br><br> <br><br>_(So sánh)_                 | **KHÔNG**               | **SQL + LLM**                                                             | Bạn query thông tin của 2 sản phẩm A và B bằng SQL, sau đó đưa dữ liệu thô cho LLM và bảo nó: "Hãy so sánh 2 cái này".                                                               |

Đây là câu hỏi đi vào trọng tâm của việc thiết kế hệ thống (System Design). Để chatbot không bị "ngáo" (trả lời râu ông nọ cắm cằm bà kia), bạn cần phân định rạch ròi công nghệ cho từng case và xây dựng một **"Bộ điều hướng" (Router)** thông minh.

---

### Phần 2: Làm sao để Chatbot hiểu (Intent Recognition & Routing)?

Để chatbot biết khách đang muốn gì (Tìm, Gợi ý, hay Hỏi sâu), bạn cần một bước ở giữa gọi là **"Intent Classification" (Phân loại ý định)**.

Mô hình luồng xử lý (Flow) sẽ đi như sau:

#### Bước 1: The Brain (Router) - Bộ não điều hướng

Khi User nhập liệu, **đừng vội tìm kiếm ngay**. Hãy gửi câu đó cho một con AI nhỏ (ví dụ GPT-4o-mini hoặc model classification nhẹ) kèm theo lịch sử chat, và yêu cầu nó phân loại.

**Prompt cho Router:**

> "Bạn là một AI Router. Dựa vào câu nói mới nhất của khách và lịch sử chat, hãy xác định Intent (ý định) là gì trong 4 loại sau:
>
> 1. **FIND_FILTER**: Khách muốn tìm theo tiêu chí cụ thể (màu, giá, hãng).
> 2. **ADVISE**: Khách mô tả vấn đề/cảm xúc, cần lời khuyên (môi khô, đi tiệc, sang trọng).
> 3. **GET_DETAILS**: Khách hỏi chi tiết về sản phẩm **đang được nhắc đến** (có chì không? dùng sao?).
> 4. **COMPARE**: Khách muốn so sánh 2 sản phẩm.
>
> Trả về JSON: `{ "intent": "...", "entities": {...} }`"

#### Bước 2: Xử lý theo từng nhánh (The Flow)

Đây là cách hệ thống xử lý logic để hiểu "đào sâu":

**Kịch bản 1: Khách mới vào -> Gợi ý (Advise)**

- **User:** "Tư vấn cho mình son nào hợp đi tiệc tối, môi mình hơi khô."
- **Router:** Phát hiện Intent = `ADVISE`.
- **Action:**
  1. Chuyển câu nói thành Vector.
  2. Search trong Database (cột `embedding`).
  3. Lấy ra Top 3 sản phẩm.
  4. **QUAN TRỌNG:** Lưu danh sách ID của 3 sản phẩm này vào **Session Memory (Bộ nhớ phiên)**. Ví dụ: `current_context_ids = [101, 102, 103]`.

**Kịch bản 2: Khách "đào sâu" (Deep Dive)**

- **User:** "Cái thứ 2 giá bao nhiêu? Nó có bền màu không?"
- **Router:**
  - Đọc lịch sử -> Thấy bot vừa gợi ý 3 cái.
  - User nói "Cái thứ 2" -> Router hiểu là ID `102` trong `current_context_ids`.
  - Câu hỏi "bền màu không" -> Intent = `GET_DETAILS`.
- **Action:**
  1. Không search lại database.
  2. Dùng SQL query thẳng vào ID `102`.
  3. Lấy thông tin `price` và `description`.
  4. Trả lời user.

**Kịch bản 3: Khách đổi ý -> Tìm kiếm (Search)**

- **User:** "Thôi mắc quá. Tìm cho mình con nào của Revlon dưới 10 đô đi."
- **Router:** Phát hiện từ khóa "Revlon" (Brand), "dưới 10 đô" (Price), "tìm" -> Intent = `FIND_FILTER`.
- **Action:**
  1. Tạo câu lệnh SQL: `SELECT * FROM variants JOIN products ... WHERE brand='Revlon' AND price < 10`.
  2. Reset lại `current_context_ids` bằng danh sách mới tìm được.

---

Đây là mô hình **chuẩn công nghiệp** hiện nay (được LangChain/LangGraph khuyến nghị) để đảm bảo độ chính xác (Reliability) và kiểm soát luồng đi (Control Flow).

Dưới đây là thiết kế chi tiết:

### 1. Kiến trúc tổng quan: The Orchestrator Pattern

Bạn không nên để các Agent tự tranh giành input. Bạn cần một **Supervisor (Router)** đứng đầu.

- **Supervisor (Router Agent):** Nhận input của User, quyết định xem "Việc này của ai?" và chuyển giao nhiệm vụ.
- **Specialized Agents (Workers):** Mỗi Agent chỉ giỏi đúng 1 việc, làm xong trả kết quả về cho Supervisor hoặc trả thẳng cho User.

### 2. Chi tiết các Agent (Dựa trên 4 use cases đã bàn)

Tôi đề xuất bạn xây dựng 3 Agent chuyên biệt:

#### 🤖 1. The Searching Agent (SQL Specialist)

- **Nhiệm vụ:** Tìm kiếm sản phẩm khi khách hàng có tiêu chí rõ ràng (Hard constraints).
- **Input:** JSON chứa các filter (`color='red'`, `brand='revlon'`, `price<15`).
- **Tool:** Có khả năng thực thi câu lệnh SQL (Text-to-SQL) trên bảng `product_variants`.
- **Ví dụ:** "Tìm son đỏ hãng Mac" -> Agent này nhảy vào làm.

#### 🤖 2. The Consultant Agent (RAG/Vector Specialist)

- **Nhiệm vụ:** Tư vấn khi khách hàng nói chung chung, dựa trên cảm xúc hoặc vấn đề.
- **Input:** Câu query ngữ nghĩa (`query='môi khô nứt nẻ'`).
- **Tool:** Vector Search trên bảng `products` (cột `embedding`).
- **Ví dụ:** "Môi mình khô quá dùng gì?" -> Agent này xử lý.

#### 🤖 3. The Product Expert (Detail & Comparison)

- **Nhiệm vụ:** Trả lời chi tiết về 1 sản phẩm cụ thể hoặc so sánh. Agent này cần "Context" (sản phẩm nào đang được nói tới).
- **Input:** `product_id` và câu hỏi (`question='có chì không?'`).
- **Tool:** SQL Query vào bảng `products` (lấy `description`, `ingredients`, `how_to_use`).
- **Ví dụ:** "Thỏi đó có chì không?" -> Agent này xử lý.

---

### 3. Luồng xử lý (Workflow) - Tuần tự hay Song song?

Bạn hỏi: _"Gửi đến các agent xử lý song song nhỉ?"_ 👉 **Câu trả lời là: Thường là KHÔNG.** Trong hội thoại chat, 95% trường hợp là xử lý **Tuần tự (Sequential)**.

Tại sao? Vì User thường chỉ có 1 ý định chính tại 1 thời điểm.

- Nếu User hỏi: _"Tìm son đỏ và cho biết cách dùng"_.
- Bạn **không nên** để Agent Search và Agent Detail chạy song song. Vì Agent Detail **cần kết quả** của Agent Search (cần biết là thỏi son nào) mới trả lời cách dùng được.

**Mô hình luồng đi chuẩn (State Graph):**

Đoạn mã

```
graph TD
    A[User Input] --> B(Router / Supervisor)
    B -- Intent: FIND --> C[Searching Agent]
    B -- Intent: ADVISE --> D[Consultant Agent]
    B -- Intent: DETAIL --> E[Product Expert]

    C --> F{Có kết quả?}
    D --> F

    F -- Yes (Lưu ID vào Memory) --> G[Generate Answer]
    E --> G
```

---

Đúng là về mặt kiến trúc cơ bản, chúng ta có **4 Agents** (1 Orchestrator + 3 Workers).

Tuy nhiên, với case **"Thông tin chung chung/thiếu dữ liệu"** (Vague Input) mà bạn vừa nêu, chúng ta **không cần tạo ra Agent thứ 5**, mà sẽ nâng cấp trí thông minh của thằng **Orchestrator (Router)**.

Kỹ thuật này trong AI gọi là **"Slot Filling" (Điền vào chỗ trống)** hoặc **"Clarification Loop" (Vòng lặp làm rõ)**.

Hãy cùng xem cách xử lý tối ưu nhất:

### 1. Tại sao không nên dùng Agent riêng cho việc hỏi lại?

Nếu bạn tạo một agent riêng chỉ để hỏi lại, luồng đi sẽ bị dài và tăng độ trễ:

- _User -> Orchestrator -> Clarification Agent -> (Sinh câu hỏi) -> Orchestrator -> User._

Thay vào đó, **Orchestrator** nên là người quyết định việc này ngay từ đầu.

### 2. Nâng cấp luồng xử lý của Orchestrator

Nhiệm vụ của Orchestrator không chỉ là "Chia việc" mà còn là **"Gác cổng" (Gatekeeper)**.

**Logic mới của Orchestrator:**

1. Nhận Input.
2. Phân tích Intent.
3. **Check "Đủ thông tin chưa?":**
   - Nếu Intent là `ADVISE` (Tư vấn), nó cần tối thiểu các trường: `Budget` (Ngân sách), `Tone` (Tông màu), hoặc `Skin_Type` (Loại da/môi).
   - Nếu thiếu $\rightarrow$ **Không gọi Worker Agent nào cả**. Trả về luôn câu hỏi cho User.
   - Nếu đủ $\rightarrow$ Gọi `Consultant Agent`.

### 3. Ví dụ luồng chạy (State Flow)

**Kịch bản: Khách nhắn "Tư vấn quà sinh nhật cho bạn gái"**

1. **User:** "Tư vấn quà sinh nhật cho bạn gái."
2. **Orchestrator (Router):**
   - Phân tích: Intent = `ADVISE`.
   - Check thông tin:
     - `Price`: Missing ❌
     - `Style/Color`: Missing ❌
     - `Brand`: Missing ❌
   - Decision: **MISSING_INFO**.

3. **Orchestrator Action:** Sinh câu hỏi gợi mở (dựa trên các trường bị thiếu).
   - _Output:_ "Dạ để em chọn món quà ưng ý nhất, anh có thể bật mí xíu là bạn gái mình hay dùng tông màu nào (đỏ, cam, hồng) hoặc anh dự kiến ngân sách khoảng bao nhiêu không ạ?"

4. **User:** "Khoảng 500k đổ lại, màu đỏ cam nhé."
5. **Orchestrator (Lần 2):**
   - Cập nhật State: `Price < 500k`, `Color = Red/Orange`.
   - Decision: **SUFFICIENT (Đủ)**.
   - Action: Gọi `Searching Agent` (hoặc Consultant Agent).

### 4. Thiết kế Prompt cho Orchestrator

Để làm được điều này, bạn cần viết Prompt cho Orchestrator Agent khéo léo một chút. Đây là mẫu Prompt (System Instruction):

> **Role:** Bạn là AI điều phối viên cho shop son môi.
>
> **Task:** Phân tích câu nói của khách hàng và quyết định bước tiếp theo.
>
> **Rules:**
>
> 1. Nếu khách hàng muốn tìm/tư vấn nhưng thông tin quá sơ sài (thiếu màu sắc, mức giá, hoặc vấn đề cụ thể), hãy trả về status `ASK_MORE` kèm theo một câu hỏi ngắn gọn, lịch sự, thân thiện để khai thác thêm thông tin. **Đừng đoán mò.**
> 2. Nếu thông tin đã đủ rõ ràng, hãy chọn Agent phù hợp (`SEARCH`, `ADVISE`, `DETAIL`) để xử lý.
>
> **Example 1:**
>
> - Input: "Tối nay đi tiệc dùng son gì?"
> - Output: `{ "action": "ASK_MORE", "response": "Dạ tiệc tối thì mình nên dùng màu nổi bật chút ạ. Chị mặc váy màu gì hoặc chị thích chất son lì hay bóng để em tìm cho chuẩn nhé?" }`
>
> **Example 2:**
>
> - Input: "Tìm son đỏ dưới 200k."
> - Output: `{ "action": "SEARCH_AGENT", "params": { "color": "red", "price_max": 200 } }`

### 5. Cập nhật Sơ đồ hệ thống

Lúc này sơ đồ của bạn sẽ có một "đường tắt" (Short-circuit):

Đoạn mã

```
graph TD
    UserInput --> Router{Phân tích}

    Router -- Thiếu thông tin --> AskUser[Hỏi lại User]
    AskUser --> UserInput

    Router -- Đủ thông tin --> CheckIntent{Intent là gì?}

    CheckIntent -- Tìm kiếm --> Agent1[Search Agent]
    CheckIntent -- Tư vấn --> Agent2[Consultant Agent]
    CheckIntent -- Chi tiết --> Agent3[Expert Agent]
```

### Tổng kết

Bạn vẫn giữ **4 Agents** (1 Lead, 3 Staff). Nhưng bạn trao thêm quyền cho ông **Lead (Orchestrator)**: Nếu yêu cầu của khách quá mơ hồ, ông Lead có quyền hỏi lại ngay lập tức mà không cần chuyển xuống cho nhân viên.

Cách này giúp phản hồi cực nhanh (vì không cần query database) và tạo cảm giác chatbot rất thông minh, biết quan tâm đến nhu cầu thực sự của khách.

---

### 1. Mô hình Quan hệ (ERD Diagram Concept)

Chúng ta sẽ tách dữ liệu thành 3 bảng chính: `brands`, `products` (dòng son), và `product_variants` (thỏi son cụ thể).

- **Logic:** Một Thương hiệu (`brands`) có nhiều Dòng son (`products`). Một Dòng son có nhiều Màu sắc/Biến thể (`product_variants`).

### 2. Thiết kế chi tiết (Physical Schema)

SQL

```
-- 1. Bảng Thương hiệu (Lookup Table)
-- Mục đích: Chuẩn hóa brand_name, tránh lặp lại chuỗi text "Revlon" hàng nghìn lần.
CREATE TABLE brands (
    brand_id SERIAL PRIMARY KEY,
    brand_name VARCHAR(255) UNIQUE NOT NULL
);

-- 2. Bảng Dòng sản phẩm (Master Data)
-- Chứa thông tin chung không thay đổi theo màu sắc (Mô tả, thành phần, highlights)
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY, -- Sử dụng product_id từ CSV (VD: xlsImpprod2940211)
    brand_id INT REFERENCES brands(brand_id),
    product_name VARCHAR(255) NOT NULL,
    description TEXT, -- Chứa thông tin để AI học (Context)
    ingredients TEXT, -- Thành phần chung
    highlights JSONB, -- Lưu dưới dạng JSON để dễ lọc (VD: ["Vegan", "Cruelty Free"])
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Bảng Biến thể (Transactional/Inventory Data)
-- Chứa thông tin cụ thể của từng thỏi son (Màu, giá, ảnh, tình trạng hàng)
CREATE TABLE product_variants (
    uniq_id VARCHAR(50) PRIMARY KEY, -- Sử dụng uniq_id từ CSV làm khóa chính
    product_id VARCHAR(50) REFERENCES products(product_id) ON DELETE CASCADE,
    color VARCHAR(255), -- Tên màu (VD: Toast Of NY)
    size VARCHAR(50),   -- Dung tích (VD: 0.15 oz)
    price DECIMAL(10, 2), -- Giá tiền để lọc và tính toán
    availability VARCHAR(50), -- Tình trạng hàng (In Stock/Out of Stock)
    primary_image_url TEXT, -- Link ảnh hiển thị cho user
    metadata JSONB -- Dự phòng cho các field khác nếu phát sinh sau này
);
```

---

### 3. Tại sao thiết kế như vậy? (Giải thích & Lợi ích)

#### A. Chuẩn hóa dữ liệu (Normalization - 3NF)

- **Vấn đề của file CSV:** Nếu bạn để chung 1 bảng, tên hãng "MAC" và mô tả dòng son "Mac Matte Lipstick" sẽ bị lặp lại 50 lần cho 50 màu son khác nhau.
- **Giải pháp:** Tách ra bảng `products`.
- **Lợi ích:**
  - **Tiết kiệm dung lượng:** Mô tả dài (`description`, `ingredients`) chỉ lưu 1 lần duy nhất cho mỗi dòng son.
  - **Dễ bảo trì:** Nếu hãng sửa mô tả công dụng của dòng son, bạn chỉ cần update 1 dòng trong bảng `products`, thay vì update hàng trăm dòng trong bảng chung.

#### B. Tách biệt "Thông tin tĩnh" và "Thông tin động"

- **Bảng `products` (Tĩnh):** Chứa kiến thức (Knowledge) cho Chatbot. AI sẽ dùng bảng này để hiểu "Son này có lì không?", "Son này có chì không?".
- **Bảng `product_variants` (Động):** Chứa thông tin bán hàng. Chatbot dùng bảng này để trả lời "Màu đỏ cam còn hàng không?", "Giá bao nhiêu?".

#### C. Sử dụng JSONB cho `highlights`

- Trong CSV, `highlights` có thể là một list các tính năng. Lưu dạng JSONB trong PostgreSQL cho phép bạn thực hiện các truy vấn cực mạnh như: _"Tìm tất cả son có tính năng 'Vegan'"_ mà không cần dùng `LIKE %...%` (rất chậm).

---

### 4. Thiết kế này Cover được những Use Case nào?

Dưới đây là các kịch bản thực tế mà chatbot của bạn sẽ gặp và cách Database này xử lý:

#### Case 1: Tư vấn theo tính năng (Semantic/Knowledge Search)

- **User:** _"Tìm cho mình loại son nào nhiều dưỡng, không bị khô môi."_
- **Hệ thống:** Chatbot sẽ search trong bảng `products` (cột `description`, `ingredients`). Vì đã tách bảng, việc search rất nhanh và không bị trùng lặp kết quả (không trả về 10 thỏi son cùng loại chỉ khác màu).

#### Case 2: Tư vấn theo màu sắc và giá (Filter Search)

- **User:** _"Mình muốn tìm son màu đỏ gạch, giá dưới 15 đô."_
- **Hệ thống:**
  1. Query bảng `product_variants`: `WHERE color LIKE '%brick red%' AND price < 15`.
  2. JOIN với bảng `products` để lấy thêm tên đầy đủ và ảnh.
- **Hiệu quả:** Tốc độ cực nhanh vì search trên các trường đã được đánh index (`price`, `color`).

#### Case 3: Hiển thị chi tiết sản phẩm (Product Card)

- **User:** _"Cho mình xem thỏi Revlon màu Toast of NY."_
- **Hệ thống:** Dùng `uniq_id` hoặc tìm theo `color` + `product_name` để lấy thông tin.
  - Lấy ảnh, giá, size từ `product_variants`.
  - Lấy công dụng, thành phần từ `products`.
  - Ghép lại thành một câu trả lời hoàn chỉnh.

#### Case 4: Kiểm tra tình trạng hàng (Inventory Check)

- **User:** _"Màu này còn hàng không shop?"_
- **Hệ thống:** Chỉ cần check cột `availability` trong bảng `product_variants`. Việc tách bảng giúp việc update trạng thái kho hàng (hàng nghìn transaction/giây) không làm ảnh hưởng đến việc đọc mô tả sản phẩm của AI.
