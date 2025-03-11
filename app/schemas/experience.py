from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class EducationBase(BaseModel):
    institution: str
    degree: str
    year: Optional[int] = None
    honors: Optional[str] = None

class EducationCreate(EducationBase):
    pass

class EducationUpdate(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    year: Optional[int] = None
    honors: Optional[str] = None

class EducationInDB(EducationBase):
    id: UUID
    lawyer_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class WorkExperienceBase(BaseModel):
    role: str
    company: str
    start_date: str  # Format: YYYY-MM
    end_date: Optional[str] = None  # Format: YYYY-MM or "Present"
    description: Optional[str] = None

class WorkExperienceCreate(WorkExperienceBase):
    pass

class WorkExperienceUpdate(BaseModel):
    role: Optional[str] = None
    company: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

class WorkExperienceInDB(WorkExperienceBase):
    id: UUID
    lawyer_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class AchievementBase(BaseModel):
    title: str
    year: Optional[int] = None
    issuer: Optional[str] = None

class AchievementCreate(AchievementBase):
    pass

class AchievementUpdate(BaseModel):
    title: Optional[str] = None
    year: Optional[int] = None
    issuer: Optional[str] = None

class AchievementInDB(AchievementBase):
    id: UUID
    lawyer_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class ExperienceStats(BaseModel):
    cases_won: int
    total_cases: int
    years_experience: int
    specialized_areas: int

class ExperienceResponse(BaseModel):
    education: List[EducationBase]
    work_experience: List[WorkExperienceBase]
    achievements: List[AchievementBase]
    stats: ExperienceStats
