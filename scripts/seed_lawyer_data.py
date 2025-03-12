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
    os.environ["DATABASE_URL"] = (
        "postgresql://postgres:postgres@localhost:5432/lexic_db"
    )

from app.db.database import SessionLocal
from app.models.lawyer import Lawyer
from app.models.user import User
from app.models.review import Review
from app.models.experience import Education, WorkExperience, Achievement
from app.models.message import Message, Call
from app.schemas.review import ReviewCreate, ReviewAuthor
from app.schemas.experience import (
    EducationCreate,
    WorkExperienceCreate,
    AchievementCreate,
)
from app.schemas.message import MessageCreate, CallCreate
from app.db.repositories import reviews as reviews_repository
from app.db.repositories import experience as experience_repository
from app.db.repositories import messages as messages_repository
from app.db.repositories import lawyers as lawyers_repository

# Sample data for lawyer reviews
REVIEWS = [
    {
        "rating": 5,
        "title": "Excelente asesoría en mi caso de divorcio",
        "content": "El abogado me brindó un servicio excepcional durante todo mi proceso de divorcio. Siempre estuvo disponible para responder mis dudas y me mantuvo informado en cada etapa. Altamente recomendado.",
        "author": {"name": "Juan Pérez", "email": "juan.perez@example.com"},
        "is_hired": True,
        "is_anonymous": False,
    },
    {
        "rating": 4,
        "title": "Muy buena atención y profesionalismo",
        "content": "Me ayudó con un tema laboral complejo y logró un buen resultado. Lo único que podría mejorar es la rapidez en las respuestas, pero en general quedé muy satisfecho con el servicio.",
        "author": {"name": "María González", "email": "maria.gonzalez@example.com"},
        "is_hired": True,
        "is_anonymous": False,
    },
    {
        "rating": 5,
        "title": "Excelente experiencia",
        "content": "Resolvió mi caso de manera eficiente y profesional. Muy claro en sus explicaciones y siempre accesible para consultas. Definitivamente lo recomendaría.",
        "author": {"name": "Carlos Rodríguez", "email": "carlos.rodriguez@example.com"},
        "is_hired": True,
        "is_anonymous": False,
    },
    {
        "rating": 3,
        "title": "Buen abogado pero respuestas lentas",
        "content": "Profesionalmente es muy bueno y conoce bien su trabajo, pero a veces tardaba varios días en responder mis mensajes, lo cual me generaba ansiedad.",
        "author": {"name": "Ana Martínez", "email": "ana.martinez@example.com"},
        "is_hired": True,
        "is_anonymous": True,
    },
    {
        "rating": 5,
        "title": "Increíble servicio en mi caso inmobiliario",
        "content": "Me asistió con la compra de una propiedad con varios problemas legales. Su conocimiento y dedicación fueron fundamentales para resolver todo satisfactoriamente.",
        "author": {"name": "Roberto Sánchez", "email": "roberto.sanchez@example.com"},
        "is_hired": True,
        "is_anonymous": False,
    },
    {
        "rating": 1,
        "title": "No recomiendo en absoluto",
        "content": "Mala experiencia. No cumplió con los plazos prometidos y el resultado fue muy por debajo de mis expectativas. Además, la comunicación fue deficiente.",
        "author": {"name": "Laura Torres", "email": "laura.torres@example.com"},
        "is_hired": True,
        "is_anonymous": True,
    },
]

# Sample education data
EDUCATION = [
    {
        "institution": "Universidad de Chile",
        "degree": "Licenciado en Ciencias Jurídicas y Sociales",
        "year": 2015,
        "honors": "Distinción Máxima",
    },
    {
        "institution": "Universidad Católica de Chile",
        "degree": "Magíster en Derecho de Empresas",
        "year": 2018,
        "honors": "Cum Laude",
    },
    {
        "institution": "Universidad de Los Andes",
        "degree": "Licenciatura en Derecho",
        "year": 2016,
        "honors": None,
    },
    {
        "institution": "Universidad Diego Portales",
        "degree": "Magíster en Derecho Penal",
        "year": 2019,
        "honors": "Distinción Académica",
    },
    {
        "institution": "Harvard Law School",
        "degree": "LL.M. (Master of Laws)",
        "year": 2020,
        "honors": None,
    },
]

# Sample work experience data
WORK_EXPERIENCE = [
    {
        "role": "Socio Principal",
        "company": "Libbey Law Offices",
        "start_date": "2023-01",
        "end_date": "Present",
        "description": "Especializado en derecho civil y comercial. Manejo de casos de alta complejidad y representación de clientes corporativos.",
    },
    {
        "role": "Abogado Senior",
        "company": "González & Asociados",
        "start_date": "2020-05",
        "end_date": "2022-12",
        "description": "Responsable del área de litigios civiles y comerciales. Representación de clientes en juicios orales y arbitrajes.",
    },
    {
        "role": "Abogado Asociado",
        "company": "Estudio Jurídico Méndez",
        "start_date": "2018-03",
        "end_date": "2020-04",
        "description": "Especialista en derecho laboral y seguridad social. Asesoría y representación de empresas en conflictos laborales.",
    },
    {
        "role": "Asesor Jurídico",
        "company": "Ministerio de Justicia",
        "start_date": "2016-07",
        "end_date": "2018-02",
        "description": "Asesoría legal en materias de políticas públicas y elaboración de normativas.",
    },
    {
        "role": "Pasante",
        "company": "Tribunal Constitucional",
        "start_date": "2015-09",
        "end_date": "2016-06",
        "description": "Apoyo en investigación jurídica y elaboración de informes para ministros del tribunal.",
    },
]

