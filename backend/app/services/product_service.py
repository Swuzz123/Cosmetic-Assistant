from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Product, ProductVariant

class ProductService:
  @staticmethod
  def get_product_by_id(db: Session, product_id: str) -> Optional[Product]:
    """Fetch a product by its ID, including variants"""
    stmt = select(Product).where(Product.product_id == product_id)
    result = db.execute(stmt).scalars().first()
    return result

  @staticmethod
  def get_product_by_id_or_name(db: Session, identifier: str) -> Optional[Product]:
    """Fetch product by ID first, then try Name (case-insensitive), then fuzzy"""
    # 1. Try ID
    stmt = select(Product).where(Product.product_id == identifier)
    result = db.execute(stmt).scalars().first()
    
    if not result:
        # 2. Try Name (Identifier inside Product Name)
        # e.g. identifier="Ruby Woo", name="Mac Ruby Woo" -> MATCH
        stmt = select(Product).where(Product.product_name.ilike(f"%{identifier}%"))
        result = db.execute(stmt).scalars().first()
        
    if not result:
        # 3. Try Reverse Name (Product Name inside Identifier)
        # e.g. identifier="Lippie Stix by ColourPop", name="Lippie Stix" -> MATCH
        # Using python-side filtering for simplicity and safety against SQL injection quirks with formatting
        # Or using SQL: WHERE :identifier ILIKE ('%' || product_name || '%')
        from sqlalchemy import literal, func
        stmt = select(Product).where(literal(identifier).ilike(func.concat('%', Product.product_name, '%')))
        # We might match multiple (e.g. "Lipstick" inside "Red Lipstick"). We want the LONGEST match ideally.
        # Let's take the first one for now, usually it finds the specific one if identifier is specific.
        result = db.execute(stmt).scalars().first()
        
    return result

  @staticmethod
  def get_top_products(db: Session, limit: int = 10) -> List[Product]:
    """Fetch top products (simple limit for now)"""
    stmt = select(Product).limit(limit)
    return db.execute(stmt).scalars().all()

  @staticmethod
  def get_variant_inventory(db: Session, variant_id: str) -> Optional[ProductVariant]:
    """Check inventory/details for a specific variant"""
    stmt = select(ProductVariant).where(ProductVariant.uniq_id == variant_id)
    return db.execute(stmt).scalars().first()
