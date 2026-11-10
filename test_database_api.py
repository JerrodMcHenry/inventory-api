
def test_create_product_in_database(client):
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

    product = response.json()

    assert product["id"] == 500
    assert product["name"] == "Test Keyboard"
    assert product["quantity"] == 10

    get_response = client.get("/products/500")

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Test Keyboard"
