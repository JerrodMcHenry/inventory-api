
from decimal import Decimal

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from exceptions import (
    ProductNotFoundError,
    InsufficientStockError,
)
from models import Product


def get_product(session: Session, product_id: int) -> Product | None:
    return session.get(Product, product_id)


def list_products(session: Session) -> list[Product]:
    statement = select(Product).order_by(Product.id)
    return list(session.scalars(statement).all())


def create_product(
    session: Session,
    product_id: int,
    name: str,
    price: Decimal,
    quantity: int,
) -> Product:
    product = Product(
        id=product_id,
        name=name,
        price=price,
        quantity=quantity,
    )

    session.add(product)
    session.commit()
    session.refresh(product)

    return product


def update_stock(
    session: Session,
    product_id: int,
    quantity_change: int,
) -> Product:
    statement = (
        update(Product)
        .where(Product.id == product_id)
        .where(Product.quantity + quantity_change >= 0)
        .values(quantity=Product.quantity + quantity_change)
        .returning(Product.id)
    )

    updated_id = session.scalar(statement)

    if updated_id is None:
        exists = session.get(Product, product_id)

        session.rollback()

        if exists is None:
            raise ProductNotFoundError("Product not found")

        raise InsufficientStockError("Insufficient stock")

    session.commit()

    return session.get(Product, product_id)


def delete_product(
    session: Session,
    product_id: int,
) -> dict:
    statement = (
        delete(Product)
        .where(Product.id == product_id)
        .returning(
            Product.id,
            Product.name,
            Product.price,
            Product.quantity,
        )
    )

    deleted = session.execute(statement).one_or_none()

    if deleted is None:
        session.rollback()
        raise ProductNotFoundError("Product not found")

    result = dict(deleted._mapping)

    session.commit()

    return result
