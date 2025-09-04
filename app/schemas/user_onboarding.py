from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from app.core.consts import OnboardingStep


class OnboardingStepOut(BaseModel):
    """Onboarding step output schema"""
    id: UUID
    user_id: UUID
    step_name: str
    completed_at: datetime

    model_config = ConfigDict(
        ser_json_timedelta="iso8601",
        ser_json_bytes="utf8",
        json_encoders={
            datetime: lambda dt: dt.strftime(
                "%Y-%m-%dT%H:%M:%S.{:03d}Z".format(int(dt.microsecond / 1000))
            )
        },
        from_attributes=True,
    )


class OnboardingStepUpdate(BaseModel):
    """Schema for updating onboarding step"""
    step_name: OnboardingStep
    completed_at: Optional[datetime] = None


class OnboardingProgressOut(BaseModel):
    """Complete onboarding progress for user"""
    user_id: UUID
    steps: List[OnboardingStepOut]

    model_config = ConfigDict(from_attributes=True)