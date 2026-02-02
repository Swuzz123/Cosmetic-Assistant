from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.models import Product, ProductVariant, Brand

class SearchService:
  @staticmethod
  def search_products(
    db: Session, 
    brand_name: Optional[str] = None, 
    price_min: Optional[float] = None, 
    price_max: Optional[float] = None,
    color: Optional[str] = None
  ) -> List[Dict[str, Any]]:
    """
    Dynamic SQL search for products based on hard filters.
    Returns a list of dictionaries with product and variant info.
    """
    stmt = select(Product, ProductVariant, Brand).\
      join(ProductVariant, Product.product_id == ProductVariant.product_id).\
      join(Brand, Product.brand_id == Brand.brand_id)

    conditions = []

    if brand_name:
      # Case insensitive partial match
      conditions.append(Brand.brand_name.ilike(f"%{brand_name}%"))
    
    if price_min is not None:
      conditions.append(ProductVariant.price >= price_min)
        
    if price_max is not None:
      conditions.append(ProductVariant.price <= price_max)
        
    if color:
      conditions.append(ProductVariant.color.ilike(f"%{color}%"))

    if conditions:
      stmt = stmt.where(and_(*conditions))
    
    # Limit results to avoid overload
    stmt = stmt.limit(20)

    results = db.execute(stmt).all()
    
    # Format output
    output = []
    for product, variant, brand in results:
      output.append({
        "product_id": product.product_id,
        "product_name": product.product_name,
        "brand": brand.brand_name,
        "variant_id": variant.uniq_id,
        "color": variant.color,
        "price": float(variant.price) if variant.price else 0.0,
        "availability": variant.availability,
        "image": variant.primary_image_url
      })
        
    return output
