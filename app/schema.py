"""Request and response models for the ticket triage API."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CustomerTier = Literal["free", "standard", "premium"]


class TicketRequest(BaseModel):
    """A support ticket submitted for automatic prioritization."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(
        description="Customer-visible ticket subject and body.",
        examples=["Production is down for every customer after the release."],
        min_length=3,
        max_length=4000,
    )
    customer_tier: CustomerTier = Field(description="Contract tier of the customer.")
    monthly_revenue: float = Field(
        description="Monthly revenue attributable to this customer account.",
        ge=0,
        le=1_000_000_000,
    )


class PredictionResponse(BaseModel):
    """Model output consumed by the routing application."""

    model_config = ConfigDict(extra="forbid")

    priority: Literal["urgent", "high", "normal", "low"]
    confidence: float = Field(ge=0, le=1)
    probabilities: dict[str, float]
    model_version: str
