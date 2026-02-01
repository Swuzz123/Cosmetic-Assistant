-- 1. INDEX TABLE brands 
CREATE INDEX IF NOT EXISTS idx_products_brand_id ON products(brand_id);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(product_name);


-- 2. INDEX TABLE product_variants
CREATE INDEX IF NOT EXISTS idx_variants_product_id ON product_variants(product_id);
CREATE INDEX IF NOT EXISTS idx_variants_price ON product_variants(price);
CREATE INDEX IF NOT EXISTS idx_variants_color ON product_variants(color);


-- 3. INDEX TABLE order_items
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
