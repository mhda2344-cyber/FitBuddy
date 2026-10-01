from pydantic import BaseModel, Field


class UserInput(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=150
    )

    user_id: str = Field(
        min_length=1,
        max_length=100
    )

    age: int = Field(
        ge=13,
        le=120
    )

    weight: float = Field(
        gt=0,
        le=500
    )

    goal: str = Field(
        min_length=1,
        max_length=100
    )

    intensity: str = Field(
        pattern="^(low|medium|high)$"
    )


class FeedbackRequest(BaseModel):
    user_id: str = Field(
        min_length=1,
        max_length=100
    )

    feedback: str = Field(
        min_length=3,
        max_length=1000
    )