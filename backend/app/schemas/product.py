from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    subcategory: Optional[str]
    description: Optional[str]
    features: Optional[Any]
    eligibility_criteria: Optional[Any]
    min_income: Optional[float]
    min_age: Optional[int]
    max_age: Optional[int]
    min_credit_score: Optional[int]
    risk_profile: Optional[str]
    is_active: bool
    is_premium: bool
    annual_fee: float
    interest_rate: Optional[float]
    benefits: Optional[Any]
    tags: Optional[Any]

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    category: str
    subcategory: Optional[str] = None
    description: Optional[str] = None
    features: Optional[Any] = None
    eligibility_criteria: Optional[Any] = None
    min_income: Optional[float] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    min_credit_score: Optional[int] = None
    risk_profile: Optional[str] = None
    occupation_types: Optional[Any] = None
    family_requirements: Optional[Any] = None
    is_active: bool = True
    is_premium: bool = False
    annual_fee: float = 0
    interest_rate: Optional[float] = None
    processing_fee: float = 0
    benefits: Optional[Any] = None
    tags: Optional[Any] = None
