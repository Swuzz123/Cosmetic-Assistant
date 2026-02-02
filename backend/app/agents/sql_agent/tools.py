from typing import List, Dict, Optional
from langchain_core.tools import tool
from sqlalchemy import text
from .connection import get_sync_db_context, execute_read_only_query

# ============================== TOOL DEFINITIONS ==============================

@tool
def search_products_by_sql(sql_query: str) -> List[Dict]:
    """
    Execute a Safe SQL query to find products. 
    Use this tool when the user filters by price, brand, color, or specific attributes.
    
    The database has 3 main tables:
    1. brands (brand_id, brand_name)
    2. products (product_id, brand_id, product_name, description, ingredients, highlights)
    3. product_variants (uniq_id, product_id, color, price, size, availability)
    
    IMPORTANT: 
    - Always JOIN 'products' and 'product_variants' on 'product_id' to get full info.
    - 'description' is in 'products', but 'price' and 'color' are in 'product_variants'.
    - Use LIMIT 5 unless specified otherwise.
    """
    print(f"\n[DEBUG] Executing SQL: {sql_query}")
    return execute_read_only_query(sql_query)

@tool
def get_product_details(product_id: str) -> Dict:
    """
    Get full details for a specific product by its ID.
    Use this when the user asks specific questions about a product (ingredients, usage, etc.)
    """
    query = """
    SELECT 
        p.product_name, p.description, p.ingredients, p.highlights,
        pv.color, pv.price, pv.availability, b.brand_name
    FROM products p
    JOIN product_variants pv ON p.product_id = pv.product_id
    JOIN brands b ON p.brand_id = b.brand_id
    WHERE p.product_id = :pid OR pv.uniq_id = :pid
    LIMIT 1;
    """
    
    with get_sync_db_context() as session:
        result = session.execute(text(query), {"pid": product_id}).mappings().first()
        if result:
            return dict(result)
        return {"error": "Product not found"}

@tool
def check_inventory(product_name: str, color: Optional[str] = None) -> List[Dict]:
    """
    Check stock/availability for a product.
    """
    base_query = """
    SELECT p.product_name, pv.color, pv.availability, pv.price 
    FROM product_variants pv
    JOIN products p ON pv.product_id = p.product_id
    WHERE p.product_name ILIKE :name
    """
    params = {"name": f"%{product_name}%"}
    
    if color:
        base_query += " AND pv.color ILIKE :color"
        params["color"] = f"%{color}%"
        
    return execute_read_only_query(base_query, params)
