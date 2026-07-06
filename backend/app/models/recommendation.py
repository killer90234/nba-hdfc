from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("hdfc_products.id"), nullable=True)
    product_name = Column(String(200), nullable=False)
    product_category = Column(String(50))

    confidence_score = Column(Float, nullable=False)
    acceptance_probability = Column(Float)
    reason = Column(Text)
    ai_analysis = Column(JSON)
    rule_engine_output = Column(JSON)
    eligibility_status = Column(String(20))  # eligible, conditionally_eligible, not_eligible
    rank = Column(Integer)

    status = Column(String(20), default="pending")  # pending, explained, applied, accepted, rejected
    applied_date = Column(DateTime)
    outcome = Column(String(30))  # accepted, rejected, pending

    rm_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("Customer", back_populates="recommendations")
