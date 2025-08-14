from pydantic import BaseModel, Field
from typing import List, Optional


class TravelQuery(BaseModel):
    """Request body schema for user travel query."""
    query: str = Field(..., example="Looking for a romantic beach getaway in Europe during July")


class HotelRecommendation(BaseModel):
    name: str
    city: str
    price_per_night: float
    rating: float


class FlightRecommendation(BaseModel):
    airline: str
    from_airport: str
    to_airport: str
    price: float
    duration: str
    date: str


class ExperienceRecommendation(BaseModel):
    name: str
    city: str
    price: float
    duration: str


class TravelAdvice(BaseModel):
    """Structured response returned by the Gen-AI Travel Assistant."""
    destination: str
    reason: str
    budget: str
    tips: List[str]

    # Optional enrichments
    hotel: Optional[HotelRecommendation] = None
    flight: Optional[FlightRecommendation] = None
    experience: Optional[ExperienceRecommendation] = None
