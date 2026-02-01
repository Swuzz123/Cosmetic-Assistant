-- 1. Ingest brands
COPY brands (brand_id, brand_name)
FROM '/data/brands.csv'
DELIMITER ','
CSV HEADER;
SELECT setval('brands_brand_id_seq', (SELECT MAX(brand_id) FROM brands));

-- 2. Ingest products
COPY products (
  product_id,
  brand_id,
  product_name,
  description,
  ingredients,
  highlights
)
FROM '/data/products.csv'
DELIMITER ','
CSV HEADER;

-- 3. Ingest product_variants
COPY product_variants (
  uniq_id,
  product_id,
  color,
  size,
  price,
  availability,
  primary_image_url
)
FROM '/data/variants.csv'
DELIMITER ','
CSV HEADER;
