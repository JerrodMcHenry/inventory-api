# Inventory API — Engineering Guide

## Purpose

This document records the engineering concepts, implementation decisions, mistakes, debugging sessions, and lessons from building Inventory API.

**Objective:** Understand how to independently build a Python backend, connect it to PostgreSQL, manage database transactions, validate HTTP requests, and maintain database schemas.

The latest reported checkpoint was 32 passing tests, a successful migration on a fresh PostgreSQL database, and a clean Alembic schema check.

---

## 1. How We Built Inventory API

We progressed through seven layers:

1. **Python fundamentals:** Dictionary-based CRUD.
2. **HTTP:** FastAPI endpoints.
3. **Validation:** Pydantic models.
4. **Persistence:** SQLAlchemy ORM and repository functions.
5. **Database:** PostgreSQL running in Docker.
6. **Migrations:** Alembic schema versioning.
7. **Verification:** pytest and database integration tests.

The most important architectural principle:

**HTTP routes should handle HTTP concerns. Repository functions should handle database operations.**

This separation makes the application easier to understand, modify, and test.

## 2. Python Fundamentals — Dictionary-Based CRUD

We started with a Python dictionary storing products by their IDs.

Example:

```python
products = {
    101: {
        "id": 101,
        "name": "Keyboard",
        "price": 49.99,
        "quantity": 20
    }
}
```

### Dictionary membership

```python
if product_id in products:
    ...
```

This checks whether the product ID exists as a dictionary key.

It does not compare the product ID to the entire dictionary.

### Dictionary indexing

```python
product = products[product_id]
```

Retrieves the value associated with the key.

If the key doesn't exist, Python raises `KeyError`.

### Dictionary `.get()`

```python
product = products.get(product_id)
```

Returns the value when present or `None` when absent, unless a different default is supplied.

### Our CRUD operations

We implemented:

- `get_product()`
- `list_products()`
- `create_product()`
- `update_stock()`
- `delete_product()`

These exercises established how to retrieve, create, update, and remove application state.

### The important struggle: Turning requirements into code

One recurring difficulty was understanding what the requirement meant but not knowing which Python operations to write.

Use this process:

1. Identify the inputs.
2. Define the expected output.
3. Identify invalid cases.
4. Choose the appropriate data structure operations.
5. Write the implementation.
6. Check the edge cases.

Example requirement:

"Return a product by its ID, or raise an error when it doesn't exist."

Translate that into:

```python
def get_product(products, product_id):
    if product_id not in products:
        raise ProductNotFoundError("Product not found")

    return products[product_id]
```

The important skill is not memorizing this function. It's learning to translate a requirement into conditions, data access, and return behavior.

## 3. Pydantic — Validating Incoming Data

Python dictionaries don't automatically enforce a schema.

An API needs to validate incoming requests before processing them.

We introduced Pydantic models such as `ProductCreate`, `StockUpdate`, and `ProductResponse`.

Example:

```python
from pydantic import BaseModel, ConfigDict, Field

class ProductCreate(BaseModel):
    model_config = ConfigDict(strict=True)

    id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(
        ge=0,
        le=99999999.99,
        allow_inf_nan=False
    )
    quantity: int = Field(ge=0, le=2147483647)
```

### Essential concepts

**BaseModel:** Defines a structured data model with validation.

**Field:** Adds constraints to individual attributes.

**ConfigDict:** Configures model behavior.

**strict=True:** Limits automatic type coercion.

**gt=0:** Value must be greater than zero.

**ge=0:** Value must be greater than or equal to zero.

**from_attributes=True:** Allows Pydantic to populate a response model from object attributes, including SQLAlchemy ORM objects.

### Validation versus business logic

Pydantic validates whether the request has acceptable structure and values.

Business logic determines whether the requested operation is permitted.

For example:

- Negative initial quantity: request validation problem.
- Removing more stock than exists: business rule violation.
- Product ID already exists: uniqueness conflict.

These are different responsibilities.

## 4. FastAPI — Exposing Python Through HTTP

FastAPI allows clients to interact with Python application functionality over HTTP.

Our API exposes:

| Method | Route                          | Purpose          |
| ------ | ------------------------------ | ---------------- |
| GET    | `/products`                    | List products    |
| GET    | `/products/{product_id}`       | Get one product  |
| POST   | `/products`                    | Create product   |
| PATCH  | `/products/{product_id}/stock` | Adjust inventory |
| DELETE | `/products/{product_id}`       | Delete product   |

### HTTP concepts to remember

