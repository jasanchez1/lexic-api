import time
import psycopg2
from core.config import settings

def wait_for_db():
    while True:
        try:
            conn = psycopg2.connect(settings.DATABASE_URL)
            conn.close()
            break
        except psycopg2.OperationalError:
            print("Database unavailable, waiting...")
            time.sleep(1)

if __name__ == "__main__":
    wait_for_db()