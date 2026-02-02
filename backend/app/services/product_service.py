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
  def get_top_products(db: Session, limit: int = 10) -> List[Product]:
    """Fetch top products (simple limit for now)"""
    stmt = select(Product).limit(limit)
    return db.execute(stmt).scalars().all()

  @staticmethod
  def get_variant_inventory(db: Session, variant_id: str) -> Optional[ProductVariant]:
    """Check inventory/details for a specific variant"""
    stmt = select(ProductVariant).where(ProductVariant.uniq_id == variant_id)
    return db.execute(stmt).scalars().first()
