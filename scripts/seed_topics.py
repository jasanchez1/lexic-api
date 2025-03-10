import sys
import os
from pathlib import Path
from uuid import UUID

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set the DATABASE_URL environment variable for local development if not already set
if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/lexic_db"

from app.db.database import SessionLocal
from app.models.topic import Topic
from app.db.repositories import topics as topics_repository
from app.schemas.topic import TopicCreate

# Legal topics data for Chile
TOPICS = [
    {
        "name": "Divorcios y Pensión Alimenticia",
        "slug": "divorcios-pension-alimenticia",
        "description": "Procesos de separación y acuerdos de manutención para hijos, pensiones de alimentos.",
        "subtopics": [
            {
                "name": "Divorcio",
                "slug": "divorcio",
                "description": "Procesos de separación matrimonial"
            },
            {
                "name": "Pensión de Alimentos",
                "slug": "pension-alimentos",
                "description": "Acuerdos y disputas sobre manutención infantil"
            },
            {
                "name": "Custodia de Menores",
                "slug": "custodia-menores",
                "description": "Determinación de la custodia y régimen de visitas"
            }
        ]
    },
    {
        "name": "Derecho Laboral",
        "slug": "derecho-laboral",
        "description": "Derechos y obligaciones en relaciones laborales, despidos, finiquitos y compensaciones.",
        "subtopics": [
            {
                "name": "Despido Injustificado",
                "slug": "despido-injustificado",
                "description": "Reclamos por despidos sin justa causa"
            },
            {
                "name": "Acoso Laboral",
                "slug": "acoso-laboral",
                "description": "Situaciones de acoso en el trabajo"
            },
            {
                "name": "Contratos Laborales",
                "slug": "contratos-laborales",
                "description": "Consultas sobre términos contractuales laborales"
            }
        ]
    },
    {
        "name": "Derecho Civil",
        "slug": "derecho-civil",
        "description": "Contratos civiles, arrendamientos, compraventa de propiedades y herencias.",
        "subtopics": [
            {
                "name": "Arrendamientos",
                "slug": "arrendamientos",
                "description": "Contratos de arriendo y disputas relacionadas"
            },
            {
                "name": "Compraventa de Propiedades",
                "slug": "compraventa-propiedades",
                "description": "Trámites y problemas en transacciones inmobiliarias"
            },
            {
                "name": "Herencias y Testamentos",
                "slug": "herencias-testamentos",
                "description": "Sucesiones, testamentos y disputas hereditarias"
            }
        ]
    },
    {
        "name": "Derecho Penal",
        "slug": "derecho-penal",
        "description": "Defensa en causas penales, delitos, recursos y procedimientos penales.",
        "subtopics": [
            {
                "name": "Delitos Económicos",
                "slug": "delitos-economicos",
                "description": "Fraudes, estafas y otros delitos financieros"
            },
            {
                "name": "Defensa Criminal",
                "slug": "defensa-criminal",
                "description": "Representación legal en causas penales"
            },
            {
                "name": "Violencia Intrafamiliar",
                "slug": "violencia-intrafamiliar",
                "description": "Casos de violencia doméstica y medidas de protección"
            }
        ]
    },
    {
        "name": "Derecho Comercial",
        "slug": "derecho-comercial",
        "description": "Constitución de empresas, conflictos societarios, propiedad intelectual y contratos mercantiles.",
        "subtopics": [
            {
                "name": "Constitución de Empresas",
                "slug": "constitucion-empresas",
                "description": "Creación y registro de sociedades comerciales"
            },
            {
                "name": "Contratos Comerciales",
                "slug": "contratos-comerciales",
                "description": "Acuerdos y disputas en el ámbito empresarial"
            },
            {
                "name": "Propiedad Intelectual",
                "slug": "propiedad-intelectual",
                "description": "Patentes, marcas y derechos de autor"
            }
        ]
    },
    {
        "name": "Derecho de Consumo",
        "slug": "derecho-consumo",
        "description": "Reclamos por productos defectuosos, incumplimiento de garantías y derechos del consumidor.",
        "subtopics": [
            {
                "name": "Reclamos por Productos",
                "slug": "reclamos-productos",
                "description": "Productos defectuosos o que no cumplen lo prometido"
            },
            {
                "name": "Disputas con Instituciones Financieras",
                "slug": "disputas-financieras",
                "description": "Problemas con bancos, tarjetas de crédito y seguros"
            },
            {
                "name": "Garantías y Devoluciones",
                "slug": "garantias-devoluciones",
                "description": "Derechos del consumidor respecto a garantías"
            }
        ]
    },
    {
        "name": "Derecho Inmobiliario",
        "slug": "derecho-inmobiliario",
        "description": "Transacciones inmobiliarias, problemas con constructoras, escrituración y derechos reales.",
        "subtopics": [
            {
                "name": "Problemas con Constructoras",
                "slug": "problemas-constructoras",
                "description": "Defectos de construcción y retrasos en entrega"
            },
            {
                "name": "Escrituración",
                "slug": "escrituracion",
                "description": "Procesos de escrituración y transferencia de propiedades"
            },
            {
                "name": "Conflictos de Límites",
                "slug": "conflictos-limites",
                "description": "Disputas sobre deslindes y servidumbres"
            }
        ]
    },
    {
        "name": "Derecho Migratorio",
        "slug": "derecho-migratorio",
        "description": "Visas, residencia, nacionalidad y problemas migratorios.",
        "subtopics": [
            {
                "name": "Visas de Trabajo",
                "slug": "visas-trabajo",
                "description": "Permisos para trabajar en Chile"
            },
            {
                "name": "Residencia Permanente",
                "slug": "residencia-permanente",
                "description": "Procesos para obtener residencia definitiva"
            },
            {
                "name": "Nacionalidad Chilena",
                "slug": "nacionalidad-chilena",
                "description": "Requisitos y trámites para obtener la nacionalidad"
            }
        ]
    }
]

def seed_topics():
    """Seed legal topics data into database"""
    db = SessionLocal()
    
    try:
        # Check if topics already exist
        existing_topics = db.query(Topic).count()
        if existing_topics > 0:
            print(f"Database already has {existing_topics} topics. Skipping seeding.")
            return
        
        print("Seeding legal topics...")
        count = 0
        
        # First, create main topics
        topic_id_map = {}  # To store main topic IDs for subtopics association
        
        for topic_data in TOPICS:
            # Extract subtopics before creating the main topic
            subtopics = topic_data.pop("subtopics", [])
            
            # Create main topic
            topic_in = TopicCreate(
                name=topic_data["name"],
                slug=topic_data["slug"],
                description=topic_data["description"],
                parent_id=None
            )
            created_topic = topics_repository.create_topic(db, topic_in)
            topic_id_map[topic_data["slug"]] = created_topic.id
            count += 1
            
            # Create subtopics for this main topic
            for subtopic in subtopics:
                subtopic_in = TopicCreate(
                    name=subtopic["name"],
                    slug=subtopic["slug"],
                    description=subtopic["description"],
                    parent_id=created_topic.id
                )
                topics_repository.create_topic(db, subtopic_in)
                count += 1
            
        print(f"Successfully seeded {count} topics")
        
    except Exception as e:
        print(f"Error seeding topics: {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_topics()

