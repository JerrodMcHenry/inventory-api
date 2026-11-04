products = {
    101: {
        "name": "Keyboard",
        "price": 49.99,
        "quantity": 20
    },
    102: {
        "name": "Mouse",
        "price": 24.99,
        "quantity": 15
    }
}


def get_product(products, product_id: int):
    product = products.get(product_id)
    return product
    
    
    
def create_product(
    products: dict,
    product_id: int,
    name: str,
    price: float,
    quantity: int
):
    if product_id in products:
        raise ValueError("This ID is in use. Try again")
    
    product = {
        "name": name,
        "price": price,
        "quantity": quantity
    }
    
    products[product_id] = product
    
    return product