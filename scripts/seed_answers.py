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
from app.models.question import Question
from app.models.answer import Answer, Reply
from app.models.user import User
from app.models.lawyer import Lawyer
from app.db.repositories import answers as answers_repository
from app.schemas.answer import AnswerCreate, ReplyCreate

# Sample answers
ANSWERS = [
    {
        "content": "Sí, es posible modificar el monto de la pensión de alimentos cuando hay un cambio significativo en las circunstancias económicas. Esto se conoce como una demanda de rebaja de pensión alimenticia.\n\nPara iniciar este proceso, debe presentar una demanda en el tribunal de familia correspondiente, aportando pruebas documentales de su cambio de situación económica (contratos, liquidaciones de sueldo, finiquito, etc.).\n\nEl juez considerará principalmente:\n- La disminución efectiva y comprobable de sus ingresos\n- Que esta disminución no sea voluntaria o de mala fe\n- Las necesidades actuales de los hijos\n- Los ingresos del otro progenitor\n\nLe recomendaría reunir toda la documentación que acredite su nueva situación económica antes de iniciar el proceso. Este trámite puede tardar entre 2 y 4 meses aproximadamente.",
        "is_lawyer": True,
        "is_accepted": True,
        "replies": [
            {
                "content": "Complementando la respuesta anterior, es importante mencionar que los tribunales consideran el principio de proporcionalidad, es decir, que la pensión debe ser proporcional a las posibilidades económicas del alimentante y a las necesidades del alimentado. También puede solicitar medidas urgentes mientras se tramita la causa si su situación es muy apremiante.",
                "is_lawyer": True
            },
            {
                "content": "Muchas gracias por la información. ¿Es recomendable contratar un abogado para este trámite o puedo hacerlo por cuenta propia?",
                "is_lawyer": False
            }
        ]
    },
    {
        "content": "En el caso de un despido sin previo aviso alegando bajo rendimiento, esto podría constituir un despido injustificado según la legislación laboral chilena.\n\nDerechos que le corresponden:\n1. Indemnización por años de servicio: Un mes por cada año trabajado (con tope de 11 años)\n2. Indemnización sustitutiva del aviso previo: Un mes de sueldo\n3. Recargo del 30% sobre la indemnización por años de servicio (por causal improcedente)\n\nEn su caso específico, trabajando 3 años y 8 meses, tendría derecho a:\n- 4 meses de sueldo por años de servicio (se cuenta el año iniciado)\n- 1 mes por aviso previo\n- Recargo del 30% sobre los 4 meses\n\nDebe presentar un reclamo ante la Inspección del Trabajo dentro de 60 días hábiles desde el despido. Recomiendo guardar toda comunicación y documentación relacionada con su desempeño laboral para demostrar que nunca hubo evaluaciones negativas formales.",
        "is_lawyer": True,
        "is_accepted": False,
        "replies": []
    },
    {
        "content": "Respecto a la garantía de arrendamiento, la ley N°18.101 establece que esta debe ser devuelta al finalizar el contrato, a menos que existan daños imputables al arrendatario.\n\nEn su caso, al no existir un inventario inicial, el arrendador enfrenta dificultades para probar que los daños no existían previamente. Le recomiendo:\n\n1. Enviar una carta certificada solicitando formalmente la devolución, detallando que los daños existían previamente\n2. Intentar una mediación a través de SERNAC si el monto es inferior a 10 UTM\n3. Como último recurso, presentar una demanda ante el Juzgado de Policía Local\n\nPara futuros arriendos, siempre documente el estado inicial del inmueble con fotografías fechadas y un inventario firmado por ambas partes. Esto evita precisamente este tipo de disputas.",
        "is_lawyer": True,
        "is_accepted": False,
        "replies": []
    },
    {
        "content": "Para el tema de productos defectuosos, la Ley del Consumidor (19.496) es clara: cuando un producto nuevo presenta fallas dentro de los 3 meses desde la compra, usted tiene derecho a elegir entre:\n\n1. La reparación gratuita\n2. La reposición del producto\n3. La devolución del dinero\n\nLa elección es suya, no de la tienda. Para hacer valer este derecho:\n\n1. Presente un reclamo formal por escrito a la tienda\n2. Si no hay respuesta satisfactoria, acuda al SERNAC\n3. Como último recurso, presente una demanda en el Juzgado de Policía Local\n\nGuarde todas las boletas, garantías y comunicaciones con la tienda. También es útil documentar la falla con videos o fotografías. Este tipo de casos suelen resolverse favorablemente para el consumidor cuando la falla ocurre tan pronto como en su caso.",
        "is_lawyer": False,
        "is_accepted": False,
        "replies": []
    }
]

