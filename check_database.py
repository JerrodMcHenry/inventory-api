
from sqlalchemy import select

from database import SessionLocal
from models import Product


with SessionLocal() as session:
    statement = select(Product)

    products = session.scalars(statement).all()

    for product in products:
        print(
            f"ID: {product.id}, "
            f"Name: {product.name}, "
            f"Price: {product.price}, "
            f"Quantity: {product.quantity}"
        )
