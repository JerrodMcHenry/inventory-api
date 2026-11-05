
from exceptions import (
    ProductNotFoundError,
    DuplicateProductError,
    InsufficientStockError,
)


def get_product(products: dict, product_id: int):
    """Retrieve a product by ID, or return None if it doesn't exist."""
    return products.get(product_id)


def create_product(
    products: dict,
    product_id: int,
    name: str,
    price: float,
    quantity: int
):
    """Validate and add a new product to inventory."""

    if product_id in products:
        raise ValueError("This ID is in use. Try again")

    if not isinstance(name, str) or not name.strip():
        raise ValueError("Product name cannot be empty")

    if isinstance(price, bool) or not isinstance(price, (int, float)):
        raise ValueError("Product price must be a number")

    if price < 0:
        raise ValueError("Product price cannot be negative")

    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise ValueError("Product quantity must be an integer")

    if quantity < 0:
        raise ValueError("Product quantity cannot be negative")

    product = {
        "name": name,
        "price": price,
        "quantity": quantity
    }

    products[product_id] = product

    return product



def update_stock(
    products: dict,
    product_id: int,
    quantity_change: int
):
    """Update the stock quantity of an existing product."""

    # 1. Find the product
    product = products.get(product_id)

    if product is None:
        raise ValueError("Product does not exist")

    # 2. Validate the quantity change
    if isinstance(quantity_change, bool) or not isinstance(quantity_change, int):
        raise ValueError("Quantity change must be an integer")

    # 3. Calculate the new quantity
    new_quantity = product["quantity"] + quantity_change

    # 4. Prevent negative inventory
    if new_quantity < 0:
        raise InsufficientStockError("Insufficient stock")

    # 5. Update the existing product
    product["quantity"] = new_quantity

    # 6. Return the updated product
    return product


def delete_product(products: dict, product_id: int):
    """Delete a product by ID and return the removed product."""

    if product_id not in products:
        raise ValueError("Product does not exist")

    return products.pop(product_id)


def list_products(products: dict) -> list:
    """Return all products as a list, including their IDs."""

    result = []

    for product_id, product in products.items():
        product_data = {
            "id": product_id,
            **product
        }

        result.append(product_data)

    return result