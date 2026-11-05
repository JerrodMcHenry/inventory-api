import pytest

from inventory import get_product, create_product, update_stock, delete_product, list_products


@pytest.fixture
def products():
    return {
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


# -------------------------
# GET PRODUCT TESTS
# -------------------------

def test_get_existing_product(products):
    result = get_product(products, 101)

    assert result == {
        "name": "Keyboard",
        "price": 49.99,
        "quantity": 20
    }


def test_get_missing_product(products):
    result = get_product(products, 999)

    assert result is None


# -------------------------
# CREATE PRODUCT TESTS
# -------------------------

def test_create_product():
    products = {}

    result = create_product(
        products,
        101,
        "Keyboard",
        49.99,
        20
    )

    assert 101 in products
    assert products[101]["name"] == "Keyboard"
    assert products[101]["price"] == 49.99
    assert products[101]["quantity"] == 20
    assert result == products[101]


def test_create_product_duplicate_id(products):
    original = products[101].copy()

    with pytest.raises(ValueError, match="This ID is in use"):
        create_product(products, 101, "Monitor", 199.99, 5)

    assert products[101] == original


@pytest.mark.parametrize("name", ["", " ", "   "])
def test_create_product_invalid_name(name):
    products = {}

    with pytest.raises(ValueError, match="Product name cannot be empty"):
        create_product(products, 103, name, 49.99, 20)

    assert products == {}


@pytest.mark.parametrize("price", [-1, -49.99])
def test_create_product_negative_price(price):
    products = {}

    with pytest.raises(ValueError, match="Product price cannot be negative"):
        create_product(products, 103, "Monitor", price, 10)

    assert products == {}


@pytest.mark.parametrize("price", ["free", None, True])
def test_create_product_invalid_price_type(price):
    products = {}

    with pytest.raises(ValueError, match="Product price must be a number"):
        create_product(products, 103, "Monitor", price, 10)

    assert products == {}


@pytest.mark.parametrize("quantity", [-1, -10])
def test_create_product_negative_quantity(quantity):
    products = {}

    with pytest.raises(ValueError, match="Product quantity cannot be negative"):
        create_product(products, 103, "Monitor", 199.99, quantity)

    assert products == {}


@pytest.mark.parametrize("quantity", [2.5, "10", None, True])
def test_create_product_invalid_quantity_type(quantity):
    products = {}

    with pytest.raises(ValueError, match="Product quantity must be an integer"):
        create_product(products, 103, "Monitor", 199.99, quantity)

    assert products == {}


def test_create_product_zero_price_and_quantity():
    products = {}

    result = create_product(products, 103, "Sample", 0, 0)

    assert result["price"] == 0
    assert result["quantity"] == 0
    assert 103 in products
    
def test_update_stock_increase():
    products = {
        101: {"name": "Keyboard", "price": 49.99, "quantity": 20}
    }

    result = update_stock(products, 101, 15)

    assert result["quantity"] == 35
    assert products[101]["quantity"] == 35


def test_update_stock_decrease():
    products = {
        101: {"name": "Keyboard", "price": 49.99, "quantity": 20}
    }

    result = update_stock(products, 101, -5)

    assert result["quantity"] == 15


def test_update_stock_insufficient_stock():
    products = {
        101: {"name": "Keyboard", "price": 49.99, "quantity": 20}
    }

    with pytest.raises(ValueError, match="Insufficient stock"):
        update_stock(products, 101, -25)

    assert products[101]["quantity"] == 20


def test_update_stock_missing_product():
    products = {}

    with pytest.raises(ValueError, match="Product does not exist"):
        update_stock(products, 999, 10)


@pytest.mark.parametrize("quantity_change", [2.5, "10", None, True])
def test_update_stock_invalid_quantity_change(quantity_change):
    products = {
        101: {"name": "Keyboard", "price": 49.99, "quantity": 20}
    }

    with pytest.raises(ValueError, match="Quantity change must be an integer"):
        update_stock(products, 101, quantity_change)

    assert products[101]["quantity"] == 20


def test_update_stock_to_zero():
    products = {
        101: {"name": "Keyboard", "price": 49.99, "quantity": 20}
    }

    result = update_stock(products, 101, -20)

    assert result["quantity"] == 0
    
def test_delete_existing_product():
    products = {
        101: {"name": "Keyboard", "price": 49.99, "quantity": 20},
        102: {"name": "Mouse", "price": 24.99, "quantity": 15}
    }

    deleted = delete_product(products, 101)

    assert deleted == {
        "name": "Keyboard",
        "price": 49.99,
        "quantity": 20
    }

    assert 101 not in products
    assert 102 in products


def test_delete_missing_product():
    products = {
        101: {"name": "Keyboard", "price": 49.99, "quantity": 20}
    }

    with pytest.raises(ValueError, match="Product does not exist"):
        delete_product(products, 999)

    assert 101 in products
    assert len(products) == 1


def test_delete_last_product():
    products = {
        101: {"name": "Keyboard", "price": 49.99, "quantity": 20}
    }

    deleted = delete_product(products, 101)

    assert deleted["name"] == "Keyboard"
    assert products == {}
    
def test_list_products():
    products = {
        101: {"name": "Keyboard", "price": 49.99, "quantity": 20},
        102: {"name": "Mouse", "price": 24.99, "quantity": 15}
    }

    result = list_products(products)

    assert result == [
        {"id": 101, "name": "Keyboard", "price": 49.99, "quantity": 20},
        {"id": 102, "name": "Mouse", "price": 24.99, "quantity": 15}
    ]


def test_list_products_empty():
    products = {}

    result = list_products(products)

    assert result == []


def test_list_products_does_not_modify_inventory():
    products = {
        101: {"name": "Keyboard", "price": 49.99, "quantity": 20}
    }

    original = {
        101: {"name": "Keyboard", "price": 49.99, "quantity": 20}
    }

    list_products(products)

    assert products == original


def test_list_products_returns_independent_dictionaries():
    products = {
        101: {"name": "Keyboard", "price": 49.99, "quantity": 20}
    }

    result = list_products(products)

    result[0]["quantity"] = 999

    assert products[101]["quantity"] == 20