from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.customer import Customer, CustomerFamily, CustomerEmployment, CustomerBanking, CustomerExistingProduct
from app.models.product import HDFCProduct
from app.models.recommendation import Recommendation
from app.schemas.recommendation import RecommendationResponse, RecommendationRequest, RecommendationApply
from app.ai.gemini_service import get_gemini_recommendations
from app.ai.recommendation_engine import RuleEngine, EligibilityEngine, ProductRanker
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/api/recommendations", tags=["AI Recommendations"])

rule_engine = RuleEngine()
eligibility_engine = EligibilityEngine()
ranker = ProductRanker()


@router.post("/generate/{customer_id}")
async def generate_recommendations(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    family = db.query(CustomerFamily).filter(CustomerFamily.customer_id == customer.id).first()
    employment = db.query(CustomerEmployment).filter(CustomerEmployment.customer_id == customer.id).first()
    banking = db.query(CustomerBanking).filter(CustomerBanking.customer_id == customer.id).first()
    existing_products = db.query(CustomerExistingProduct).filter(CustomerExistingProduct.customer_id == customer.id).all()
    existing_product_names = [p.product_name for p in existing_products]

    # Build comprehensive customer data
    customer_data = {
        "name": customer.full_name,
        "age": customer.age,
        "gender": customer.gender,
        "occupation": customer.occupation or "",
        "employer": customer.employer or "",
        "annual_income": customer.annual_income or 0,
        "marital_status": customer.marital_status or "",
        "city": customer.city or "",
        "state": customer.state or "",
        "risk_appetite": customer.risk_appetite or "moderate",
        "current_products": existing_product_names,
    }

    if employment:
        customer_data.update({
            "monthly_income": employment.monthly_income or 0,
            "monthly_expenses": employment.monthly_expenses or 0,
            "credit_score": employment.credit_score or 700,
            "employment_type": employment.employment_type or "",
            "years_in_job": employment.years_in_job or 0,
            "company_category": employment.company_category or "",
            "gst_registered": employment.gst_registered or False,
        })

    if banking:
        customer_data.update({
            "current_balance": banking.current_balance or 0,
            "average_balance": banking.average_balance or 0,
            "fd_amount": banking.fd_amount or 0,
            "rd_amount": banking.rd_amount or 0,
            "upi_monthly": banking.upi_monthly or 0,
            "monthly_debit": banking.monthly_debit or 0,
            "monthly_credit": banking.monthly_credit or 0,
            "salary_credit": banking.salary_credit or 0,
            "cash_deposit_monthly": banking.cash_deposit_monthly or 0,
            "has_savings_account": banking.has_savings_account or False,
            "has_current_account": banking.has_current_account or False,
        })

    if family:
        customer_data.update({
            "married": family.spouse_name is not None,
            "spouse_name": family.spouse_name or "",
            "spouse_age": family.spouse_age or 0,
            "spouse_occupation": family.spouse_occupation or "",
            "num_children": family.num_children or 0,
            "child1_age": family.child1_age or 0,
            "child1_education": family.child1_education or "",
            "child2_age": family.child2_age or 0,
            "child2_education": family.child2_education or "",
            "dependent_parents": family.dependent_parents or False,
            "parents_senior_citizen": family.parents_senior_citizen or False,
            "family_income": family.family_income or 0,
            "family_assets": family.family_assets or 0,
            "family_investments": family.family_investments or 0,
            "family_insurance_value": family.family_insurance_value or 0,
            "family_goals": family.family_goals or "",
        })

    # Get AI recommendations
    ai_response = await get_gemini_recommendations(customer_data)
    ai_recommendations = ai_response.get("recommendations", [])

    # Run rule engine
    rules = rule_engine.evaluate(customer, family, employment, banking, existing_product_names)

    # Build product map for eligibility checking
    products = db.query(HDFCProduct).filter(HDFCProduct.is_active == True).all()
    product_map = {p.name: p for p in products}

    # Check eligibility and resolve product_id
    for rec in ai_recommendations:
        product = product_map.get(rec["product"])
        if product:
            elig = eligibility_engine.check(customer, employment, banking, product)
            rec["eligibility_status"] = elig["status"]
            rec["eligibility_reasons"] = elig["reasons"]
            rec["product_id"] = product.id
        else:
            rec["eligibility_status"] = rec.get("eligibility_status", "unknown")
            rec["eligibility_reasons"] = []
            rec["product_id"] = None

    # Rank top 3
    ranked = ranker.rank(customer, employment, banking, ai_recommendations, rules)

    # Save to database
    saved_recs = []
    for i, rec in enumerate(ranked):
        db_rec = Recommendation(
            customer_id=customer.id,
            product_id=rec.get("product_id"),
            product_name=rec["product"],
            product_category=rec.get("category", ""),
            confidence_score=rec.get("confidence", 0),
            acceptance_probability=rec.get("acceptance_probability", 0),
            reason=rec.get("reason", ""),
            ai_analysis={
                "customer_insights": ai_response.get("customer_insights", {}),
                "benefits": rec.get("benefits", []),
                "monthly_cost": rec.get("monthly_cost", ""),
                "expected_roi": rec.get("expected_roi", ""),
            },
            rule_engine_output={"rules": [r["rule"] for r in rules]},
            eligibility_status=rec.get("eligibility_status", "unknown"),
            rank=i + 1,
            rm_id=current_user.id,
        )
        db.add(db_rec)
        saved_recs.append(db_rec)

    db.commit()

    for rec in saved_recs:
        db.refresh(rec)

    return {
        "customer_id": customer_id,
        "customer_name": customer.full_name,
        "recommendations": [
            {
                "id": r.id,
                "product_name": r.product_name,
                "product_category": r.product_category,
                "confidence_score": r.confidence_score,
                "acceptance_probability": r.acceptance_probability,
                "reason": r.reason,
                "eligibility_status": r.eligibility_status,
                "rank": r.rank,
                "status": r.status,
                "ai_analysis": r.ai_analysis,
            }
            for r in saved_recs
        ],
        "rules_applied": [r["rule"] for r in rules],
        "customer_insights": ai_response.get("customer_insights", {}),
    }


@router.get("/customer/{customer_id}", response_model=list[RecommendationResponse])
def get_customer_recommendations(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return (
        db.query(Recommendation)
        .filter(Recommendation.customer_id == customer.id)
        .order_by(Recommendation.rank)
        .all()
    )


@router.put("/{recommendation_id}/apply")
def apply_recommendation(
    recommendation_id: int,
    data: RecommendationApply,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.status = "applied"
    rec.outcome = data.outcome
    if data.outcome == "applied":
        rec.applied_date = datetime.utcnow()
    db.commit()

    return {"message": f"Recommendation marked as {data.outcome}"}
