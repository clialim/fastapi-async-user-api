from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, computed_field
from pydantic import computed_field


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


class HealthRiskPredictionResponse(BaseModel):
    id: int
    user_id: int
    diabetes_probability: float
    hypertension_probability: float
    created_at: datetime

    @computed_field
    @property
    def created_at_kst(self) -> datetime:
        KST = timezone(timedelta(hours=9))
        return self.created_at.astimezone(KST)
