
from decimal import Decimal
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from exceptions import (
    ProductNotFoundError,
    InsufficientStockError,
)
from models import Product
from product_repository import (
    get_product,
    list_products,
    create_product,
    update_stock,
    delete_product,
)


app = FastAPI(
    title="Inventory API",
    description="A REST API for managing warehouse inventory",
    version="0.3.0",
)


# Request models

class ProductCreate(BaseModel):
    model_config = ConfigDict(strict=True)

    id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0, le=99999999.99, allow_inf_nan=False)
    quantity: int = Field(ge=0, le=2147483647)


class StockUpdate(BaseModel):
    model_config = ConfigDict(strict=True)

    quantity_change: int


# Response model

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: Decimal
    quantity: int


DatabaseSession = Annotated[Session, Depends(get_db)]


# GET all products

@app.get("/products", response_model=list[ProductResponse])
def read_products(session: DatabaseSession):
    return list_products(session)


# GET one product

@app.get("/products/{product_id}", response_model=ProductResponse)
def read_product(product_id: int, session: DatabaseSession):
    product = get_product(session, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


# CREATE product

@app.post(
    "/products",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductResponse,
)
def add_product(data: ProductCreate, session: DatabaseSession):
    try:
        return create_product(
            session=session,
            product_id=data.id,
            name=data.name,
            price=Decimal(str(data.price)),
            quantity=data.quantity,
        )

    except IntegrityError as error:
        session.rollback()

        if get_product(session, data.id) is not None:
            raise HTTPException(
                status_code=409,
                detail="Product already exists",
            ) from error

        raise


# UPDATE stock

@app.patch(
    "/products/{product_id}/stock",
    response_model=ProductResponse,
)
def change_stock(
    product_id: int,
    data: StockUpdate,
    session: DatabaseSession,
):
    try:
        return update_stock(
            session,
            product_id,
            data.quantity_change,
        )

    except ProductNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except InsufficientStockError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error


# DELETE product

@app.delete(
    "/products/{product_id}",
    response_model=ProductResponse,
)
def remove_product(product_id: int, session: DatabaseSession):
    try:
        return delete_product(session, product_id)

    except ProductNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
