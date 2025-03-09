# scripts/seed_practice_areas.py
import sys
import os
import json
from pathlib import Path
from uuid import UUID

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set the DATABASE_URL environment variable for local development if not already set
if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/lexic_db"

from app.db.database import SessionLocal
from app.models import PracticeArea, PracticeAreaCategory
from app.db.repositories import areas as areas_repository
from app.db.repositories import categories as categories_repository
from app.schemas.area import PracticeAreaCreate
from app.schemas.category import PracticeAreaCategoryCreate

# Practice area categories
CATEGORIES = [
    {"name": "Civil", "slug": "civil"},
    {"name": "Familia", "slug": "family"},
    {"name": "Laboral", "slug": "labor"},
    {"name": "Penal", "slug": "criminal"},
    {"name": "Comercial", "slug": "commercial"},
    {"name": "Consumidor", "slug": "consumer"},
    {"name": "Tributario", "slug": "tax"},
    {"name": "Administrativo", "slug": "administrative"},
    {"name": "Internacional", "slug": "international"},
    {"name": "Ambiental", "slug": "environmental"},
    {"name": "Derechos Humanos", "slug": "human-rights"},
    {"name": "Otros", "slug": "other"}
]

# Practice areas data with category_slug instead of category
PRACTICE_AREAS = [
    # Civil Law
    {"name": "Contratos", "slug": "contratos", "category_slug": "civil", "description": "Asesoría y litigios en materia de contratos civiles"},
    {"name": "Sucesiones", "slug": "sucesiones", "category_slug": "civil", "description": "Herencias y derecho sucesorio"},
    {"name": "Testamentos", "slug": "testamentos", "category_slug": "civil", "description": "Preparación y disputas de testamentos"},
    {"name": "Propiedad", "slug": "propiedad", "category_slug": "civil", "description": "Derechos de propiedad y bienes raíces"},
    {"name": "Compra y Arriendo de Propiedades", "slug": "compra-arriendo-propiedades", "category_slug": "civil"},
    {"name": "Estudios de Títulos", "slug": "estudios-titulos", "category_slug": "civil"},
    {"name": "Pago de Honorarios", "slug": "pago-honorarios", "category_slug": "civil"},
    {"name": "Inmigración", "slug": "inmigracion-civil", "category_slug": "civil"},
    {"name": "Deudas y Embargos", "slug": "deudas-embargos", "category_slug": "civil"},
    {"name": "Recurso de protección contra alza en Isapres", "slug": "recurso-isapres", "category_slug": "civil"},
    {"name": "Mascotas", "slug": "mascotas", "category_slug": "civil"},
    {"name": "Problemas entre vecinos", "slug": "problemas-vecinos", "category_slug": "civil"},
    {"name": "Negligencia médica", "slug": "negligencia-medica", "category_slug": "civil"},

    # Family Law
    {"name": "Violencia Intrafamiliar", "slug": "violencia-intrafamiliar", "category_slug": "family"},
    {"name": "Adopciones", "slug": "adopciones", "category_slug": "family"},
    {"name": "Juicio o reconocimiento de Paternidad", "slug": "juicio-paternidad", "category_slug": "family"},
    {"name": "Tuición", "slug": "tuicion", "category_slug": "family"},
    {"name": "Régimen de Visitas", "slug": "regimen-visitas", "category_slug": "family"},
    {"name": "Pensión Alimenticia", "slug": "pension-alimenticia", "category_slug": "family"},
    {"name": "Divorcio", "slug": "divorcio", "category_slug": "family"},
    {"name": "Cambio de Nombre", "slug": "cambio-nombre", "category_slug": "family"},
    {"name": "Declaración de Interdicción", "slug": "declaracion-interdiccion", "category_slug": "family"},

    # Labor Law
    {"name": "Accidentes Laborales", "slug": "accidentes-laborales", "category_slug": "labor"},
    {"name": "Negociación Colectiva", "slug": "negociacion-colectiva", "category_slug": "labor"},
    {"name": "Constitución y Asesoría de Sindicatos", "slug": "asesoria-sindicatos", "category_slug": "labor"},
    {"name": "Despido Injustificado", "slug": "despido-injustificado", "category_slug": "labor"},
    {"name": "Acoso Sexual", "slug": "acoso-sexual", "category_slug": "labor"},
    {"name": "Defensa de Derechos Laborales", "slug": "derechos-laborales", "category_slug": "labor"},
    {"name": "Autodespido", "slug": "autodespido", "category_slug": "labor"},
    {"name": "Licencia médica", "slug": "licencia-medica", "category_slug": "labor"},

    # Criminal Law
    {"name": "Delitos Informáticos", "slug": "delitos-informaticos", "category_slug": "criminal"},
    {"name": "Robos y Hurtos", "slug": "robos-hurtos", "category_slug": "criminal"},
    {"name": "Abuso Sexual y Violación", "slug": "abuso-sexual", "category_slug": "criminal"},
    {"name": "Homicidios", "slug": "homicidios", "category_slug": "criminal"},
    {"name": "Estafas y Delitos económicos", "slug": "estafas", "category_slug": "criminal"},
    {"name": "Tráfico de Drogas", "slug": "trafico-drogas", "category_slug": "criminal"},
    {"name": "Discriminación y Delitos de odio", "slug": "discriminacion-delitos", "category_slug": "criminal"},
    {"name": "Accidentes de Tránsito", "slug": "accidentes-transito", "category_slug": "criminal"},
    {"name": "Agresiones y Riñas", "slug": "agresiones", "category_slug": "criminal"},
    {"name": "Manejo en estado de ebriedad", "slug": "manejo-ebriedad", "category_slug": "criminal"},
    {"name": "Amenazas y extorsiones", "slug": "amenazas", "category_slug": "criminal"},
    {"name": "Injurias y Calumnias", "slug": "injurias-calumnias", "category_slug": "criminal"},

    # Tax Law
    {"name": "Asesoría tributaria", "slug": "asesoria-tributaria", "category_slug": "tax"},
    {"name": "Defensa tributaria", "slug": "defensa-tributaria", "category_slug": "tax"},
    {"name": "Reorganización empresarial", "slug": "reorganizacion-empresarial", "category_slug": "tax"},
    {"name": "Planificación Tributaria", "slug": "planificacion-tributaria", "category_slug": "tax"},
    {"name": "Litigios Tributarios", "slug": "litigios-tributarios", "category_slug": "tax"},

    # Commercial Law
    {"name": "Constitución de empresas", "slug": "constitucion-empresas", "category_slug": "commercial"},
    {"name": "Contratos comerciales", "slug": "contratos-comerciales", "category_slug": "commercial"},
    {"name": "Propiedad intelectual e industrial", "slug": "propiedad-intelectual", "category_slug": "commercial"},
    {"name": "Litigios comerciales", "slug": "litigios-comerciales", "category_slug": "commercial"},
    {"name": "Mercado de Capitales", "slug": "mercado-capitales", "category_slug": "commercial"},
    {"name": "Insolvencia y Quiebras", "slug": "insolvencia-quiebras", "category_slug": "commercial"},
    {"name": "Litigio y Arbitrajes", "slug": "litigio-arbitrajes", "category_slug": "commercial"},
    {"name": "Inversión Extranjera", "slug": "inversion-extranjera", "category_slug": "commercial"},
    {"name": "Recursos Naturales y Medioambientales", "slug": "recursos-naturales", "category_slug": "commercial"},
    {"name": "Importaciones, exportaciones y derecho aduanero", "slug": "derecho-aduanero-commercial", "category_slug": "commercial"},

    # Consumer Protection
    {"name": "Telecomunicaciones", "slug": "telecomunicaciones", "category_slug": "consumer"},
    {"name": "Tiendas comerciales y retail", "slug": "retail", "category_slug": "consumer"},
    {"name": "Bancos, AFPs y empresa financieras", "slug": "servicios-financieros", "category_slug": "consumer"},
    {"name": "Transporte", "slug": "transporte", "category_slug": "consumer"},
    {"name": "Servicios básicos", "slug": "servicios-basicos", "category_slug": "consumer", "description": "Agua, luz, electricidad, etc."},
    {"name": "Aseguradoras", "slug": "aseguradoras", "category_slug": "consumer"},
    {"name": "Comercio electrónico", "slug": "comercio-electronico", "category_slug": "consumer"},
    {"name": "Educación", "slug": "educacion", "category_slug": "consumer"},
    {"name": "Automóviles e Indumotoras", "slug": "automoviles", "category_slug": "consumer"},
    {"name": "Inmobiliarias y constructoras", "slug": "inmobiliarias", "category_slug": "consumer"},
    {"name": "Salud", "slug": "salud", "category_slug": "consumer", "description": "Hospitales, clínicas, etc."},
    {"name": "Entretención y turismo", "slug": "entretencion", "category_slug": "consumer"},

    # Human Rights
    {"name": "Violación a los Derechos humanos por parte del Estado", "slug": "violacion-ddhh-estado", "category_slug": "human-rights"},
    {"name": "Otros casos de violación a los Derechos humanos", "slug": "otros-ddhh", "category_slug": "human-rights"},

    # Administrative Law
    {"name": "Procedimientos administrativos", "slug": "procedimientos-administrativos", "category_slug": "administrative"},
    {"name": "Contratos con el Estado", "slug": "contratos-estado", "category_slug": "administrative"},
    {"name": "Permisos y licencias", "slug": "permisos-licencias", "category_slug": "administrative"},
    {"name": "Responsabilidad del Estado", "slug": "responsabilidad-estado", "category_slug": "administrative"},

    # International Law
    {"name": "Comercio internacional", "slug": "comercio-internacional", "category_slug": "international"},
    {"name": "Derechos humanos", "slug": "derechos-humanos-internacional", "category_slug": "international"},
    {"name": "Arbitraje internacional", "slug": "arbitraje-internacional", "category_slug": "international"},

    # Environmental Law
    {"name": "Evaluación de impacto ambiental", "slug": "evaluacion-impacto-ambiental", "category_slug": "environmental"},
    {"name": "Litigios ambientales", "slug": "litigios-ambientales", "category_slug": "environmental"},
    {"name": "Regulación ambiental", "slug": "regulacion-ambiental", "category_slug": "environmental"},

    # Other Areas
    {"name": "Abogados franquicias", "slug": "franquicias", "category_slug": "other"},
    {"name": "Abogados inmigración", "slug": "inmigracion", "category_slug": "other"},
    {"name": "Abogados quiebras", "slug": "quiebras", "category_slug": "other"},
    {"name": "Abogados telecomunicaciones", "slug": "telecomunicaciones-otros", "category_slug": "other"},
    {"name": "Auditoría", "slug": "auditoria", "category_slug": "other"},
    {"name": "Derecho informático", "slug": "derecho-informatico", "category_slug": "other"},
    {"name": "Derecho publicidad", "slug": "derecho-publicidad", "category_slug": "other"},
    {"name": "Derechos de agua", "slug": "derechos-agua", "category_slug": "other"},
    {"name": "Derechos de la mujer", "slug": "derechos-mujer", "category_slug": "other"},
    {"name": "Derechos de los niños", "slug": "derechos-ninos", "category_slug": "other"},
    {"name": "Discriminación", "slug": "discriminacion", "category_slug": "other"},
    {"name": "Fuero maternal", "slug": "fuero-maternal", "category_slug": "other"},
    {"name": "Ley de transparencia", "slug": "ley-transparencia", "category_slug": "other"},
    {"name": "Multas", "slug": "multas", "category_slug": "other"},
    {"name": "Nacionalidad", "slug": "nacionalidad", "category_slug": "other"},
    {"name": "Participación ciudadana", "slug": "participacion-ciudadana", "category_slug": "other"},
    {"name": "Prevaricación", "slug": "prevaricacion", "category_slug": "other"},
    {"name": "Protección de datos", "slug": "proteccion-datos", "category_slug": "other"},
    {"name": "Pueblos indígenas", "slug": "pueblos-indigenas", "category_slug": "other"},
    {"name": "Remates", "slug": "remates", "category_slug": "other"},
    {"name": "Seguro de cesantía", "slug": "seguro-cesantia", "category_slug": "other"},
    {"name": "Seguros", "slug": "seguros", "category_slug": "other"},
    {"name": "Visas", "slug": "visas", "category_slug": "other"}
]

