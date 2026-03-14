from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.jwt import verify_user
from database.connection import get_session
from database.orm import HealthProfile, HealthRiskPrediction
from llm import predict_health_risk
from response import HealthRiskPredictionResponse
from enum import StrEnum

router = APIRouter(tags=["Prediction"])


@router.post(
    "/predictions",
    summary="당뇨병/고혈압 위험도 예측 API",
    status_code=status.HTTP_201_CREATED,
    response_model=HealthRiskPredictionResponse,
)
async def risk_predict_handler(
    user_id: int = Depends(verify_user),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(HealthProfile).where(HealthProfile.user_id == user_id)
    profile = await session.scalar(stmt)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="health profile not found",
        )

    risk_prediction = await predict_health_risk(profile=profile)

    new_prediction = HealthRiskPrediction(
        user_id=user_id,
        diabetes_probability=risk_prediction.diabetes_probability,
        hypertension_probability=risk_prediction.hypertension_probability,
        model_version="gpt-5-mini",
    )

    session.add(new_prediction)
    await session.commit()
    await session.refresh(new_prediction)

    return new_prediction
