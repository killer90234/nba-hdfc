from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.customer import Customer
from app.models.recommendation import Recommendation
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_customers = db.query(sqlfunc.count(Customer.id)).scalar() or 0

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_recs = db.query(sqlfunc.count(Recommendation.id)).filter(
        Recommendation.created_at >= today
    ).scalar() or 0

    total_recs = db.query(sqlfunc.count(Recommendation.id)).scalar() or 0
    applied = db.query(sqlfunc.count(Recommendation.id)).filter(
        Recommendation.status.in_(["applied", "accepted"])
    ).scalar() or 0
    accepted = db.query(sqlfunc.count(Recommendation.id)).filter(
        Recommendation.status == "accepted"
    ).scalar() or 0

    acceptance_rate = (accepted / total_recs * 100) if total_recs > 0 else 0

    # Top products
    top_products = (
        db.query(
            Recommendation.product_name,
            sqlfunc.count(Recommendation.id).label("count"),
            sqlfunc.avg(Recommendation.confidence_score).label("avg_confidence"),
        )
        .group_by(Recommendation.product_name)
        .order_by(sqlfunc.count(Recommendation.id).desc())
        .limit(5)
        .all()
    )

    # Recent activity
    recent = (
        db.query(Recommendation)
        .order_by(Recommendation.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "total_customers": total_customers,
        "today_recommendations": today_recs,
        "total_recommendations": total_recs,
        "acceptance_rate": round(acceptance_rate, 1),
        "applied_count": applied,
        "accepted_count": accepted,
        "top_products": [
            {
                "name": p.product_name,
                "count": p.count,
                "avg_confidence": round(float(p.avg_confidence or 0), 1),
            }
            for p in top_products
        ],
        "recent_activities": [
            {
                "id": r.id,
                "product": r.product_name,
                "confidence": r.confidence_score,
                "status": r.status,
                "date": r.created_at.isoformat() if r.created_at else None,
            }
            for r in recent
        ],
    }


@router.get("/analytics/conversion")
def get_conversion_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    products = (
        db.query(
            Recommendation.product_name,
            sqlfunc.count(Recommendation.id).label("total"),
            sqlfunc.count(Recommendation.id).filter(Recommendation.status == "applied").label("applied"),
            sqlfunc.count(Recommendation.id).filter(Recommendation.status == "accepted").label("accepted"),
        )
        .group_by(Recommendation.product_name)
        .all()
    )

    return [
        {
            "product_name": p.product_name,
            "total_recommended": p.total,
            "applied": p.applied,
            "accepted": p.accepted,
            "conversion_rate": round((p.accepted / p.total * 100) if p.total > 0 else 0, 1),
        }
        for p in products
    ]


@router.get("/analytics/rm-performance")
def get_rm_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    performance = (
        db.query(
            User.full_name,
            User.employee_id,
            sqlfunc.count(Recommendation.id).label("total_recs"),
            sqlfunc.count(Recommendation.id).filter(Recommendation.status == "accepted").label("accepted"),
            sqlfunc.avg(Recommendation.confidence_score).label("avg_confidence"),
        )
        .join(User, User.id == Recommendation.rm_id)
        .group_by(User.id, User.full_name, User.employee_id)
        .all()
    )

    return [
        {
            "name": p.full_name,
            "employee_id": p.employee_id,
            "total_recommendations": p.total_recs,
            "accepted": p.accepted,
            "conversion_rate": round((p.accepted / p.total_recs * 100) if p.total_recs > 0 else 0, 1),
            "avg_confidence": round(float(p.avg_confidence or 0), 1),
        }
        for p in performance
    ]