**GET:** Retrieve resources.

**POST:** Create resources or submit operations.

**PATCH:** Partially update a resource.

**DELETE:** Remove a resource.

### Important status codes

- **201 Created:** Resource successfully created.
- **404 Not Found:** Requested product doesn't exist.
- **409 Conflict:** Request conflicts with existing state, such as a duplicate ID.
- **422 Unprocessable Content:** Request failed validation.

### Dependency injection

Our API uses:

```python
DatabaseSession = Annotated[
    Session,
    Depends(get_db)
]
```

FastAPI calls `get_db()` and supplies a database session to the route.

This avoids manually constructing sessions in every endpoint.

It also makes testing easier because FastAPI dependencies can be overridden.

## 5. SQLAlchemy — Mapping Python Objects to Database Tables

We introduced SQLAlchemy to replace the dictionary as the API's persistence mechanism.

The `Product` model represents a PostgreSQL table.

Conceptually:

```text
Python Product object
        |
        v
SQLAlchemy ORM mapping
        |
        v
PostgreSQL products table
```

### Table structure

| Column   | PostgreSQL type  | Rules       |
| -------- | ---------------- | ----------- |
| id       | INTEGER IDENTITY | Primary key |
| name     | VARCHAR(100)     | Required    |
| price    | NUMERIC(10,2)    | Nonnegative |
| quantity | INTEGER          | Nonnegative |

### SQLAlchemy terminology

**DeclarativeBase:** Base class for defining ORM models.

**Mapped:** Type annotation identifying ORM-managed attributes.

**mapped_column:** Declares how a Python attribute maps to a database column.

**Session:** Manages ORM interactions and transaction state.

**select():** Constructs SQL queries.

**session.get():** Retrieves an ORM object by primary key.

### Why use Decimal for prices?

PostgreSQL `NUMERIC(10,2)` represents fixed-precision decimal values.

SQLAlchemy maps this naturally to Python `Decimal`.

Binary floating-point numbers can introduce representation inaccuracies, making `Decimal` preferable for monetary values.

One future improvement would be using `Decimal` throughout the request and persistence layers rather than accepting a `float` request price.

## 6. Repository Pattern — Separating HTTP From Persistence

We introduced `product_repository.py`.

Its responsibility is to interact with the database.

Examples include:

```python
def get_product(session, product_id):
    return session.get(Product, product_id)
```

And:

```python
def list_products(session):
    return list(
        session.scalars(
            select(Product).order_by(Product.id)
        ).all()
    )
```

The FastAPI route should not need to know the details of every SQL query.

### Why this separation matters

Imagine replacing PostgreSQL with a different persistence mechanism.

If database queries are scattered throughout HTTP routes, the change is harder.

With a repository, persistence behavior is concentrated in one layer.

This is a useful separation of concerns, although it does add another module to maintain.

## 7. End-to-End Request Flow

Consider this request:

```http
PATCH /products/101/stock
Content-Type: application/json
```

```json
{
  "quantity_change": -2
}
```

The execution flow:

1. The client sends an HTTP request.
2. FastAPI matches the endpoint.
3. Pydantic validates the request body.
4. FastAPI injects a SQLAlchemy session.
5. The route calls `update_stock()` in the repository.
6. SQLAlchemy executes the SQL statement.
7. PostgreSQL evaluates the stock condition and updates the row if allowed.
8. The repository commits the successful transaction.
9. The updated product is retrieved.
10. FastAPI serializes and returns the response.

If the product doesn't exist or stock would become negative, the repository raises the appropriate domain error and the API maps it to an HTTP error response.

**You should be able to explain this flow without looking at the code.**

## 8. Database Transactions

Transactions are one of the most important concepts in backend development.

### `session.add()`

Registers an ORM object for persistence.

It does not by itself guarantee the object is saved permanently.

### `session.flush()`

Sends pending SQL statements to the database within the current transaction.

The changes are not yet committed.

### `session.commit()`

Commits the transaction.

Successful committed changes become durable according to the database's guarantees.

### `session.rollback()`

Reverses uncommitted transaction changes.

It is also important for recovering a session after certain database errors.

### `session.refresh()`

Reloads an ORM object's attributes from the database.

### Example

```python
product = session.get(Product, 101)

product.name = "Updated Keyboard"

session.flush()
session.rollback()
```

Assuming the original name was `"Keyboard"`, the database retains that original name after the rollback.

**Critical distinction:** `flush()` is not `commit()`.

## 9. Atomic Inventory Updates

