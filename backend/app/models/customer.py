from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(20), unique=True, nullable=False, index=True)

    # Personal Details
    full_name = Column(String(150), nullable=False)
    age = Column(Integer)
    date_of_birth = Column(DateTime)
    gender = Column(String(10))
    occupation = Column(String(100))
    employer = Column(String(150))
    annual_income = Column(Float)
    education = Column(String(100))
    marital_status = Column(String(20))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    pan_number = Column(String(10))
    aadhaar_masked = Column(String(12))
    email = Column(String(150))
    mobile = Column(String(15))
    kyc_status = Column(String(20), default="pending")
    preferred_language = Column(String(30), default="English")
    risk_appetite = Column(String(20), default="moderate")

    # Relationship Manager
    rm_id = Column(Integer, ForeignKey("users.id"))
    customer_since = Column(DateTime)
    total_relationship_value = Column(Float, default=0)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    family_details = relationship("CustomerFamily", back_populates="customer", uselist=False)
    employment_details = relationship("CustomerEmployment", back_populates="customer", uselist=False)
    banking_details = relationship("CustomerBanking", back_populates="customer", uselist=False)
    existing_products = relationship("CustomerExistingProduct", back_populates="customer")
    recommendations = relationship("Recommendation", back_populates="customer")


class CustomerFamily(Base):
    __tablename__ = "customer_family"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), unique=True, nullable=False)

    father_name = Column(String(150))
    father_age = Column(Integer)
    father_alive = Column(Boolean, default=True)
    father_occupation = Column(String(100))

    mother_name = Column(String(150))
    mother_age = Column(Integer)
    mother_alive = Column(Boolean, default=True)
    mother_occupation = Column(String(100))

    spouse_name = Column(String(150))
    spouse_age = Column(Integer)
    spouse_occupation = Column(String(100))
    marriage_anniversary = Column(DateTime)

    num_children = Column(Integer, default=0)
    child1_age = Column(Integer)
    child1_education = Column(String(100))
    child2_age = Column(Integer)
    child2_education = Column(String(100))
    child3_age = Column(Integer)

    family_income = Column(Float)
    family_medical_history = Column(Text)
    parents_senior_citizen = Column(Boolean, default=False)
    family_business = Column(Boolean, default=False)
    family_assets = Column(Float, default=0)
    family_liabilities = Column(Float, default=0)
    family_investments = Column(Float, default=0)
    family_insurance_value = Column(Float, default=0)
    family_goals = Column(Text)
    dependent_parents = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("Customer", back_populates="family_details")


class CustomerEmployment(Base):
    __tablename__ = "customer_employment"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), unique=True, nullable=False)

    employment_type = Column(String(30))  # government, private, business, professional, retired, self_employed, student
    monthly_income = Column(Float)
    monthly_expenses = Column(Float)
    salary_date = Column(Integer)  # day of month
    years_in_job = Column(Integer)
    company_category = Column(String(50))  # MNC, PSU, Startup, MSME, etc.
    business_turnover = Column(Float)
    gst_registered = Column(Boolean, default=False)
    credit_score = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("Customer", back_populates="employment_details")


class CustomerBanking(Base):
    __tablename__ = "customer_banking"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), unique=True, nullable=False)

    has_savings_account = Column(Boolean, default=False)
    has_salary_account = Column(Boolean, default=False)
    has_current_account = Column(Boolean, default=False)
    has_nre_account = Column(Boolean, default=False)
    has_nro_account = Column(Boolean, default=False)
    has_fd = Column(Boolean, default=False)
    has_rd = Column(Boolean, default=False)

    current_balance = Column(Float, default=0)
    average_balance = Column(Float, default=0)
    salary_credit = Column(Float, default=0)
    monthly_debit = Column(Float, default=0)
    monthly_credit = Column(Float, default=0)
    cash_deposit_monthly = Column(Float, default=0)
    cash_withdrawal_monthly = Column(Float, default=0)
    upi_monthly = Column(Float, default=0)
    neft_monthly = Column(Float, default=0)
    rtgs_monthly = Column(Float, default=0)
    imps_monthly = Column(Float, default=0)
    atm_usage_monthly = Column(Integer, default=0)
    cheque_usage_monthly = Column(Integer, default=0)

    fd_amount = Column(Float, default=0)
    rd_amount = Column(Float, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("Customer", back_populates="banking_details")


class CustomerExistingProduct(Base):
    __tablename__ = "customer_existing_products"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("hdfc_products.id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    product_category = Column(String(50))
    account_number = Column(String(30))
    status = Column(String(20), default="active")
    since_date = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", back_populates="existing_products")
