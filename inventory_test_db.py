
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing")

test_database_url = DATABASE_URL.rsplit("/", 1)[0] + "/inventory_test_db"

if not test_database_url.endswith("/inventory_test_db"):
    raise RuntimeError("Unsafe test database URL")

engine = create_engine(test_database_url)

with engine.connect() as connection:
    database_name = connection.scalar(
        text("SELECT current_database()")
    )

    print(f"Connected to: {database_name}")

    if database_name != "inventory_test_db":
        raise RuntimeError("Connected to the wrong database!")

engine.dispose()
