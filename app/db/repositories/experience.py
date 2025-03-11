from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime
from dateutil.relativedelta import relativedelta

from app.models.experience import Education, WorkExperience, Achievement
from app.models.lawyer import Lawyer
from app.models.area import lawyer_area_association, PracticeArea
from app.schemas.experience import (
    EducationCreate, EducationUpdate,
    WorkExperienceCreate, WorkExperienceUpdate,
    AchievementCreate, AchievementUpdate,
    ExperienceStats
)

# Education repository functions
def get_education_by_id(db: Session, education_id: UUID) -> Optional[Education]:
    """
    Get education entry by ID
    """
    return db.query(Education).filter(Education.id == education_id).first()

def get_education_by_lawyer(db: Session, lawyer_id: UUID) -> List[Education]:
    """
    Get all education entries for a lawyer
    """
    return db.query(Education).filter(Education.lawyer_id == lawyer_id).order_by(Education.year.desc()).all()

def create_education(db: Session, education: EducationCreate, lawyer_id: UUID) -> Education:
    """
    Create a new education entry
    """
    db_education = Education(
        institution=education.institution,
        degree=education.degree,
        year=education.year,
        honors=education.honors,
        lawyer_id=lawyer_id
    )
    db.add(db_education)
    db.commit()
    db.refresh(db_education)
    return db_education

def update_education(db: Session, education: Education, education_data: EducationUpdate) -> Education:
    """
    Update an education entry
    """
    update_data = education_data.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(education, key, value)
        
    db.add(education)
    db.commit()
    db.refresh(education)
    return education

def delete_education(db: Session, education_id: UUID) -> None:
    """
    Delete an education entry
    """
    education = db.query(Education).filter(Education.id == education_id).first()
    if education:
        db.delete(education)
        db.commit()
    return None

# Work Experience repository functions
def get_work_experience_by_id(db: Session, experience_id: UUID) -> Optional[WorkExperience]:
    """
    Get work experience entry by ID
    """
    return db.query(WorkExperience).filter(WorkExperience.id == experience_id).first()

def get_work_experience_by_lawyer(db: Session, lawyer_id: UUID) -> List[WorkExperience]:
    """
    Get all work experience entries for a lawyer
    """
    return db.query(WorkExperience).filter(WorkExperience.lawyer_id == lawyer_id).all()

def create_work_experience(db: Session, experience: WorkExperienceCreate, lawyer_id: UUID) -> WorkExperience:
    """
    Create a new work experience entry
    """
    db_experience = WorkExperience(
        role=experience.role,
        company=experience.company,
        start_date=experience.start_date,
        end_date=experience.end_date,
        description=experience.description,
        lawyer_id=lawyer_id
    )
    db.add(db_experience)
    db.commit()
    db.refresh(db_experience)
    return db_experience

def update_work_experience(db: Session, experience: WorkExperience, experience_data: WorkExperienceUpdate) -> WorkExperience:
    """
    Update a work experience entry
    """
    update_data = experience_data.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(experience, key, value)
        
    db.add(experience)
    db.commit()
    db.refresh(experience)
    return experience

def delete_work_experience(db: Session, experience_id: UUID) -> None:
    """
    Delete a work experience entry
    """
    experience = db.query(WorkExperience).filter(WorkExperience.id == experience_id).first()
    if experience:
        db.delete(experience)
        db.commit()
    return None

# Achievement repository functions
def get_achievement_by_id(db: Session, achievement_id: UUID) -> Optional[Achievement]:
    """
    Get achievement entry by ID
    """
    return db.query(Achievement).filter(Achievement.id == achievement_id).first()

def get_achievements_by_lawyer(db: Session, lawyer_id: UUID) -> List[Achievement]:
    """
    Get all achievement entries for a lawyer
    """
    return db.query(Achievement).filter(Achievement.lawyer_id == lawyer_id).order_by(Achievement.year.desc()).all()

def create_achievement(db: Session, achievement: AchievementCreate, lawyer_id: UUID) -> Achievement:
    """
    Create a new achievement entry
    """
    db_achievement = Achievement(
        title=achievement.title,
        year=achievement.year,
        issuer=achievement.issuer,
        lawyer_id=lawyer_id
    )
    db.add(db_achievement)
    db.commit()
    db.refresh(db_achievement)
    return db_achievement

def update_achievement(db: Session, achievement: Achievement, achievement_data: AchievementUpdate) -> Achievement:
    """
    Update an achievement entry
    """
    update_data = achievement_data.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(achievement, key, value)
        
    db.add(achievement)
    db.commit()
    db.refresh(achievement)
    return achievement

def delete_achievement(db: Session, achievement_id: UUID) -> None:
    """
    Delete an achievement entry
    """
    achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if achievement:
        db.delete(achievement)
        db.commit()
    return None

# Experience stats functions
def get_experience_stats(db: Session, lawyer_id: UUID) -> ExperienceStats:
    """
    Get experience statistics for a lawyer
    """
    lawyer = db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()
    
    if not lawyer:
        return ExperienceStats(
            cases_won=0,
            total_cases=0,
            years_experience=0,
            specialized_areas=0
        )
    
    # Calculate specialized areas
    specialized_areas = db.query(lawyer_area_association).filter(
        lawyer_area_association.c.lawyer_id == lawyer_id
    ).count()
    
    # Calculate years of experience
    years_experience = 0
    if lawyer.professional_start_date:
        today = datetime.now()
        delta = relativedelta(today, lawyer.professional_start_date)
        years_experience = delta.years
    
    # For now, use placeholder values for cases
    # In a real implementation, you would have a cases table to query
    cases_won = 45
    total_cases = 52
    
    return ExperienceStats(
        cases_won=cases_won,
        total_cases=total_cases,
        years_experience=years_experience,
        specialized_areas=specialized_areas
    )
