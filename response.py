from pydantic import BaseModel
from datetime import datetime


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime


class LoginResponse(BaseModel):
    access_token: str


class HealthProfileResponse(BaseModel):
    id: int
    user_id: int
    age: int
    height_cm: float
    weight_kg: float
    smoking: bool
    exercise_per_week: int
