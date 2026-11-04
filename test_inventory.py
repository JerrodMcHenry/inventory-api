from inventory import get_product


def test_get_existing_product():
    products = {
        101: {
            "name": "Keyboard",
            "price": 49.99,
            "quantity": 20
        }
    }
    
    result = get_product(products, 101)
    
    assert result == {
        "name": "Keyboard",
        "price": 49.99,
        "quantity": 20 
    }