def seed_practice_areas():
    """Seed practice areas into database"""
    db = SessionLocal()
    
    try:
        # Check if categories already exist
        existing_categories = db.query(PracticeAreaCategory).count()
        if existing_categories > 0:
            print(f"Database already has {existing_categories} practice area categories. Skipping category seeding.")
        else:
            # Seed categories first
            print("Seeding practice area categories...")
            category_count = 0
            
            for category_data in CATEGORIES:
                category_in = PracticeAreaCategoryCreate(**category_data)
                categories_repository.create_category(db, category_in)
                category_count += 1
                
            print(f"Successfully seeded {category_count} practice area categories")
        
        # Check if areas already exist
        existing_areas = db.query(PracticeArea).count()
        if existing_areas > 0:
            print(f"Database already has {existing_areas} practice areas. Skipping area seeding.")
            return
        
        # Create a mapping of category slugs to category IDs
        category_map = {}
        categories = db.query(PracticeAreaCategory).all()
        for category in categories:
            category_map[category.slug] = category.id
        
        print("Seeding practice areas...")
        area_count = 0
        
        for area_data in PRACTICE_AREAS:
            # Convert category_slug to category_id
            category_slug = area_data.pop("category_slug")
            if category_slug not in category_map:
                print(f"Warning: Category '{category_slug}' not found, skipping area '{area_data['name']}'")
                continue
                
            area_data["category_id"] = category_map[category_slug]
            
            # Create area
            area_in = PracticeAreaCreate(**area_data)
            areas_repository.create_area(db, area_in)
            area_count += 1
            
        print(f"Successfully seeded {area_count} practice areas")
        
    except Exception as e:
        print(f"Error seeding practice areas: {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_practice_areas()