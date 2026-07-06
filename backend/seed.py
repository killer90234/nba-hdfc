"""Seed script to create demo users and sample data"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.customer import Customer, CustomerFamily, CustomerEmployment, CustomerBanking, CustomerExistingProduct
from app.models.product import HDFCProduct
from app.models.recommendation import Recommendation
from app.auth.jwt import get_password_hash
from app.services.product_catalogue import HDFC_PRODUCT_CATALOGUE
from datetime import datetime
import uuid


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if users exist
    if db.query(User).count() > 0:
        print("Users already exist. Skipping user seed.")
    else:
        # Create Admin
        admin = User(
            employee_id="HDFC001",
            full_name="Priya Sharma",
            email="priya.sharma@hdfcbank.com",
            phone="9876543210",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            branch="Mumbai Main",
            region="West",
        )
        db.add(admin)

        # Create RM
        rm = User(
            employee_id="HDFC002",
            full_name="Rajesh Kumar",
            email="rajesh.kumar@hdfcbank.com",
            phone="9876543211",
            hashed_password=get_password_hash("rm123"),
            role=UserRole.RELATIONSHIP_MANAGER,
            branch="Mumbai Main",
            region="West",
        )
        db.add(rm)

        # Create Manager
        mgr = User(
            employee_id="HDFC003",
            full_name="Anita Desai",
            email="anita.desai@hdfcbank.com",
            phone="9876543212",
            hashed_password=get_password_hash("mgr123"),
            role=UserRole.MANAGER,
            branch="Delhi Central",
            region="North",
        )
        db.add(mgr)

        db.commit()
        print("Created 3 demo users")

    # Seed HDFC Products
    if db.query(HDFCProduct).count() > 0:
        print("Products already exist. Skipping product seed.")
    else:
        for p in HDFC_PRODUCT_CATALOGUE:
            product = HDFCProduct(**p)
            db.add(product)
        db.commit()
        print(f"Seeded {len(HDFC_PRODUCT_CATALOGUE)} HDFC products")

    # Create sample customers
    if db.query(Customer).count() == 0:
        rm_user = db.query(User).filter(User.employee_id == "HDFC002").first()

        # Customer 1: Rahul Patel - High income, married, 1 child
        c1 = Customer(
            customer_id="HDFC" + uuid.uuid4().hex[:8].upper(),
            full_name="Rahul Patel",
            age=34,
            date_of_birth=datetime(1992, 5, 15),
            gender="Male",
            occupation="Software Architect",
            employer="TCS",
            annual_income=1800000,
            education="M.Tech",
            marital_status="Married",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            pan_number="ABCDE1234F",
            mobile="9876543220",
            email="rahul.patel@email.com",
            kyc_status="verified",
            risk_appetite="moderate",
            rm_id=rm_user.id if rm_user else None,
            customer_since=datetime(2020, 3, 15),
        )
        db.add(c1)
        db.flush()

        db.add(CustomerFamily(
            customer_id=c1.id,
            spouse_name="Neha Patel",
            spouse_age=31,
            spouse_occupation="Product Manager",
            num_children=1,
            child1_age=5,
            child1_education="Pre-school",
            family_income=2800000,
            family_assets=4500000,
            family_investments=1200000,
            family_insurance_value=500000,
            dependent_parents=False,
            parents_senior_citizen=False,
            family_goals="Buy a larger house, start child education fund",
        ))
        db.add(CustomerEmployment(
            customer_id=c1.id,
            employment_type="private",
            monthly_income=150000,
            monthly_expenses=80000,
            salary_date=1,
            years_in_job=8,
            company_category="MNC",
            credit_score=785,
        ))
        db.add(CustomerBanking(
            customer_id=c1.id,
            has_savings_account=True,
            current_balance=450000,
            average_balance=380000,
            salary_credit=150000,
            monthly_debit=75000,
            monthly_credit=160000,
            upi_monthly=35000,
            fd_amount=800000,
        ))

        # Customer 2: Priya Menon - Young professional
        c2 = Customer(
            customer_id="HDFC" + uuid.uuid4().hex[:8].upper(),
            full_name="Priya Menon",
            age=27,
            gender="Female",
            occupation="Data Analyst",
            employer="Infosys",
            annual_income=900000,
            education="MBA",
            marital_status="Single",
            city="Bangalore",
            state="Karnataka",
            pincode="560001",
            pan_number="FGHIJ5678K",
            mobile="9876543221",
            email="priya.menon@email.com",
            kyc_status="verified",
            risk_appetite="aggressive",
            rm_id=rm_user.id if rm_user else None,
            customer_since=datetime(2022, 7, 1),
        )
        db.add(c2)
        db.flush()

        db.add(CustomerEmployment(
            customer_id=c2.id,
            employment_type="private",
            monthly_income=75000,
            monthly_expenses=40000,
            salary_date=5,
            years_in_job=3,
            company_category="MNC",
            credit_score=720,
        ))
        db.add(CustomerBanking(
            customer_id=c2.id,
            has_savings_account=True,
            current_balance=120000,
            average_balance=95000,
            salary_credit=75000,
            monthly_debit=38000,
            monthly_credit=80000,
            upi_monthly=20000,
            rd_amount=100000,
        ))

        # Customer 3: Suresh Reddy - Business owner
        c3 = Customer(
            customer_id="HDFC" + uuid.uuid4().hex[:8].upper(),
            full_name="Suresh Reddy",
            age=48,
            gender="Male",
            occupation="Business Owner",
            employer="Reddy Industries",
            annual_income=5000000,
            education="B.Com",
            marital_status="Married",
            city="Hyderabad",
            state="Telangana",
            pincode="500001",
            pan_number="KLMNO9012P",
            mobile="9876543222",
            email="suresh.reddy@email.com",
            kyc_status="verified",
            risk_appetite="moderate",
            rm_id=rm_user.id if rm_user else None,
            customer_since=datetime(2018, 1, 10),
        )
        db.add(c3)
        db.flush()

        db.add(CustomerFamily(
            customer_id=c3.id,
            spouse_name="Lakshmi Reddy",
            spouse_age=44,
            num_children=2,
            child1_age=20,
            child1_education="Engineering Student",
            child2_age=16,
            child2_education="Class 11",
            family_income=6000000,
            family_assets=15000000,
            family_investments=4000000,
            family_insurance_value=2000000,
            dependent_parents=True,
            parents_senior_citizen=True,
            family_goals="Children education, retirement planning, business expansion",
        ))
        db.add(CustomerEmployment(
            customer_id=c3.id,
            employment_type="business",
            monthly_income=400000,
            monthly_expenses=150000,
            years_in_job=20,
            company_category="MSME",
            business_turnover=5000000,
            gst_registered=True,
            credit_score=810,
        ))
        db.add(CustomerBanking(
            customer_id=c3.id,
            has_savings_account=True,
            has_current_account=True,
            current_balance=2500000,
            average_balance=2000000,
            monthly_debit=300000,
            monthly_credit=400000,
            cash_deposit_monthly=500000,
            fd_amount=1500000,
        ))

        # Customer 4: Kavita Joshi - Senior
        c4 = Customer(
            customer_id="HDFC" + uuid.uuid4().hex[:8].upper(),
            full_name="Kavita Joshi",
            age=62,
            gender="Female",
            occupation="Retired Teacher",
            annual_income=400000,
            education="M.A.",
            marital_status="Widowed",
            city="Pune",
            state="Maharashtra",
            pincode="411001",
            pan_number="PQRST3456U",
            mobile="9876543223",
            email="kavita.joshi@email.com",
            kyc_status="verified",
            risk_appetite="conservative",
            rm_id=rm_user.id if rm_user else None,
            customer_since=datetime(2015, 6, 20),
        )
        db.add(c4)
        db.flush()

        db.add(CustomerFamily(
            customer_id=c4.id,
            num_children=1,
            child1_age=35,
            child1_education="Doctor",
            family_income=400000,
            family_assets=3000000,
            family_investments=1800000,
            family_insurance_value=1000000,
            dependent_parents=False,
            parents_senior_citizen=False,
            family_goals="Safe retirement income, health coverage",
        ))
        db.add(CustomerEmployment(
            customer_id=c4.id,
            employment_type="retired",
            monthly_income=33000,
            monthly_expenses=25000,
            credit_score=750,
        ))
        db.add(CustomerBanking(
            customer_id=c4.id,
            has_savings_account=True,
            has_fd=True,
            current_balance=800000,
            average_balance=750000,
            fd_amount=1800000,
        ))

        # Add existing products for each customer
        # Customer 1: Rahul - has savings + FD + millennia
        c1_savings = db.query(HDFCProduct).filter(HDFCProduct.name == "Savings Max Account").first()
        c1_fd = db.query(HDFCProduct).filter(HDFCProduct.name == "Fixed Deposit").first()
        c1_mill = db.query(HDFCProduct).filter(HDFCProduct.name == "Millennia Credit Card").first()
        if c1_savings:
            db.add(CustomerExistingProduct(customer_id=c1.id, product_id=c1_savings.id, product_name="Savings Max Account", product_category="accounts", status="active"))
        if c1_fd:
            db.add(CustomerExistingProduct(customer_id=c1.id, product_id=c1_fd.id, product_name="Fixed Deposit", product_category="investments", status="active"))
        if c1_mill:
            db.add(CustomerExistingProduct(customer_id=c1.id, product_id=c1_mill.id, product_name="Millennia Credit Card", product_category="credit_cards", status="active"))

        # Customer 2: Priya - has savings + RD only
        c2_savings = db.query(HDFCProduct).filter(HDFCProduct.name == "Regular Savings Account").first()
        c2_rd = db.query(HDFCProduct).filter(HDFCProduct.name == "Recurring Deposit").first()
        if c2_savings:
            db.add(CustomerExistingProduct(customer_id=c2.id, product_id=c2_savings.id, product_name="Regular Savings Account", product_category="accounts", status="active"))
        if c2_rd:
            db.add(CustomerExistingProduct(customer_id=c2.id, product_id=c2_rd.id, product_name="Recurring Deposit", product_category="investments", status="active"))

        # Customer 3: Suresh - has current account + FD + FASTag
        c3_current = db.query(HDFCProduct).filter(HDFCProduct.name == "Current Account").first()
        c3_fd = db.query(HDFCProduct).filter(HDFCProduct.name == "Fixed Deposit").first()
        c3_fastag = db.query(HDFCProduct).filter(HDFCProduct.name == "FASTag").first()
        c3_biz = db.query(HDFCProduct).filter(HDFCProduct.name == "Business MoneyBack").first()
        if c3_current:
            db.add(CustomerExistingProduct(customer_id=c3.id, product_id=c3_current.id, product_name="Current Account", product_category="accounts", status="active"))
        if c3_fd:
            db.add(CustomerExistingProduct(customer_id=c3.id, product_id=c3_fd.id, product_name="Fixed Deposit", product_category="investments", status="active"))
        if c3_fastag:
            db.add(CustomerExistingProduct(customer_id=c3.id, product_id=c3_fastag.id, product_name="FASTag", product_category="digital", status="active"))
        if c3_biz:
            db.add(CustomerExistingProduct(customer_id=c3.id, product_id=c3_biz.id, product_name="Business MoneyBack", product_category="credit_cards", status="active"))

        # Customer 4: Kavita - has savings + FD + health insurance
        c4_savings = db.query(HDFCProduct).filter(HDFCProduct.name == "Senior Citizen Savings Account").first()
        c4_fd = db.query(HDFCProduct).filter(HDFCProduct.name == "Fixed Deposit").first()
        c4_health = db.query(HDFCProduct).filter(HDFCProduct.name == "HDFC Health Insurance").first()
        if c4_savings:
            db.add(CustomerExistingProduct(customer_id=c4.id, product_id=c4_savings.id, product_name="Senior Citizen Savings Account", product_category="accounts", status="active"))
        if c4_fd:
            db.add(CustomerExistingProduct(customer_id=c4.id, product_id=c4_fd.id, product_name="Fixed Deposit", product_category="investments", status="active"))
        if c4_health:
            db.add(CustomerExistingProduct(customer_id=c4.id, product_id=c4_health.id, product_name="HDFC Health Insurance", product_category="insurance", status="active"))

        db.commit()
        print("Created 4 sample customers with full profiles and existing products")
    else:
        print("Customers already exist. Skipping customer seed.")

    db.close()
    print("\nSeed completed!")
    print("\nDemo Credentials:")
    print("  Admin:  HDFC001 / admin123")
    print("  RM:     HDFC002 / rm123")
    print("  Manager: HDFC003 / mgr123")


if __name__ == "__main__":
    seed()