Inventory management introduces a concurrency problem.

Suppose a product has 10 units.

Two requests arrive at nearly the same time.

A naive implementation might:

1. Read quantity.
2. Calculate a new quantity in Python.
3. Write the new value.

Both requests could read the same old value and overwrite each other's changes.

Our repository instead performs an atomic SQL update.

Conceptually:

```sql
UPDATE products
SET quantity = quantity + :change
WHERE id = :product_id
  AND quantity + :change >= 0
RETURNING id;
```

The condition and update are evaluated together by PostgreSQL.

This prevents the operation from producing negative stock through that update statement.

### Important distinction

The atomic SQL approach is stronger than a naive read-modify-write implementation.

However, we did not complete comprehensive parallel-load testing.

Don't confuse a sound concurrency design with proof that every concurrent scenario has been tested.

## 10. PostgreSQL and Docker

We used PostgreSQL 18 in Docker.

The development configuration included:

- Container: `inventory-postgres`
- Development database: `inventory_db`
- Test database: `inventory_test_db`
- Host port: `5433`
- Container port: `5432`
- Named Docker volume for persistent database storage.

### Why port 5433?

Host port 5432 was already occupied.

We mapped PostgreSQL's internal port 5432 to host port 5433.

```text
Mac localhost:5433
        |
        v
Docker container:5432
        |
        v
PostgreSQL
```

The container can still use PostgreSQL's normal internal port.

### Why a Docker volume?

Without persistent storage, deleting and recreating a container can destroy database files.

A named volume separates stored data from the container lifecycle.

### Environment variables

Database credentials and connection settings are loaded from `.env`.

Never commit real credentials.

The development and test databases must remain separate.

## 11. Database Testing

We used pytest to verify API behavior against PostgreSQL.

The tests included scenarios for:

- Product creation.
- Product retrieval.
- Product listing.
- Duplicate IDs.
- Stock updates.
- Insufficient inventory.
- Product deletion.
- Missing products.
- Invalid request data.

### Test isolation

Our pytest setup uses:

1. A separate PostgreSQL test database.
2. A fixture that checks the active database name.
3. A SQLAlchemy connection and outer transaction.
4. A test session using savepoints.
5. A FastAPI dependency override.
6. Transaction rollback after each test.

This helps prevent one test from affecting another or modifying development data.

We verified that a test-created product did not remain after the test run.

### Why verify the database name?

A misconfigured test connection could accidentally point to the development database.

Tests that create, update, and delete records could then damage real development data.

Checking the active database name provides a safety barrier.

### Testing limitation

Our fixture creates tables through SQLAlchemy metadata rather than exclusively through Alembic migrations.

We verified migration-based schema creation separately.

## 12. Alembic — Database Schema Migrations

Alembic manages version-controlled changes to database structure.

### Why migrations matter

Without migrations, developers may manually change databases and end up with inconsistent schemas.

Migrations record how the schema evolves.

Our initial migration revision was:

`49f04f6e31ff`

It creates the `products` table with its columns, primary key, identity definition, and nonnegative constraints.

### Commands

```bash
alembic revision -m "description"
```

Creates a new empty migration revision.

```bash
alembic history
```

Displays revisions defined in migration files.

```bash
alembic current
```

Displays the revision recorded in the connected database.

```bash
alembic upgrade head
```

Applies pending migrations.

```bash
alembic stamp head
```

Records a revision without executing its schema changes.

```bash
alembic check
```

Checks for detectable differences between the SQLAlchemy model metadata and the database schema.

### Upgrade versus stamp

For a new database, `upgrade head` executes the migration to create the schema.

For an existing database that already matches the schema, `stamp head` can establish the migration baseline.

**Never blindly stamp a database.** It can falsely mark a migration as applied even when the schema is incorrect.

## 13. Debugging Lessons From the Project

### Bug 1 — Docker command not found

**Symptom:** Docker worked in Mac Terminal but not in VS Code's zsh terminal.

**Cause:** The Docker executable directory was missing from the shell's PATH.

**Resolution:** Add the Docker executable directory to PATH in `~/.zshrc` and reload the shell configuration.

**Lesson:** A command lookup failure is not necessarily an application failure.

### Bug 2 — PostgreSQL port conflict

**Symptom:** Host port 5432 was unavailable.

**Cause:** Another process was using that port.

**Resolution:** Use host port 5433 mapped to container port 5432.

**Lesson:** Understand the distinction between host networking and container networking.

### Bug 3 — Test database did not exist

