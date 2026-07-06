from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.product import HDFCProduct
from app.schemas.product import ProductResponse, ProductCreate
from app.auth.jwt import get_current_user, require_role
from app.services.product_catalogue import HDFC_PRODUCT_CATALOGUE

router = APIRouter(prefix="/api/products", tags=["HDFC Products"])


@router.get("", response_model=list[ProductResponse])
def list_products(
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(HDFCProduct).filter(HDFCProduct.is_active == True)
    if category:
        query = query.filter(HDFCProduct.category == category)
    return query.all()


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    categories = db.query(HDFCProduct.category).distinct().all()
    return [c[0] for c in categories]


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(HDFCProduct).filter(HDFCProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/seed", status_code=201)
def seed_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    existing = db.query(HDFCProduct).count()
    if existing > 0:
        return {"message": f"Already {existing} products in database"}

    for p in HDFC_PRODUCT_CATALOGUE:
        product = HDFCProduct(**p)
        db.add(product)
    db.commit()

    return {"message": f"Seeded {len(HDFC_PRODUCT_CATALOGUE)} HDFC products"}


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    product = HDFCProduct(**data.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    product = db.query(HDFCProduct).filter(HDFCProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product
