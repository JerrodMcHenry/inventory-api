from fastapi import FastAPI, HTTPException
from inventory import get_product, list_products


app = FastAPI(
    title="Inventory API",
    description="A REST API for managing warehouse inventory",
    version="0.1.0"
)

products = {
    101: {
        "name": "Keyboard",
        "price": 49.99,
        "quantity": 20,
    },
    102: {
        "name": "Mouse",
        "price": 24.99,
        "quantity": 15,
    },
}


@app.get("/products")
def get_products():
    return list_products(products)

@app.get("/products/{product_id}")
def get_prouduct_by_id(product_id: int):
    product = get_product(products, product_id)
    
    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product does not exist"
        )

    return {"id": product_id, **product}