# Sample achievement data
ACHIEVEMENTS = [
    {
        "title": "Premio Colegio de Abogados - Mejor Tesis",
        "year": 2015,
        "issuer": "Colegio de Abogados de Chile",
    },
    {
        "title": "Reconocimiento a la Excelencia Profesional",
        "year": 2019,
        "issuer": "Asociación de Abogados de Chile",
    },
    {
        "title": "Autor del Libro 'Derecho Civil en la Era Digital'",
        "year": 2021,
        "issuer": "Editorial Jurídica",
    },
    {"title": "Mejor Abogado Joven del Año", "year": 2018, "issuer": "Revista Legal"},
    {
        "title": "Beca de Excelencia para Estudios en el Extranjero",
        "year": 2017,
        "issuer": "Fundación Fulbright",
    },
]

# Sample message data
MESSAGES = [
    {
        "name": "Diego Fernández",
        "email": "diego.fernandez@example.com",
        "phone": "+56 9 1234 5678",
        "message": "Necesito asesoría urgente para un problema de despido injustificado. ¿Podría contactarme para agendar una consulta esta semana?",
    },
    {
        "name": "Valentina López",
        "email": "valentina.lopez@example.com",
        "phone": "+56 9 8765 4321",
        "message": "Estoy interesada en recibir asesoramiento legal para la compra de una propiedad con algunas complicaciones legales. ¿Tiene disponibilidad para una consulta?",
    },
    {
        "name": "Sebastián Morales",
        "email": "sebastian.morales@example.com",
        "phone": "+56 9 2468 1357",
        "message": "Quisiera consultarle sobre un tema de herencia. Mi padre falleció hace un mes y necesito orientación sobre los trámites a seguir.",
    },
    {
        "name": "Camila Rojas",
        "email": "camila.rojas@example.com",
        "phone": "+56 9 1357 2468",
        "message": "Vi su perfil y me interesa su experiencia en derecho comercial. Soy dueña de una pequeña empresa y necesito asesoría para un contrato importante.",
    },
    {
        "name": "Matías Silva",
        "email": "matias.silva@example.com",
        "phone": "+56 9 9876 5432",
        "message": "Tengo un problema con mi arrendador que no quiere devolver la garantía. ¿Podría ayudarme con este caso? Necesitaría una respuesta pronto.",
    },
]

# Sample call data (timestamps will be generated dynamically)
CALL_COMPLETED_STATUS = [True, False]  # For random selection


