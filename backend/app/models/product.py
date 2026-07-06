from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import Base


class HDFCProduct(Base):
    __tablename__ = "hdfc_products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)  # accounts, credit_cards, loans, investments, insurance, digital
    subcategory = Column(String(100))
    description = Column(Text)
    features = Column(JSON)
    eligibility_criteria = Column(JSON)
    min_income = Column(Float)
    min_age = Column(Integer)
    max_age = Column(Integer)
    min_credit_score = Column(Integer)
    risk_profile = Column(String(20))  # conservative, moderate, aggressive
    occupation_types = Column(JSON)  # list of allowed occupation types
    family_requirements = Column(JSON)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    annual_fee = Column(Float, default=0)
    interest_rate = Column(Float)
    processing_fee = Column(Float, default=0)
    benefits = Column(JSON)
    tags = Column(JSON)  # search tags
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
