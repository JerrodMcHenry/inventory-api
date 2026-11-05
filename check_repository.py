
from database import SessionLocal
from product_repository import get_product, list_products


with SessionLocal() as session:
    product = get_product(session, 101)

    if product is not None:
        print(f"Found product: {product.name}")

    products = list_products(session)

    for product in products:
        print(f"{product.id}: {product.name}")
