# scripts/seed_users.py
import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set the DATABASE_URL environment variable for local development if not already set
if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/lexic_db"

from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.schemas.user import UserCreate
from app.db.repositories.users import create_user, get_user_by_email

# Sample user data
USERS = [
    {
        "email": "usuario1@example.com",
        "password": "password123",
        "first_name": "Juan",
        "last_name": "González"
    },
    {
        "email": "usuario2@example.com",
        "password": "password123",
        "first_name": "María",
        "last_name": "Rodríguez"
    },
    {
        "email": "usuario3@example.com",
        "password": "password123",
        "first_name": "Carlos",
        "last_name": "López"
    },
    {
        "email": "usuario4@example.com",
        "password": "password123",
        "first_name": "Ana",
        "last_name": "Martínez"
    },
    {
        "email": "usuario5@example.com",
        "password": "password123",
        "first_name": "Pedro",
        "last_name": "Sánchez"
    },
    {
        "email": "usuario6@example.com",
        "password": "password123",
        "first_name": "Laura",
        "last_name": "Pérez"
    },
    {
        "email": "usuario7@example.com",
        "password": "password123",
        "first_name": "Diego",
        "last_name": "Fernández"
    },
    {
        "email": "usuario8@example.com",
        "password": "password123",
        "first_name": "Valentina",
        "last_name": "Gómez"
    },
    {
        "email": "usuario9@example.com",
        "password": "password123",
        "first_name": "Andrés",
        "last_name": "Torres"
    },
    {
        "email": "usuario10@example.com",
        "password": "password123",
        "first_name": "Camila",
        "last_name": "Silva"
    },
    # Adding more users for good measure
    {
        "email": "admin@lexic.com",
        "password": "admin1234",
        "first_name": "Admin",
        "last_name": "User"
    },
    {
        "email": "tester@lexic.com",
        "password": "test1234",
        "first_name": "Test",
        "last_name": "User"
    },
    {
        "email": "roberto@example.com",
        "password": "password123",
        "first_name": "Roberto",
        "last_name": "Méndez"
    },
    {
        "email": "carolina@example.com",
        "password": "password123",
        "first_name": "Carolina",
        "last_name": "Vega"
    },
    {
        "email": "javier@example.com",
        "password": "password123",
        "first_name": "Javier",
        "last_name": "Muñoz"
    }
]

def seed_users():
    """Seed user data into database"""
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"Database already has {existing_users} users. Skipping seeding.")
            return
        
        print("Seeding users...")
        count = 0
        
        for user_data in USERS:
            # Check if user already exists
            existing_user = get_user_by_email(db, user_data["email"])
            if existing_user:
                print(f"User with email {user_data['email']} already exists. Skipping.")
                continue
                
            # Create user
            user_create = UserCreate(
                email=user_data["email"],
                password=user_data["password"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"]
            )
            
            create_user(db, user_create)
            count += 1
            
        print(f"Successfully seeded {count} users")
        
    except Exception as e:
        print(f"Error seeding users: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()