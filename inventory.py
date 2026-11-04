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
    
    
    
print(get_product(products, 102))
print(get_product(products, 105))