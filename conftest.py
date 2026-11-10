
import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session

from database import get_db
from main import app
from models import Base


load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is missing")


test_engine = create_engine(TEST_DATABASE_URL)


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    with test_engine.connect() as connection:
        database_name = connection.scalar(
            text("SELECT current_database()")
        )

        if database_name != "inventory_test_db":
            raise RuntimeError(
                "Refusing to run tests against a non-test database"
            )

    Base.metadata.create_all(bind=test_engine)

    yield

    test_engine.dispose()


@pytest.fixture
def db_session(prepare_test_database):
    connection = test_engine.connect()
    transaction = connection.begin()

    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
