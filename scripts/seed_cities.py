# scripts/seed_cities.py
import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set the DATABASE_URL environment variable for local development if not already set
if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/lexic_db"

from app.db.database import SessionLocal
from app.models.city import City
from app.db.repositories import cities as cities_repository
from app.schemas.city import CityCreate

# Sample city data for Chile
CITIES = [
    {"name": "Santiago", "slug": "santiago"},
    {"name": "Valparaíso", "slug": "valparaiso"},
    {"name": "Viña del Mar", "slug": "vina-del-mar"},
    {"name": "Concepción", "slug": "concepcion"},
    {"name": "La Serena", "slug": "la-serena"},
    {"name": "Antofagasta", "slug": "antofagasta"},
    {"name": "Temuco", "slug": "temuco"},
    {"name": "Rancagua", "slug": "rancagua"},
    {"name": "Iquique", "slug": "iquique"},
    {"name": "Puerto Montt", "slug": "puerto-montt"},
    {"name": "Arica", "slug": "arica"},
    {"name": "Talca", "slug": "talca"},
    {"name": "Punta Arenas", "slug": "punta-arenas"},
    {"name": "Chillán", "slug": "chillan"},
    {"name": "Calama", "slug": "calama"},
    {"name": "Osorno", "slug": "osorno"},
    {"name": "Coquimbo", "slug": "coquimbo"},
    {"name": "Valdivia", "slug": "valdivia"},
    {"name": "Copiapó", "slug": "copiapo"},
    {"name": "Curicó", "slug": "curico"}
]

def seed_cities():
    """Seed city data into database"""
    db = SessionLocal()
    
    try:
        # Check if cities already exist
        existing_cities = db.query(City).count()
        if existing_cities > 0:
            print(f"Database already has {existing_cities} cities. Skipping seeding.")
            return
        
        print("Seeding cities...")
        count = 0
        
        for city_data in CITIES:
            city_in = CityCreate(**city_data)
            cities_repository.create_city(db, city_in)
            count += 1
            
        print(f"Successfully seeded {count} cities")
        
    except Exception as e:
        print(f"Error seeding cities: {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_cities()

