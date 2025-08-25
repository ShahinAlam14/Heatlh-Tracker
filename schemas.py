from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

# Health Data schemas
class HealthDataBase(BaseModel):
    date: Optional[datetime.date] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    steps: Optional[int] = None
    sleep_hours: Optional[float] = None
    water_intake: Optional[float] = None
    calories_consumed: Optional[int] = None
    calories_burned: Optional[int] = None
    heart_rate: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    notes: Optional[str] = None

class HealthDataCreate(HealthDataBase):
    pass

class HealthDataUpdate(HealthDataBase):
    pass

class HealthDataResponse(HealthDataBase):
    id: int
    user_id: int
    
    class Config:
        orm_mode = True

# Nutrition Entry schemas
class NutritionEntryBase(BaseModel):
    meal_type: str
    food_name: str
    calories: int
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    time: Optional[datetime] = None

class NutritionEntryCreate(NutritionEntryBase):
    health_data_id: int

class NutritionEntryResponse(NutritionEntryBase):
    id: int
    health_data_id: int
    
    class Config:
        orm_mode = True

# Activity Entry schemas
class ActivityEntryBase(BaseModel):
    activity_type: str
    duration: int
    calories_burned: Optional[int] = None
    time: Optional[datetime] = None

class ActivityEntryCreate(ActivityEntryBase):
    health_data_id: int

class ActivityEntryResponse(ActivityEntryBase):
    id: int
    health_data_id: int
    
    class Config:
        orm_mode = True

# Goal schemas
class GoalBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_value: float
    goal_type: str
    target_date: Optional[date] = None

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    goal_type: Optional[str] = None
    target_date: Optional[date] = None
    is_achieved: Optional[bool] = None

class GoalResponse(GoalBase):
    id: int
    user_id: int
    current_value: Optional[float] = None
    start_date: date
    is_achieved: bool
    
    class Config:
        orm_mode = True

# Health Insights schemas
class HealthInsightRequest(BaseModel):
    weight: Optional[float] = None
    height: Optional[float] = None
    steps: Optional[int] = None
    sleep_hours: Optional[float] = None
    water_intake: Optional[float] = None
    calories_consumed: Optional[int] = None
    calories_burned: Optional[int] = None
    heart_rate: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None

class HealthInsightResponse(BaseModel):
    summary: str
    insights: List[Dict[str, str]]
    health_score: int
    priority_focus_areas: List[str]

# Nutrition recommendation schemas
class NutritionRecommendationRequest(BaseModel):
    meals: List[Dict[str, Any]]
    total_calories: Optional[int] = None
    total_protein: Optional[float] = None
    total_carbs: Optional[float] = None
    total_fat: Optional[float] = None
    weight_goal: Optional[str] = None

class NutritionRecommendationResponse(BaseModel):
    assessment: str
    recommendations: List[Dict[str, str]]
    meal_ideas: List[Dict[str, str]]

# Activity recommendation schemas
class ActivityRecommendationRequest(BaseModel):
    activities: List[Dict[str, Any]]
    total_duration: Optional[int] = None
    total_calories_burned: Optional[int] = None
    steps: Optional[int] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    fitness_level: Optional[str] = None
    goals: Optional[str] = None

class ActivityRecommendationResponse(BaseModel):
    assessment: str
    recommended_activities: List[Dict[str, str]]
    weekly_plan: List[Dict[str, Any]]
