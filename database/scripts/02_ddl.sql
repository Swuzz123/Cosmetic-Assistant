-- =============== NHÓM 1: Kho dữ liệu sản phẩm (Knowledge Base) ===============

-- Brand Table (Lookup Table)
-- Mục đích: Chuẩn hóa brand_name, tránh lặp lại chuỗi text "Revlon" hàng nghìn lần.
CREATE TABLE IF NOT EXISTS brands (
  brand_id            SERIAL PRIMARY KEY,
  brand_name          VARCHAR(255) UNIQUE NOT NULL
);

-- Product Table (Master Data)
-- Chứa thông tin chung không thay đổi theo màu sắc (Mô tả, thành phần, highlights)
CREATE TABLE IF NOT EXISTS products (
  product_id          VARCHAR(50) PRIMARY KEY, 
  brand_id            INT REFERENCES brands(brand_id),
  product_name        VARCHAR(255) NOT NULL,
  description         TEXT, 
  ingredients         TEXT, 
  highlights          TEXT,
  embedding           vector(768),
  created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product_variants Table (Transactional/Inventory Data)
-- Chứa thông tin cụ thể của từng thỏi son (Màu, giá, ảnh, tình trạng hàng)
CREATE TABLE IF NOT EXISTS product_variants (
  uniq_id             VARCHAR(50) PRIMARY KEY, 
  product_id          VARCHAR(50) REFERENCES products(product_id) ON DELETE CASCADE,
  color               VARCHAR(225), 
  size                VARCHAR(50),   
  price               DECIMAL(10, 2), 
  availability        VARCHAR(50), 
  primary_image_url   TEXT
);

-- ============ NHÓM 2: Quản lý Người Dùng & Ngữ Cảnh (User Context) ===========

-- Customer Table
CREATE TABLE IF NOT EXISTS customers (
  customer_id           SERIAL PRIMARY KEY,
  full_name             VARCHAR(100),
  phone_number          VARCHAR(20),
  skin_profile          JSONB,
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat_session Table (Short-term Memory)
CREATE TABLE IF NOT EXISTS chat_sessions (
  session_id            VARCHAR(100) PRIMARY KEY,
  customer_id           INT REFERENCES customers(customer_id),
  start_time            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_interaction      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  current_intent        VARCHAR(50),
  context_data          JSONB 
);

-- ====================== NHÓM 3: Giao Dịch (Transaction) ======================

-- Orders Table
CREATE TABLE IF NOT EXISTS orders (
  order_id              SERIAL PRIMARY KEY,
  customer_id           INT REFERENCES customers(customer_id),
  session_id            VARCHAR(100) REFERENCES chat_sessions(session_id),
  total_amount          DECIMAL(10, 2),
  status                VARCHAR(50) DEFAULT 'pending',
  shipping_address      TEXT,
  payment_method        VARCHAR(50),
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order_items Table
CREATE TABLE IF NOT EXISTS order_items (
  order_item_id         SERIAL PRIMARY KEY,
  order_id              INT REFERENCES orders(order_id) ON DELETE CASCADE,
  variant_id            VARCHAR(50) REFERENCES product_variants(uniq_id),
  quantity              INT DEFAULT 1,
  unit_price            DECIMAL(10, 2)
);



