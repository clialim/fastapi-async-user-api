from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Body
from database.connection import engine, get_session
from database.orm import Base
from request import SignUpRequest


@asynccontextmanager
async def lifespan(_):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/users")
async def signup_handler(
    body: SignUpRequest = Body(...),
    session=Depends(get_session),
):
    return {
        "email": body.email,
    }
