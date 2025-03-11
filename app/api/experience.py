from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.db.repositories import experience as experience_repository
from app.db.repositories import lawyers as lawyers_repository
from app.schemas.experience import AchievementCreate, AchievementInDB, AchievementUpdate, EducationCreate, EducationInDB, EducationUpdate, ExperienceResponse, WorkExperienceCreate, WorkExperienceInDB, WorkExperienceUpdate

router = APIRouter()


@router.get("/{lawyer_id}/experience", response_model=ExperienceResponse)
async def get_lawyer_experience(lawyer_id: UUID, db: Session = Depends(get_db)):
    """
    Get detailed experience information for a lawyer
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")

    # Get education, work experience, and achievements
    education = experience_repository.get_education_by_lawyer(db, lawyer_id)
    work_experience = experience_repository.get_work_experience_by_lawyer(db, lawyer_id)
    achievements = experience_repository.get_achievements_by_lawyer(db, lawyer_id)

    # Get stats
    stats = experience_repository.get_experience_stats(db, lawyer_id)

    # Format response
    return ExperienceResponse(
        education=[e.__dict__ for e in education],
        work_experience=[e.__dict__ for e in work_experience],
        achievements=[e.__dict__ for e in achievements],
        stats=stats,
    )


# Add to app/api/experience.py after the existing GET endpoint

# Education endpoints
@router.post("/{lawyer_id}/education", response_model=EducationInDB, status_code=status.HTTP_201_CREATED)
async def create_lawyer_education(
    lawyer_id: UUID,
    education: EducationCreate,
    db: Session = Depends(get_db)
):
    """
    Add an education entry for a lawyer
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Create education entry
    db_education = experience_repository.create_education(db, education, lawyer_id)
    return db_education

@router.patch("/{lawyer_id}/education/{education_id}", response_model=EducationInDB)
async def update_lawyer_education(
    lawyer_id: UUID,
    education_id: UUID,
    education: EducationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an education entry
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Verify education exists and belongs to the lawyer
    db_education = experience_repository.get_education_by_id(db, education_id)
    if not db_education:
        raise HTTPException(status_code=404, detail="Education entry not found")
    
    if db_education.lawyer_id != lawyer_id:
        raise HTTPException(status_code=400, detail="Education entry does not belong to this lawyer")
    
    # Update education
    updated_education = experience_repository.update_education(db, db_education, education)
    return updated_education

@router.delete("/{lawyer_id}/education/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lawyer_education(
    lawyer_id: UUID,
    education_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete an education entry
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Verify education exists and belongs to the lawyer
    db_education = experience_repository.get_education_by_id(db, education_id)
    if not db_education:
        raise HTTPException(status_code=404, detail="Education entry not found")
    
    if db_education.lawyer_id != lawyer_id:
        raise HTTPException(status_code=400, detail="Education entry does not belong to this lawyer")
    
    # Delete education
    experience_repository.delete_education(db, education_id)
    return None

# Work Experience endpoints
@router.post("/{lawyer_id}/work-experience", response_model=WorkExperienceInDB, status_code=status.HTTP_201_CREATED)
async def create_lawyer_work_experience(
    lawyer_id: UUID,
    experience: WorkExperienceCreate,
    db: Session = Depends(get_db)
):
    """
    Add a work experience entry for a lawyer
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Create work experience entry
    db_experience = experience_repository.create_work_experience(db, experience, lawyer_id)
    return db_experience

@router.patch("/{lawyer_id}/work-experience/{experience_id}", response_model=WorkExperienceInDB)
async def update_lawyer_work_experience(
    lawyer_id: UUID,
    experience_id: UUID,
    experience: WorkExperienceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a work experience entry
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Verify work experience exists and belongs to the lawyer
    db_experience = experience_repository.get_work_experience_by_id(db, experience_id)
    if not db_experience:
        raise HTTPException(status_code=404, detail="Work experience entry not found")
    
    if db_experience.lawyer_id != lawyer_id:
        raise HTTPException(status_code=400, detail="Work experience entry does not belong to this lawyer")
    
    # Update work experience
    updated_experience = experience_repository.update_work_experience(db, db_experience, experience)
    return updated_experience

@router.delete("/{lawyer_id}/work-experience/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lawyer_work_experience(
    lawyer_id: UUID,
    experience_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a work experience entry
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Verify work experience exists and belongs to the lawyer
    db_experience = experience_repository.get_work_experience_by_id(db, experience_id)
    if not db_experience:
        raise HTTPException(status_code=404, detail="Work experience entry not found")
    
    if db_experience.lawyer_id != lawyer_id:
        raise HTTPException(status_code=400, detail="Work experience entry does not belong to this lawyer")
    
    # Delete work experience
    experience_repository.delete_work_experience(db, experience_id)
    return None

# Achievement endpoints
@router.post("/{lawyer_id}/achievements", response_model=AchievementInDB, status_code=status.HTTP_201_CREATED)
async def create_lawyer_achievement(
    lawyer_id: UUID,
    achievement: AchievementCreate,
    db: Session = Depends(get_db)
):
    """
    Add an achievement entry for a lawyer
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Create achievement entry
    db_achievement = experience_repository.create_achievement(db, achievement, lawyer_id)
    return db_achievement

@router.patch("/{lawyer_id}/achievements/{achievement_id}", response_model=AchievementInDB)
async def update_lawyer_achievement(
    lawyer_id: UUID,
    achievement_id: UUID,
    achievement: AchievementUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an achievement entry
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Verify achievement exists and belongs to the lawyer
    db_achievement = experience_repository.get_achievement_by_id(db, achievement_id)
    if not db_achievement:
        raise HTTPException(status_code=404, detail="Achievement entry not found")
    
    if db_achievement.lawyer_id != lawyer_id:
        raise HTTPException(status_code=400, detail="Achievement entry does not belong to this lawyer")
    
    # Update achievement
    updated_achievement = experience_repository.update_achievement(db, db_achievement, achievement)
    return updated_achievement

@router.delete("/{lawyer_id}/achievements/{achievement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lawyer_achievement(
    lawyer_id: UUID,
    achievement_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete an achievement entry
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Verify achievement exists and belongs to the lawyer
    db_achievement = experience_repository.get_achievement_by_id(db, achievement_id)
    if not db_achievement:
        raise HTTPException(status_code=404, detail="Achievement entry not found")
    
    if db_achievement.lawyer_id != lawyer_id:
        raise HTTPException(status_code=400, detail="Achievement entry does not belong to this lawyer")
    
    # Delete achievement
    experience_repository.delete_achievement(db, achievement_id)
    return None