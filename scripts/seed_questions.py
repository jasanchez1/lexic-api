# scripts/seed_questions.py
import sys
import os
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set the DATABASE_URL environment variable for local development if not already set
if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/lexic_db"

from app.db.database import SessionLocal
from app.models.question import Question, PlanToHire
from app.models.topic import Topic, QuestionTopic
from app.models.user import User
from app.db.repositories import questions as questions_repository
from app.schemas.question import QuestionCreate

# Sample questions data
QUESTIONS = [
    {
        "title": "¿Puedo modificar el monto de pensión de alimentos?",
        "content": "Hace dos años se fijó una pensión de alimentos para mis hijos, pero ahora mis ingresos han disminuido considerablemente debido a un cambio de trabajo. ¿Es posible solicitar una reducción del monto? ¿Cuál es el procedimiento y qué factores considera el juez?",
        "topic_slugs": ["pension-alimentos", "divorcios-pension-alimenticia"],
        "location": "Santiago, Chile",
        "plan_to_hire": "maybe"
    },
    {
        "title": "Despido sin aviso previo, ¿qué derechos tengo?",
        "content": "Fui despedido ayer sin ningún tipo de aviso previo. Mi empleador alegó 'bajo rendimiento' aunque nunca recibí evaluaciones negativas formales. Trabajé en la empresa durante 3 años y 8 meses. ¿Qué derechos tengo en este caso y qué indemnizaciones me corresponden?",
        "topic_slugs": ["despido-injustificado", "derecho-laboral"],
        "location": "Valparaíso, Chile",
        "plan_to_hire": "yes"
    },
    {
        "title": "Problemas con contrato de arrendamiento y devolución de garantía",
        "content": "Terminé mi contrato de arrendamiento hace un mes y aún no me devuelven la garantía. El arrendador alega daños en el inmueble que ya existían cuando yo llegué. No hicimos un inventario formal al inicio del contrato. ¿Cómo puedo proceder para recuperar mi dinero?",
        "topic_slugs": ["arrendamientos", "derecho-civil"],
        "location": "Concepción, Chile", 
        "plan_to_hire": "maybe"
    },
    {
        "title": "Disputa por límites de propiedad con vecino",
        "content": "Mi vecino construyó una pared que creo invade mi terreno por aproximadamente 50cm. Tengo las escrituras pero los planos no son muy detallados. ¿Cómo puedo verificar los límites exactos y qué opciones legales tengo si efectivamente hay una invasión?",
        "topic_slugs": ["conflictos-limites", "derecho-inmobiliario"],
        "location": "La Serena, Chile",
        "plan_to_hire": "yes"
    },
    {
        "title": "Producto defectuoso y negativa de la tienda a hacer devolución",
        "content": "Compré un refrigerador que comenzó a fallar a los 15 días. La tienda se niega a cambiar el producto y solo ofrece repararlo. He leído que tengo derecho a devolución o cambio. ¿Qué pasos debo seguir para hacer valer mis derechos como consumidor?",
        "topic_slugs": ["reclamos-productos", "derecho-consumo"],
        "location": "Santiago, Chile",
        "plan_to_hire": "no"
    },
    {
        "title": "Herencia sin testamento, ¿cómo se distribuyen los bienes?",
        "content": "Mi padre falleció recientemente y no dejó testamento. Somos tres hermanos y su actual esposa (no es nuestra madre). ¿Cómo se distribuyen los bienes en este caso según la ley chilena? ¿Qué porcentaje corresponde a cada uno?",
        "topic_slugs": ["herencias-testamentos", "derecho-civil"],
        "location": "Temuco, Chile",
        "plan_to_hire": "yes"
    },
    {
        "title": "Proceso para obtener visa de trabajo en Chile",
        "content": "Soy ingeniero colombiano y me han ofrecido un trabajo en una empresa chilena. ¿Cuál es el proceso para obtener una visa de trabajo? ¿Debo tramitarla desde Colombia o puedo hacerlo estando en Chile con visa de turista? ¿Cuánto tiempo toma aproximadamente?",
        "topic_slugs": ["visas-trabajo", "derecho-migratorio"],
        "location": "Santiago, Chile",
        "plan_to_hire": "maybe"
    },
    {
        "title": "Constitución de una SPA, costos y requisitos",
        "content": "Estoy considerando constituir una Sociedad por Acciones para mi emprendimiento. ¿Cuáles son los requisitos, costos aproximados y tiempos involucrados? ¿Tiene ventajas significativas sobre otros tipos de sociedades para un negocio pequeño que espera crecer?",
        "topic_slugs": ["constitucion-empresas", "derecho-comercial"],
        "location": "Viña del Mar, Chile",
        "plan_to_hire": "yes"
    }
]

def seed_questions():
    """Seed question data into database"""
    db = SessionLocal()
    
    try:
        # Check if questions already exist
        existing_questions = db.query(Question).count()
        if existing_questions > 0:
            print(f"Database already has {existing_questions} questions. Skipping seeding.")
            return
        
        # Get all users (to assign as authors)
        users = db.query(User).all()
        if not users:
            print("No users found in database. Please create some users first.")
            return
        
        # Get topic mapping (slug to ID)
        topics = db.query(Topic).all()
        topic_map = {topic.slug: topic.id for topic in topics}
        
        print("Seeding questions...")
        count = 0
        
        # Set a base date for created_at
        base_date = datetime.now(timezone.utc) - timedelta(days=90)
        
        for question_data in QUESTIONS:
            # Get topic IDs from slugs
            topic_ids = []
            for slug in question_data.pop("topic_slugs"):
                if slug in topic_map:
                    topic_ids.append(topic_map[slug])
                else:
                    print(f"Warning: Topic with slug '{slug}' not found, skipping.")
            
            if not topic_ids:
                print(f"No valid topics found for question '{question_data['title']}', skipping.")
                continue
            
            # Select a random user as the author
            user = random.choice(users)
            
            # Convert plan_to_hire string to enum
            plan_to_hire_str = question_data.pop("plan_to_hire")
            plan_to_hire = PlanToHire.maybe
            if plan_to_hire_str == "yes":
                plan_to_hire = PlanToHire.yes
            elif plan_to_hire_str == "no":
                plan_to_hire = PlanToHire.no
            
            # Create question
            question_create = QuestionCreate(
                title=question_data["title"],
                content=question_data["content"],
                location=question_data["location"],
                plan_to_hire=plan_to_hire,
                topic_ids=topic_ids
            )
            
            # Add a random created_at date
            days_ago = random.randint(0, 60)
            created_at = base_date + timedelta(days=days_ago)
            
            # Create the question
            db_question = questions_repository.create_question(db, question_create, user.id)
            
            # Update the created_at date directly
            db_question.created_at = created_at
            db_question.updated_at = created_at
            db.add(db_question)
            
            # Add a random view count
            db_question.view_count = random.randint(5, 200)
            
            db.commit()
            count += 1
            
        print(f"Successfully seeded {count} questions")
        
    except Exception as e:
        print(f"Error seeding questions: {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_questions()