def seed_lawyer_data():
    """Seed lawyer related data (reviews, experience, messages) into database"""
    db = SessionLocal()

    try:
        # Get all lawyers
        lawyers = db.query(Lawyer).all()
        if not lawyers:
            print("No lawyers found in database. Please seed lawyers first.")
            return

        # Get all users
        users = db.query(User).all()
        if not users:
            print("No users found in database. Please create some users first.")
            return

        # Set a base date for created_at
        base_date = datetime.now(timezone.utc) - timedelta(days=180)

        # Seed reviews
        reviews_count = db.query(Review).count()
        if reviews_count > 0:
            print(
                f"Database already has {reviews_count} reviews. Skipping review seeding."
            )
        else:
            print("Seeding lawyer reviews...")
            count = 0

            for lawyer in lawyers:
                # Each lawyer gets 2-4 reviews
                num_reviews = random.randint(2, 4)
                selected_reviews = random.sample(
                    REVIEWS, min(num_reviews, len(REVIEWS))
                )

                for review_data in selected_reviews:
                    # Generate a random created_at date
                    days_ago = random.randint(1, 180)
                    created_at = base_date + timedelta(days=days_ago)
                    
                    # Select a random user as the author
                    random_user = random.choice(users)

                    # Create review with user_id
                    review_create = ReviewCreate(
                        rating=review_data["rating"],
                        title=review_data["title"],
                        content=review_data["content"],
                        author=ReviewAuthor(**review_data["author"]),
                        is_hired=review_data["is_hired"],
                        is_anonymous=review_data["is_anonymous"],
                        user_id=random_user.id  # Added user_id
                    )
                    
                    db_review = reviews_repository.create_review(
                        db, review_create, lawyer.id
                    )

                    # Update the created_at date
                    db_review.created_at = created_at
                    db_review.updated_at = created_at
                    db.add(db_review)
                    db.commit()
                    
                    # Update lawyer review score
                    lawyers_repository.update_lawyer_review_score(db, lawyer.id, db_review.rating)
                    
                    count += 1

            print(f"Successfully seeded {count} lawyer reviews")

        # Seed education
        education_count = db.query(Education).count()
        if education_count > 0:
            print(
                f"Database already has {education_count} education entries. Skipping education seeding."
            )
        else:
            print("Seeding lawyer education...")
            count = 0

            for lawyer in lawyers:
                # Each lawyer gets 1-2 education entries
                num_education = random.randint(1, 2)
                selected_education = random.sample(
                    EDUCATION, min(num_education, len(EDUCATION))
                )

                for education_data in selected_education:
                    # Create education entry
                    education_create = EducationCreate(**education_data)
                    db_education = experience_repository.create_education(
                        db, education_create, lawyer.id
                    )
                    count += 1

            print(f"Successfully seeded {count} lawyer education entries")

        # Seed work experience
        work_exp_count = db.query(WorkExperience).count()
        if work_exp_count > 0:
            print(
                f"Database already has {work_exp_count} work experience entries. Skipping work experience seeding."
            )
        else:
            print("Seeding lawyer work experience...")
            count = 0

            for lawyer in lawyers:
                # Each lawyer gets 2-3 work experience entries
                num_experiences = random.randint(2, 3)
                selected_experiences = random.sample(
                    WORK_EXPERIENCE, min(num_experiences, len(WORK_EXPERIENCE))
                )

                for experience_data in selected_experiences:
                    # Create work experience entry
                    experience_create = WorkExperienceCreate(**experience_data)
                    db_experience = experience_repository.create_work_experience(
                        db, experience_create, lawyer.id
                    )
                    count += 1

            print(f"Successfully seeded {count} lawyer work experience entries")

        # Seed achievements
        achievement_count = db.query(Achievement).count()
        if achievement_count > 0:
            print(
                f"Database already has {achievement_count} achievement entries. Skipping achievement seeding."
            )
        else:
            print("Seeding lawyer achievements...")
            count = 0

            for lawyer in lawyers:
                # Each lawyer gets 1-3 achievements
                num_achievements = random.randint(1, 3)
                selected_achievements = random.sample(
                    ACHIEVEMENTS, min(num_achievements, len(ACHIEVEMENTS))
                )

                for achievement_data in selected_achievements:
                    # Create achievement entry
                    achievement_create = AchievementCreate(**achievement_data)
                    db_achievement = experience_repository.create_achievement(
                        db, achievement_create, lawyer.id
                    )
                    count += 1

            print(f"Successfully seeded {count} lawyer achievement entries")

        # Seed messages
        message_count = db.query(Message).count()
        if message_count > 0:
            print(
                f"Database already has {message_count} messages. Skipping message seeding."
            )
        else:
            print("Seeding lawyer messages...")
            count = 0

            for lawyer in lawyers:
                # Each lawyer gets 2-4 messages
                num_messages = random.randint(2, 4)
                selected_messages = random.sample(
                    MESSAGES, min(num_messages, len(MESSAGES))
                )

                for message_data in selected_messages:
                    # Generate a random created_at date
                    days_ago = random.randint(1, 90)
                    created_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
                    
                    # Select a random user as the sender
                    random_user = random.choice(users)

                    # Create message with user_id
                    message_create = MessageCreate(
                        name=message_data["name"],
                        email=message_data["email"],
                        phone=message_data.get("phone"),
                        message=message_data["message"],
                        user_id=random_user.id  # Added user_id
                    )
                    
                    db_message = messages_repository.create_message(
                        db, message_create, lawyer.id
                    )

                    # Update the created_at date
                    db_message.created_at = created_at
                    db_message.updated_at = created_at

                    # Randomly mark some messages as read
                    db_message.read = random.choice([True, False])

                    db.add(db_message)
                    db.commit()
                    count += 1

            print(f"Successfully seeded {count} lawyer messages")

        # Seed calls
        call_count = db.query(Call).count()
        if call_count > 0:
            print(f"Database already has {call_count} calls. Skipping call seeding.")
        else:
            print("Seeding lawyer calls...")
            count = 0

            for lawyer in lawyers:
                # Each lawyer gets 3-8 calls
                num_calls = random.randint(3, 8)

                for _ in range(num_calls):
                    # Generate a random timestamp within the last 90 days
                    days_ago = random.randint(1, 90)
                    timestamp = datetime.now(timezone.utc) - timedelta(days=days_ago)

                    # Create call
                    call_create = CallCreate(
                        completed=random.choice(CALL_COMPLETED_STATUS),
                        timestamp=timestamp,
                    )
                    db_call = messages_repository.create_call(
                        db, call_create, lawyer.id
                    )
                    count += 1

            print(f"Successfully seeded {count} lawyer calls")

    except Exception as e:
        print(f"Error seeding lawyer data: {e}")
        import traceback

        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    seed_lawyer_data()