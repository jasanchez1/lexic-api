# scripts/seed_lawyers.py
import sys
import os
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set the DATABASE_URL environment variable for local development if not already set
if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/lexic_db"

from app.db.database import SessionLocal
from app.models import PracticeArea, Lawyer, lawyer_area_association
from app.db.repositories import lawyers as lawyers_repository
from app.schemas.lawyer import LawyerCreate, LawyerAreaAssociation

# Sample lawyer data
LAWYERS = [
    {
        "name": "Gabriel Boric",
        "title": "Abogado Civil, Universidad de Chile",
        "bio": "Experto en derecho civil con amplia experiencia en casos de propiedad y contratos.",
        "phone": "+56 9 1234 5678",
        "email": "gboric@example.com",
        "city": "Santiago",
        "image_url": "https://www.cidob.org/sites/default/files/styles/max_width_290/public/gabriel_boric_font.jpg.webp",
        "languages": ["Español", "Inglés", "Portugués"],
        "catchphrase": "Soluciones legales con dedicación y compromiso",
        "professional_start_date": "2021-03-11"
    },
    {
        "name": "Carolina Tohá",
        "title": "Abogada Familiar, Universidad Católica",
        "bio": "Especialista en derecho de familia, divorcio y custodia de menores.",
        "phone": "+56 9 2345 6789",
        "email": "ctoha@example.com",
        "city": "Santiago",
        "image_url": "https://www.latercera.com/resizer/ORnAeU2BvM50D3TmbSsfYq6zW8o=/arc-anglerfish-arc2-prod-copesa/public/VBKOKZLWHFEL5DOHCGVXMLSWCA.jpeg",
        "languages": ["Español", "Inglés"],
        "catchphrase": "Protegiendo a las familias, construyendo futuro",
        "professional_start_date": "2018-05-20"
    },
    {
        "name": "Izkia Siches",
        "title": "Abogada Laboral, Universidad de Concepción",
        "bio": "Especializada en derecho laboral y seguridad social.",
        "phone": "+56 9 3456 7890",
        "email": "isiches@example.com",
        "city": "Concepción",
        "image_url": "https://www.uahurtado.cl/wp-content/uploads/2023/03/IMG_20220311_121411-1.jpg",
        "languages": ["Español"],
        "catchphrase": "Defendiendo tus derechos laborales",
        "professional_start_date": "2019-08-15"
    },
    {
        "name": "Camila Vallejo",
        "title": "Abogada Penal, Universidad de Valparaíso",
        "bio": "Abogada especializada en defensa penal y compliance corporativo.",
        "phone": "+56 9 4567 8901",
        "email": "cvallejo@example.com",
        "city": "Valparaíso",
        "image_url": "https://www.mseg.gob.cl/wp-content/uploads/2021/04/Camila-Vallejo-2.jpeg",
        "languages": ["Español", "Francés"],
        "catchphrase": "Defensa legal estratégica y efectiva",
        "professional_start_date": "2017-11-10"
    },
    {
        "name": "José Antonio Kast",
        "title": "Abogado Tributario, Universidad Católica",
        "bio": "Experto en planificación fiscal y defensa tributaria.",
        "phone": "+56 9 5678 9012",
        "email": "jakast@example.com",
        "city": "Santiago",
        "image_url": "https://i.ibb.co/s6Wbcg0/jose-antonio-kast-1.jpg",
        "languages": ["Español", "Alemán"],
        "catchphrase": "Maximizando la eficiencia fiscal legalmente",
        "professional_start_date": "2015-02-05"
    }
]

def seed_lawyers():
    """Seed lawyer data into database"""
    db = SessionLocal()
    
    try:
        # Check if lawyers already exist
        existing_lawyers = db.query(Lawyer).count()
        if existing_lawyers > 0:
            print(f"Database already has {existing_lawyers} lawyers. Skipping seeding.")
            return
        
        # Get practice areas to assign to lawyers
        areas = db.query(PracticeArea).all()
        if not areas:
            print("No practice areas found. Please run seed_practice_areas.py first.")
            return
        
        print("Seeding lawyers...")
        count = 0
        
        for lawyer_data in LAWYERS:
            # Convert professional_start_date to datetime
            if "professional_start_date" in lawyer_data:
                start_date = lawyer_data["professional_start_date"]
                lawyer_data["professional_start_date"] = datetime.fromisoformat(start_date)
            
            # Create lawyer without areas first
            lawyer_in = LawyerCreate(**lawyer_data)
            lawyer = lawyers_repository.create_lawyer(db, lawyer_in)
            
            # Randomly assign 2-4 practice areas to each lawyer
            num_areas = random.randint(2, 4)
            selected_areas = random.sample(areas, num_areas)
            
            for area in selected_areas:
                # Random experience score between 30 and 95
                experience_score = random.randint(30, 95)
                
                # Add to association table
                db.execute(
                    lawyer_area_association.insert().values(
                        lawyer_id=lawyer.id,
                        area_id=area.id,
                        experience_score=experience_score
                    )
                )
            
            db.commit()
            count += 1
            
        print(f"Successfully seeded {count} lawyers")
        
    except Exception as e:
        print(f"Error seeding lawyers: {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_lawyers()