
import pytest


@pytest.fixture
def product(client):
    response = client.post(
        "/products",
        json={
            "id": 500,
            "name": "Test Keyboard",
            "price": 79.99,
            "quantity": 10,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_product(client):
    response = client.post(
        "/products",
        json={
            "id": 501,
            "name": "Monitor",
            "price": 199.99,
            "quantity": 5,
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Monitor"

    saved = client.get("/products/501")
    assert saved.status_code == 200


def test_get_product(client, product):
    response = client.get("/products/500")

    assert response.status_code == 200
    assert response.json()["id"] == 500
    assert response.json()["name"] == "Test Keyboard"


def test_list_products(client, product):
    response = client.get("/products")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == 500


def test_duplicate_product(client, product):
    response = client.post(
        "/products",
        json={
            "id": 500,
            "name": "Duplicate Keyboard",
            "price": 49.99,
            "quantity": 3,
        },
    )

    assert response.status_code == 409


def test_update_stock(client, product):
    response = client.patch(
        "/products/500/stock",
        json={"quantity_change": -3},
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 7

    saved = client.get("/products/500")
    assert saved.json()["quantity"] == 7


def test_insufficient_stock(client, product):
    response = client.patch(
        "/products/500/stock",
        json={"quantity_change": -100},
    )

    assert response.status_code == 409

    saved = client.get("/products/500")
    assert saved.json()["quantity"] == 10


def test_delete_product(client, product):
    response = client.delete("/products/500")

    assert response.status_code == 200
    assert response.json()["id"] == 500

    missing = client.get("/products/500")
    assert missing.status_code == 404


def test_get_missing_product(client):
    response = client.get("/products/999")

    assert response.status_code == 404


def test_update_missing_product(client):
    response = client.patch(
        "/products/999/stock",
        json={"quantity_change": 5},
    )

    assert response.status_code == 404


def test_delete_missing_product(client):
    response = client.delete("/products/999")

    assert response.status_code == 404


def test_invalid_product_input(client):
    response = client.post(
        "/products",
        json={
            "id": 600,
            "name": "Invalid Product",
            "price": -10,
            "quantity": 5,
        },
    )

    assert response.status_code == 422


def test_invalid_stock_input(client, product):
    response = client.patch(
        "/products/500/stock",
        json={"quantity_change": "five"},
    )

    assert response.status_code == 422
