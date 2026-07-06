from typing import List, Dict, Any
from app.models.product import HDFCProduct
from app.models.customer import Customer, CustomerFamily, CustomerEmployment, CustomerBanking, CustomerExistingProduct


class RuleEngine:
    def evaluate(self, customer, family, employment, banking, existing_product_ids: List[int]) -> List[Dict]:
        rules = []

        # Age-based rules
        if customer.age:
            if customer.age >= 60:
                rules.append({
                    "rule": "SENIOR_CITIZEN",
                    "weight": 25,
                    "products": ["Senior Citizen Savings Account", "HDFC Health Insurance", "Fixed Deposit"],
                    "reason": "Senior citizen benefits and protection needed"
                })
            elif customer.age <= 25:
                rules.append({
                    "rule": "YOUNG_PROFESSIONAL",
                    "weight": 20,
                    "products": ["Millennia Credit Card", "SIP", "FASTag"],
                    "reason": "Young professional - digital-first products"
                })
            elif 25 <= customer.age <= 35:
                rules.append({
                    "rule": "CAREER_BUILDING",
                    "weight": 22,
                    "products": ["Regalia Gold Credit Card", "Home Loan", "HDFC Term Insurance"],
                    "reason": "Career growth phase - wealth and protection"
                })

        # Income-based rules
        if employment and employment.monthly_income:
            annual = employment.monthly_income * 12
            if annual >= 3000000:
                rules.append({
                    "rule": "HIGH_INCOME",
                    "weight": 30,
                    "products": ["Infinia Credit Card", "Diners Club Black", "Business Loan"],
                    "reason": "High income - premium products eligible"
                })
            elif annual >= 1200000:
                rules.append({
                    "rule": "MID_HIGH_INCOME",
                    "weight": 25,
                    "products": ["Regalia Gold Credit Card", "Home Loan", "HDFC Life Insurance"],
                    "reason": "Good income - premium products viable"
                })
            elif annual >= 500000:
                rules.append({
                    "rule": "MID_INCOME",
                    "weight": 20,
                    "products": ["MoneyBack+ Credit Card", "Car Loan", "SIP"],
                    "reason": "Mid income - value products"
                })

        # Family rules
        if family:
            if family.num_children and family.num_children > 0:
                rules.append({
                    "rule": "PARENT",
                    "weight": 22,
                    "products": ["HDFC Health Insurance", "HDFC Education Loan", "SIP"],
                    "reason": "Children detected - protection and education planning"
                })

            if family.marriage_anniversary:
                rules.append({
                    "rule": "MARRIED",
                    "weight": 15,
                    "products": ["Joint Account", "Home Loan", "HDFC Life Insurance"],
                    "reason": "Married - joint financial planning"
                })

            if family.dependent_parents or family.parents_senior_citizen:
                rules.append({
                    "rule": "DEPENDENT_PARENTS",
                    "weight": 20,
                    "products": ["HDFC Health Insurance", "Senior Citizen Account"],
                    "reason": "Dependent parents - family health coverage"
                })

            if family.family_goals:
                goals_lower = family.family_goals.lower()
                if "home" in goals_lower or "house" in goals_lower:
                    rules.append({"rule": "HOME_BUYER", "weight": 25, "products": ["Home Loan"], "reason": "Home buying goal"})
                if "education" in goals_lower:
                    rules.append({"rule": "EDUCATION_GOAL", "weight": 22, "products": ["Education Loan", "SIP"], "reason": "Education planning goal"})
                if "retirement" in goals_lower:
                    rules.append({"rule": "RETIREMENT_GOAL", "weight": 20, "products": ["NPS", "Fixed Deposit", "HDFC Life Insurance"], "reason": "Retirement planning"})

        # Banking behavior rules
        if banking:
            if banking.upi_monthly and banking.upi_monthly > 20000:
                rules.append({
                    "rule": "HEAVY_UPI_USER",
                    "weight": 18,
                    "products": ["PayZapp", "Millennia Credit Card"],
                    "reason": "Heavy digital payments user"
                })

            if banking.cash_deposit_monthly and banking.cash_deposit_monthly > 100000:
                rules.append({
                    "rule": "HEAVY_CASH_USER",
                    "weight": 15,
                    "products": ["Current Account", "Merchant QR"],
                    "reason": "High cash handling - business account needed"
                })

            if banking.fd_amount and banking.fd_amount >= 500000:
                rules.append({
                    "rule": "FD_HOLDER",
                    "weight": 18,
                    "products": ["SIP", "Mutual Funds", "NPS"],
                    "reason": "Existing FD holder - diversify investments"
                })

            if banking.current_balance and banking.current_balance > 500000:
                rules.append({
                    "rule": "HIGH_BALANCE",
                    "weight": 20,
                    "products": ["Savings Max Account", "Fixed Deposit", "SIP"],
                    "reason": "High balance - optimize returns"
                })

        # Employment rules
        if employment:
            if employment.employment_type == "business":
                rules.append({
                    "rule": "BUSINESS_OWNER",
                    "weight": 22,
                    "products": ["Current Account", "Business Loan", "BizGrow Credit Card", "POS Machine"],
                    "reason": "Business owner - business banking products"
                })
            elif employment.employment_type == "government":
                rules.append({
                    "rule": "GOVT_EMPLOYEE",
                    "weight": 18,
                    "products": ["Salary Account", "Home Loan", "NPS"],
                    "reason": "Government employee - stable income products"
                })
            elif employment.employment_type == "self_employed":
                rules.append({
                    "rule": "SELF_EMPLOYED",
                    "weight": 20,
                    "products": ["Current Account", "Business Loan", "MSME Loan"],
                    "reason": "Self-employed - business growth products"
                })

            if employment.credit_score and employment.credit_score >= 750:
                rules.append({
                    "rule": "EXCELLENT_CREDIT",
                    "weight": 25,
                    "products": ["Infinia Credit Card", "Personal Loan", "Home Loan"],
                    "reason": "Excellent credit score - best rates available"
                })

        # Filter out existing products
        for rule in rules:
            rule["filtered_products"] = [p for p in rule["products"] if p not in existing_product_ids]

        return rules