**Symptom:** Database connection failed during test setup.

**Cause:** `inventory_test_db` had not been created.

**Resolution:** Inspect PostgreSQL's database list and create the missing database.

**Lesson:** Verify infrastructure prerequisites before changing application code.

### Bug 4 — Alembic placeholder driver

**Symptom:**

```text
Can't load plugin: sqlalchemy.dialects:driver
```

**Cause:** Alembic's default configuration still referenced a placeholder database URL.

**Resolution:** Configure Alembic to reuse the application's SQLAlchemy engine and load `Base.metadata`.

**Lesson:** Configuration errors can occur before any application or migration logic executes.

### Bug 5 — Alembic did nothing

**Symptom:** `alembic upgrade head` exited successfully, but neither the `products` table nor `alembic_version` existed in the target database.

**Cause:** `run_migrations_online()` was defined but never called.

**Resolution:** Add the execution block to the bottom of `migrations/env.py`:

```python
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Lesson:** Defining a function does not execute it.

This was one of the most important debugging lessons in the project.

### Bug 6 — Misleading success

**Symptom:** A command returned without an error, but the expected database changes were absent.

**Cause:** The expected execution path had not run.

**Resolution:** Inspect actual database tables and migration history rather than trusting command exit status.

**Lesson:** Successful execution and correct system state are not the same thing.

## 14. Architectural Decisions and Tradeoffs

| Decision                       | Reason                                  | Tradeoff                                      |
| ------------------------------ | --------------------------------------- | --------------------------------------------- |
| Start with dictionary CRUD     | Learn Python fundamentals independently | No durable persistence                        |
| Use FastAPI                    | Expose Python operations through HTTP   | Requires understanding routing and validation |
| Use Pydantic                   | Validate request structure              | Does not replace business rules               |
| Introduce repository functions | Separate persistence from HTTP          | Additional abstraction                        |
| Use SQLAlchemy                 | Map Python objects to relational tables | Requires transaction knowledge                |
| Use PostgreSQL                 | Learn real relational persistence       | More setup and operational complexity         |
| Use Docker                     | Reproducible database environment       | Networking and volume management              |
| Use atomic stock updates       | Protect inventory invariants            | More complex SQL and error handling           |
| Use a separate test database   | Protect development data                | Additional fixture setup                      |
| Use Alembic                    | Version-control database schemas        | Migration history must be maintained          |

## 15. What We Haven't Proven

Inventory API v1 is a learning project, not a production-ready service.

We haven't fully verified:

- Database outage recovery.
- Concurrent behavior under parallel load.
- Authentication and authorization.
- Rate limiting.
- Production deployment.
- Monitoring and alerting.
- Performance under realistic traffic.

These are reasonable future improvements, but they are not necessary to close this apprenticeship milestone.

## 16. Engineering Review Questions

Answer these without copying code:

1. What's the difference between `products.get(id)` and `products[id]`?
2. What does Pydantic validate that ordinary Python dictionaries don't?
3. Why do we separate FastAPI routes from repository functions?
4. What is a SQLAlchemy Session?
5. What happens when you call `session.flush()`?
6. How is `commit()` different from `rollback()`?
7. What is a primary key?
8. Why use PostgreSQL `NUMERIC` for prices?
9. How does dependency injection work in FastAPI?
10. Trace a request from FastAPI to PostgreSQL and back.
11. Why is an atomic stock update safer than read-modify-write in Python?
12. What is the difference between HTTP 404, 409, and 422?
13. Why must tests use a separate database?
14. What's the difference between `alembic history` and `alembic current`?
15. Why did our initial Alembic migration silently do nothing?
16. What's the difference between `alembic stamp head` and `alembic upgrade head`?
17. How did we prove our migration could recreate the schema?

## 17. What You Should Be Able to Do Independently

After this project, your next engineering challenge is not writing more tests for Inventory API.

It's proving you can independently:

- Translate requirements into Python functions.
- Define Pydantic request and response models.
- Create a FastAPI endpoint.
- Write a SQLAlchemy query.
- Handle database transactions.
- Map domain errors to HTTP responses.
- Trace and debug a request across application layers.
- Explain why your architecture works.

A valuable follow-up exercise is rebuilding one endpoint from a written requirement without copying the implementation.

**The objective is independent engineering competence, not memorizing code or maximizing test count.**

---

_Prepared from the completed Inventory API apprenticeship and the repository structure provided. Review exact commands and implementation details against the current source files before treating this as a complete source-code audit._
