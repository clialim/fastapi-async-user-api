from openai import AsyncOpenAI
from database.orm import HealthProfile
from pydantic import BaseModel
from config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class RiskPredictionResult(BaseModel):
    diabetes_probability: float
    hypertension_probability: float


MODEL_NAME = "gpt-5-mini"


async def predict_health_risk(profile: HealthProfile) -> RiskPredictionResult:

    prompt = f"""
    You are a health risk prediction model.

    Predict the probability of diabetes and hypertension.

    Rules:
    - value must be between 0 and 1
    - return only JSON
    - fields:
    diabetes_probability
    hypertension_probability

    Health profile:
    age: {profile.age}
    height: {profile.height}
    weight: {profile.weight}
    smoking: {profile.smoking}
    exercise_frequency: {profile.exercise_frequency}
    """

    response = await client.responses.parse(
        model=MODEL_NAME,
        input=prompt,
        text_format=RiskPredictionResult,
    )

    return response.output_parsed
