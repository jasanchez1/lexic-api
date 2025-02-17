from src.database import engine
from sqlalchemy import text

def test_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Database connection successful!")

if __name__ == "__main__":
    test_connection()