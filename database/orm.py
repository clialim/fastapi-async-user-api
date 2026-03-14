from sqlalchemy import (
    String,
    DateTime,
    func,
    ForeignKey,
    Float,
    Boolean,
    Integer,
    event,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    with_loader_criteria,
    Session,
)

from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    def soft_delete(self):
        self.email = f"deleted_{self.id}_{self.email}"
        self.deleted_at = datetime.now(tz=timezone.utc)


@event.listens_for(Session, "do_orm_execute")
def _add_filtering_criteria(execute_state):

    if execute_state.is_select:

        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                User,
                lambda cls: cls.deleted_at.is_(None),
                include_aliases=True,
            )
        )


class HealthProfile(Base):
    __tablename__ = "health_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    height: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    smoking: Mapped[bool] = mapped_column(Boolean, nullable=False)
    exercise_frequency: Mapped[int] = mapped_column(Integer, nullable=False)


class HealthRiskPrediction(Base):
    __tablename__ = "health_risk_predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    diabetes_probability: Mapped[float] = mapped_column(Float, nullable=False)
    hypertension_probability: Mapped[float] = mapped_column(Float, nullable=False)
    model_version: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
