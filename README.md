# Inventory API

A Python/FastAPI inventory management API backed by PostgreSQL, built as a hands-on backend software engineering apprenticeship project.

## Features

- Create, retrieve, list, and delete products.
- Adjust inventory quantities using an atomic database update that prevents negative stock.
- Validate requests with Pydantic.
- Persist products using SQLAlchemy and PostgreSQL.
- Manage database schema changes using Alembic.
- Test API behavior with pytest and an isolated PostgreSQL test database.

## Technology Stack

- **Language:** Python
- **API framework:** FastAPI
- **Validation:** Pydantic
- **ORM:** SQLAlchemy
- **Database:** PostgreSQL
- **Migrations:** Alembic
- **Testing:** pytest
- **Infrastructure:** Docker

## Architecture

```text
HTTP Client
    |
    v
FastAPI Routes (main.py)
    |
    | Pydantic Request Validation
    v
Repository (product_repository.py)
    |
    | SQLAlchemy Session
    v
ORM Models (models.py)
    |
    v
PostgreSQL Database
```

`database.py` configures database connectivity and session management.

`exceptions.py` contains custom domain exceptions.

`inventory.py` preserves the original dictionary-based CRUD implementation used during the initial Python exercises. The current PostgreSQL-backed API uses `product_repository.py`.

## API Endpoints

| Method | Endpoint                       | Description              |
| ------ | ------------------------------ | ------------------------ |
| GET    | `/products`                    | List all products        |
| GET    | `/products/{product_id}`       | Retrieve a product       |
| POST   | `/products`                    | Create a product         |
| PATCH  | `/products/{product_id}/stock` | Adjust product inventory |
| DELETE | `/products/{product_id}`       | Delete a product         |

### Example: Create Product

`POST /products`

```json
{
  "id": 103,
  "name": "Monitor",
  "price": 199.99,
  "quantity": 5
}
```

### Example: Update Stock

`PATCH /products/103/stock`

```json
{
  "quantity_change": -2
}
```

The API uses validation and domain-specific error handling to reject invalid input, missing products, duplicate IDs, and insufficient inventory.

## Local Development

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure PostgreSQL

Start a PostgreSQL instance and create development and test databases.

The local development environment used PostgreSQL in Docker, with host port `5433` mapped to container port `5432`.

### 4. Configure environment variables

Create a `.env` file:

```dotenv
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@127.0.0.1:5433/inventory_db
TEST_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@127.0.0.1:5433/inventory_test_db
```

Replace the placeholders with your own credentials.

Never commit `.env` or real passwords.

### 5. Apply database migrations

For a new, empty development database:

```bash
alembic upgrade head
```

For an existing database, verify that its schema matches the initial migration before considering `alembic stamp head`.

### 6. Run the application

```bash
uvicorn main:app --reload
```

Interactive API documentation:

`http://127.0.0.1:8000/docs`

## Testing

Run PostgreSQL integration tests:

```bash
pytest -q test_database_api.py
```

Check migration status:

```bash
alembic current
alembic history
alembic check
```

The latest reported checkpoint was 32 passing tests and no new upgrade operations detected by Alembic.

The integration tests use a separate test database and transaction isolation to protect development data.

## Current Limitations

Inventory API is an educational backend engineering project, not a production-hardened inventory service.

Areas not fully implemented or verified include:

- Authentication and authorization.
- Database outage recovery.
- Concurrent-load testing.
- Monitoring and observability.
- Rate limiting.
- Production deployment.

The current test fixture creates ORM tables directly; provisioning the test database through Alembic is a possible future improvement.

## Engineering Documentation

See `ENGINEERING_GUIDE.md` for detailed explanations of architecture, database transactions, design decisions, debugging lessons, and technical interview review questions.
