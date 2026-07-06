from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ── Customer Core ──
class CustomerCreate(BaseModel):
    full_name: str
    age: Optional[int] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    employer: Optional[str] = None
    annual_income: Optional[float] = None
    education: Optional[str] = None
    marital_status: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    pan_number: Optional[str] = None
    aadhaar_masked: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    kyc_status: str = "pending"
    preferred_language: str = "English"
    risk_appetite: str = "moderate"


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    employer: Optional[str] = None
    annual_income: Optional[float] = None
    education: Optional[str] = None
    marital_status: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    risk_appetite: Optional[str] = None
    preferred_language: Optional[str] = None


class CustomerResponse(BaseModel):
    id: int
    customer_id: str
    full_name: str
    age: Optional[int]
    gender: Optional[str]
    occupation: Optional[str]
    employer: Optional[str]
    annual_income: Optional[float]
    education: Optional[str]
    marital_status: Optional[str]
    city: Optional[str]
    state: Optional[str]
    email: Optional[str]
    mobile: Optional[str]
    kyc_status: str
    risk_appetite: str
    total_relationship_value: float
    customer_since: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Family ──
class FamilyCreate(BaseModel):
    father_name: Optional[str] = None
    father_age: Optional[int] = None
    father_alive: bool = True
    father_occupation: Optional[str] = None
    mother_name: Optional[str] = None
    mother_age: Optional[int] = None
    mother_alive: bool = True
    mother_occupation: Optional[str] = None
    spouse_name: Optional[str] = None
    spouse_age: Optional[int] = None
    spouse_occupation: Optional[str] = None
    marriage_anniversary: Optional[datetime] = None
    num_children: int = 0
    child1_age: Optional[int] = None
    child1_education: Optional[str] = None
    child2_age: Optional[int] = None
    child2_education: Optional[str] = None
    child3_age: Optional[int] = None
    family_income: Optional[float] = None
    family_medical_history: Optional[str] = None
    parents_senior_citizen: bool = False
    family_business: bool = False
    family_assets: float = 0
    family_liabilities: float = 0
    family_investments: float = 0
    family_insurance_value: float = 0
    family_goals: Optional[str] = None
    dependent_parents: bool = False


class FamilyResponse(FamilyCreate):
    id: int
    customer_id: int

    class Config:
        from_attributes = True


# ── Employment ──
class EmploymentCreate(BaseModel):
    employment_type: Optional[str] = None
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    salary_date: Optional[int] = None
    years_in_job: Optional[int] = None
    company_category: Optional[str] = None
    business_turnover: Optional[float] = None
    gst_registered: bool = False
    credit_score: Optional[int] = None


class EmploymentResponse(EmploymentCreate):
    id: int
    customer_id: int

    class Config:
        from_attributes = True


# ── Banking ──
class BankingCreate(BaseModel):
    has_savings_account: bool = False
    has_salary_account: bool = False
    has_current_account: bool = False
    has_nre_account: bool = False
    has_nro_account: bool = False
    has_fd: bool = False
    has_rd: bool = False
    current_balance: float = 0
    average_balance: float = 0
    salary_credit: float = 0
    monthly_debit: float = 0
    monthly_credit: float = 0
    cash_deposit_monthly: float = 0
    cash_withdrawal_monthly: float = 0
    upi_monthly: float = 0
    neft_monthly: float = 0
    rtgs_monthly: float = 0
    imps_monthly: float = 0
    atm_usage_monthly: int = 0
    cheque_usage_monthly: int = 0
    fd_amount: float = 0
    rd_amount: float = 0


class BankingResponse(BankingCreate):
    id: int
    customer_id: int

    class Config:
        from_attributes = True


# ── Existing Products ──
class ExistingProductCreate(BaseModel):
    product_id: int
    product_name: str
    product_category: Optional[str] = None
    account_number: Optional[str] = None
    status: str = "active"
    since_date: Optional[datetime] = None


class ExistingProductResponse(ExistingProductCreate):
    id: int
    customer_id: int

    class Config:
        from_attributes = True


# ── Full Customer Profile ──
class CustomerFullProfile(BaseModel):
    customer: CustomerResponse
    family: Optional[FamilyResponse] = None
    employment: Optional[EmploymentResponse] = None
    banking: Optional[BankingResponse] = None
    existing_products: List[ExistingProductResponse] = []


class CustomerSearch(BaseModel):
    query: str