class EligibilityEngine:
    def check(self, customer, employment, banking, product: HDFCProduct) -> Dict:
        eligible = True
        reasons = []

        # Age check
        if product.min_age and customer.age and customer.age < product.min_age:
            eligible = False
            reasons.append(f"Below minimum age {product.min_age}")
        if product.max_age and customer.age and customer.age > product.max_age:
            eligible = False
            reasons.append(f"Above maximum age {product.max_age}")

        # Income check
        if product.min_income and employment and employment.monthly_income:
            annual = employment.monthly_income * 12
            if annual < product.min_income:
                eligible = False
                reasons.append(f"Income below ₹{product.min_income/100000:.1f}L required")

        # Credit score check
        if product.min_credit_score and product.min_credit_score > 0:
            if employment and employment.credit_score:
                if employment.credit_score < product.min_credit_score:
                    eligible = False
                    reasons.append(f"Credit score below {product.min_credit_score}")

        # Occupation check
        if product.occupation_types and "all" not in product.occupation_types:
            if employment and employment.employment_type:
                if employment.employment_type not in product.occupation_types:
                    eligible = False
                    reasons.append(f"Occupation type '{employment.employment_type}' not eligible")

        return {
            "eligible": eligible,
            "reasons": reasons,
            "status": "eligible" if eligible else "not_eligible",
        }


class ProductRanker:
    def rank(self, customer, employment, banking, recommendations: List[Dict], rules: List[Dict]) -> List[Dict]:
        for rec in recommendations:
            base_score = rec.get("confidence", 70)

            # Rule engine boost
            rule_boost = 0
            for rule in rules:
                if rec["product"] in rule.get("products", []):
                    rule_boost = max(rule_boost, rule.get("weight", 0) * 0.3)

            # Eligibility boost
            elig_boost = 5 if rec.get("eligibility_status") == "eligible" else -10

            # Recency boost (if customer has recent activity)
            activity_boost = 0
            if banking:
                if banking.upi_monthly and banking.upi_monthly > 10000:
                    activity_boost += 3

            final_score = min(99, base_score + rule_boost + elig_boost + activity_boost)
            rec["confidence"] = round(final_score, 1)
            rec["acceptance_probability"] = round(final_score * 0.98, 1)

        recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        return recommendations[:3]
