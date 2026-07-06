import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.customer import Customer, CustomerFamily, CustomerEmployment, CustomerBanking, CustomerExistingProduct
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse, CustomerFullProfile,
    FamilyCreate, FamilyResponse, EmploymentCreate, EmploymentResponse,
    BankingCreate, BankingResponse, ExistingProductCreate, ExistingProductResponse,
)
from app.auth.jwt import get_current_user, require_role

router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.get("/search", response_model=list[CustomerResponse])
def search_customers(
    q: str = Query(default=""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not q or q.strip() == "":
        customers = db.query(Customer).order_by(Customer.created_at.desc()).limit(50).all()
        return customers

    customers = db.query(Customer).filter(
        or_(
            Customer.full_name.ilike(f"%{q}%"),
            Customer.customer_id.ilike(f"%{q}%"),
            Customer.mobile.ilike(f"%{q}%"),
            Customer.email.ilike(f"%{q}%"),
            Customer.pan_number.ilike(f"%{q}%"),
            Customer.city.ilike(f"%{q}%"),
            Customer.occupation.ilike(f"%{q}%"),
        )
    ).limit(50).all()
    return customers


@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer_id = f"HDFC{uuid.uuid4().hex[:8].upper()}"
    customer = Customer(
        customer_id=customer_id,
        full_name=data.full_name,
        age=data.age,
        date_of_birth=data.date_of_birth,
        gender=data.gender,
        occupation=data.occupation,
        employer=data.employer,
        annual_income=data.annual_income,
        education=data.education,
        marital_status=data.marital_status,
        address=data.address,
        city=data.city,
        state=data.state,
        pincode=data.pincode,
        pan_number=data.pan_number,
        aadhaar_masked=data.aadhaar_masked,
        email=data.email,
        mobile=data.mobile,
        kyc_status=data.kyc_status,
        preferred_language=data.preferred_language,
        risk_appetite=data.risk_appetite,
        rm_id=current_user.id,
        customer_since=datetime.utcnow(),
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/{customer_id}", response_model=CustomerFullProfile)
def get_customer_profile(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    family = db.query(CustomerFamily).filter(CustomerFamily.customer_id == customer.id).first()
    employment = db.query(CustomerEmployment).filter(CustomerEmployment.customer_id == customer.id).first()
    banking = db.query(CustomerBanking).filter(CustomerBanking.customer_id == customer.id).first()
    existing = db.query(CustomerExistingProduct).filter(CustomerExistingProduct.customer_id == customer.id).all()

    return CustomerFullProfile(
        customer=CustomerResponse.from_orm(customer),
        family=FamilyResponse.from_orm(family) if family else None,
        employment=EmploymentResponse.from_orm(employment) if employment else None,
        banking=BankingResponse.from_orm(banking) if banking else None,
        existing_products=[ExistingProductResponse.from_orm(p) for p in existing],
    )


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer


# ── Family Details ──
@router.post("/{customer_id}/family", response_model=FamilyResponse, status_code=201)
def upsert_family(
    customer_id: int,
    data: FamilyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    existing = db.query(CustomerFamily).filter(CustomerFamily.customer_id == customer.id).first()
    if existing:
        for field, value in data.dict(exclude_unset=True).items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    family = CustomerFamily(customer_id=customer.id, **data.dict())
    db.add(family)
    db.commit()
    db.refresh(family)
    return family


# ── Employment Details ──
@router.post("/{customer_id}/employment", response_model=EmploymentResponse, status_code=201)
def upsert_employment(
    customer_id: int,
    data: EmploymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    existing = db.query(CustomerEmployment).filter(CustomerEmployment.customer_id == customer.id).first()
    if existing:
        for field, value in data.dict(exclude_unset=True).items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    emp = CustomerEmployment(customer_id=customer.id, **data.dict())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


# ── Banking Details ──
@router.post("/{customer_id}/banking", response_model=BankingResponse, status_code=201)
def upsert_banking(
    customer_id: int,
    data: BankingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    existing = db.query(CustomerBanking).filter(CustomerBanking.customer_id == customer.id).first()
    if existing:
        for field, value in data.dict(exclude_unset=True).items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    bank = CustomerBanking(customer_id=customer.id, **data.dict())
    db.add(bank)
    db.commit()
    db.refresh(bank)
    return bank


# ── Existing Products ──
@router.post("/{customer_id}/products", response_model=ExistingProductResponse, status_code=201)
def add_existing_product(
    customer_id: str,
    data: ExistingProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    product = CustomerExistingProduct(customer_id=customer.id, **data.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/{customer_id}/products", response_model=list[ExistingProductResponse])
def list_existing_products(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return db.query(CustomerExistingProduct).filter(CustomerExistingProduct.customer_id == customer.id).all()


@router.delete("/{customer_id}/products/{product_id}")
def remove_existing_product(
    customer_id: str,
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    product = db.query(CustomerExistingProduct).filter(
        CustomerExistingProduct.id == product_id,
        CustomerExistingProduct.customer_id == customer.id,
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product removed"}
