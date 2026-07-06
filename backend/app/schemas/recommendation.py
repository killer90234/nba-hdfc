from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class RecommendationResponse(BaseModel):
    id: int
    customer_id: int
    product_name: str
    product_category: Optional[str]
    confidence_score: float
    acceptance_probability: Optional[float]
    reason: Optional[str]
    ai_analysis: Optional[Any]
    eligibility_status: Optional[str]
    rank: Optional[int]
    status: str
    outcome: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class RecommendationRequest(BaseModel):
    customer_id: int


class RecommendationApply(BaseModel):
    recommendation_id: int
    outcome: str  # applied, accepted, rejected


class AIAnalysisRequest(BaseModel):
    customer_id: int


class AIAnalysisResponse(BaseModel):
    customer_name: str
    age: Optional[int]
    income: Optional[float]
    credit_score: Optional[int]
    current_products: List[str]
    monthly_spending: dict
    family_summary: str
    recommendations: List[dict]
    gemini_raw_response: Optional[str]
    rule_engine_output: List[dict]
    eligibility_results: List[dict]


class DashboardStats(BaseModel):
    total_customers: int
    today_recommendations: int
    total_recommendations: int
    acceptance_rate: float
    total_revenue_impact: float
    top_products: List[dict]
    recent_activities: List[dict]
    rm_performance: List[dict]


class ProductConversionStats(BaseModel):
    product_name: str
    total_recommended: int
    applied: int
    accepted: int
    conversion_rate: float
