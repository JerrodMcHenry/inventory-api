
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict

from inventory import (
    get_product,
    list_products,
    create_product,
    update_stock,
    delete_product,
)

from exceptions import (
    ProductNotFoundError,
    DuplicateProductError,
    InsufficientStockError,
)

app = FastAPI(
    title="Inventory API",
    description="A REST API for managing warehouse inventory",
    version="0.2.0",
)


class ProductCreate(BaseModel):
    model_config = ConfigDict(strict=True)

    id: int = Field(gt=0)
    name: str = Field(min_length=1)
    price: float = Field(ge=0, allow_inf_nan=False)
    quantity: int = Field(ge=0)


class StockUpdate(BaseModel):
    model_config = ConfigDict(strict=True)

    quantity_change: int


# Temporary storage until we introduce PostgreSQL.
products = {
    101: {"name": "Keyboard", "price": 49.99, "quantity": 20},
    102: {"name": "Mouse", "price": 24.99, "quantity": 15},
}


@app.get("/products")
def get_products():
    return list_products(products)


@app.get("/products/{product_id}")
def get_product_by_id(product_id: int):
    product = get_product(products, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product does not exist",
        )

    return {"id": product_id, **product}


@app.post("/products", status_code=status.HTTP_201_CREATED)
def add_product(data: ProductCreate):
    try:
        product = create_product(
            products,
            data.id,
            data.name,
            data.price,
            data.quantity,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    return {"id": data.id, **product}


@app.patch("/products/{product_id}/stock")
def change_stock(product_id: int, data: StockUpdate):
    try:
        product = update_stock(
            products,
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

    return {"id": product_id, **product}



@app.delete("/products/{product_id}")
def remove_product(product_id: int):
    try:
        deleted = delete_product(products, product_id)
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    return {"id": product_id, **deleted}
