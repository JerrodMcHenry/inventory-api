
import pytest
from fastapi.testclient import TestClient

from main import app, products

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_inventory():
    """Give each test a fresh inventory."""
    products.clear()
    products.update({
        101: {"name": "Keyboard", "price": 49.99, "quantity": 20},
        102: {"name": "Mouse", "price": 24.99, "quantity": 15},
    })


def test_list_products():
    response = client.get("/products")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_missing_product():
    response = client.get("/products/999")

    assert response.status_code == 404


def test_create_product():
    response = client.post("/products", json={
        "id": 103,
        "name": "Monitor",
        "price": 199.99,
        "quantity": 10,
    })

    assert response.status_code == 201
    assert response.json()["name"] == "Monitor"
    assert products[103]["quantity"] == 10


def test_duplicate_product():
    response = client.post("/products", json={
        "id": 101,
        "name": "Another Keyboard",
        "price": 59.99,
        "quantity": 5,
    })

    assert response.status_code == 409
    assert products[101]["name"] == "Keyboard"


def test_update_stock():
    response = client.patch(
        "/products/101/stock",
        json={"quantity_change": -5},
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 15


def test_insufficient_stock():
    response = client.patch(
        "/products/101/stock",
        json={"quantity_change": -100},
    )

    assert response.status_code == 409
    assert products[101]["quantity"] == 20


def test_invalid_product():
    response = client.post("/products", json={
        "id": 103,
        "name": "Monitor",
        "price": -50,
        "quantity": 10,
    })

    assert response.status_code == 422
    assert 103 not in products


def test_delete_product():
    response = client.delete("/products/101")

    assert response.status_code == 200
    assert 101 not in products