def seed_answers():
    """Seed answer and reply data into database"""
    db = SessionLocal()
    
    try:
        # Check if answers already exist
        existing_answers = db.query(Answer).count()
        if existing_answers > 0:
            print(f"Database already has {existing_answers} answers. Skipping seeding.")
            return
        
        # Get all questions
        questions = db.query(Question).all()
        if not questions:
            print("No questions found in database. Please seed questions first.")
            return
        
        # Get all users and lawyers
        users = db.query(User).all()
        lawyers = db.query(Lawyer).all()
        
        if not users:
            print("No users found in database. Please create some users first.")
            return
        
        if not lawyers:
            print("No lawyers found in database. This is not blocking, but lawyer answers won't have lawyer_id.")
        
        print("Seeding answers and replies...")
        answer_count = 0
        reply_count = 0
        
        # Set a base date for created_at
        base_date = datetime.now(timezone.utc) - timedelta(days=60)
        
        # Randomly assign answers to questions
        for question in questions:
            # Each question gets 1-3 answers
            num_answers = random.randint(1, 3)
            available_answers = random.sample(ANSWERS, min(num_answers, len(ANSWERS)))
            
            for i, answer_data in enumerate(available_answers):
                # Select a random user as the author
                user = random.choice(users)
                
                # Get lawyer_id if answer is from a lawyer
                lawyer_id = None
                if answer_data["is_lawyer"] and lawyers:
                    lawyer = random.choice(lawyers)
                    lawyer_id = lawyer.id
                
                # Create answer
                answer_create = AnswerCreate(
                    content=answer_data["content"],
                    lawyer_id=lawyer_id
                )
                
                # Add a random created_at date after the question date
                days_after_question = random.randint(1, 14)
                created_at = question.created_at + timedelta(days=days_after_question)
                if created_at > datetime.now():
                    created_at = datetime.now(tz=timezone.utc) - timedelta(days=random.randint(1, 7))
                
                # Create the answer
                db_answer = answers_repository.create_answer(db, answer_create, question.id, user.id)
                
                # Update the created_at date directly
                db_answer.created_at = created_at
                db_answer.updated_at = created_at
                
                # Set as accepted if it's the first answer and is_accepted is True
                if i == 0 and answer_data["is_accepted"]:
                    db_answer.is_accepted = True
                
                db.add(db_answer)
                db.commit()
                answer_count += 1
                
                # Add replies if any
                for reply_data in answer_data.get("replies", []):
                    # Select a random user for the reply
                    reply_user = random.choice(users)
                    
                    # If reply is from lawyer, try to use a lawyer
                    if reply_data["is_lawyer"] and lawyers:
                        lawyer = random.choice(lawyers)
                        # Find the user associated with this lawyer if any
                        if lawyer.user_id:
                            lawyer_user = db.query(User).filter(User.id == lawyer.user_id).first()
                            if lawyer_user:
                                reply_user = lawyer_user
                    
                    # Create reply
                    reply_create = ReplyCreate(
                        content=reply_data["content"]
                    )
                    
                    # Add a random created_at date after the answer date
                    days_after_answer = random.randint(1, 7)
                    reply_created_at = created_at + timedelta(days=days_after_answer)
                    if reply_created_at > datetime.now():
                        reply_created_at = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 3))
                    
                    # Create the reply
                    db_reply = answers_repository.create_reply(db, reply_create, db_answer.id, reply_user.id)
                    
                    # Update the created_at date directly
                    db_reply.created_at = reply_created_at
                    db_reply.updated_at = reply_created_at
                    
                    db.add(db_reply)
                    db.commit()
                    reply_count += 1
                
                # Add helpful votes
                if users:
                    # Randomly select 0-5 users who found the answer helpful
                    num_helpful = random.randint(0, min(5, len(users)))
                    helpful_users = random.sample(users, num_helpful)
                    
                    for helpful_user in helpful_users:
                        answers_repository.toggle_helpful(db, db_answer.id, helpful_user.id)
            
        print(f"Successfully seeded {answer_count} answers and {reply_count} replies")
        
    except Exception as e:
        print(f"Error seeding answers: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_answers()