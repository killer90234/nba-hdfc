import json
import google.generativeai as genai
from app.config import get_settings

settings = get_settings()

if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY not in ("your-gemini-api-key-here", ""):
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
    except Exception:
        pass


def build_gemini_prompt(customer_data: dict) -> str:
    existing = customer_data.get("current_products", [])
    age = customer_data.get("age", 0)
    income = customer_data.get("annual_income", 0)
    credit = customer_data.get("credit_score", 0)
    married = customer_data.get("married", False)
    children = customer_data.get("num_children", 0)
    occupation = customer_data.get("occupation", "")
    city = customer_data.get("city", "")
    risk = customer_data.get("risk_appetite", "moderate")
    balance = customer_data.get("current_balance", 0)
    fd = customer_data.get("fd_amount", 0)
    surplus = (customer_data.get("monthly_income", 0) or 0) - (customer_data.get("monthly_expenses", 0) or 0)

    return f"""You are HDFC Bank's AI Relationship Manager. Analyze this customer and recommend the BEST 3 HDFC Bank products they don't already own.

CUSTOMER SNAPSHOT:
- Name: {customer_data.get('name', 'N/A')}, Age: {age}, Gender: {customer_data.get('gender', 'N/A')}
- Occupation: {occupation} at {customer_data.get('employer', 'N/A')} ({customer_data.get('employment_type', 'N/A')})
- Annual Income: ₹{income:,.0f} | Monthly: ₹{customer_data.get('monthly_income', 0):,.0f}
- Credit Score: {credit} | Risk: {risk}
- Marital Status: {customer_data.get('marital_status', 'N/A')} | Children: {children}
- City: {city}
- Monthly Surplus: ₹{surplus:,.0f}
- Current Balance: ₹{balance:,.0f} | FD: ₹{fd:,.0f}
- UPI Monthly: ₹{customer_data.get('upi_monthly', 0):,.0f}

EXISTING HDFC PRODUCTS (NEVER RECOMMEND THESE):
{json.dumps(existing, indent=2)}

FAMILY CONTEXT:
- Spouse: {customer_data.get('spouse_name', 'None')} (Age: {customer_data.get('spouse_age', 'N/A')})
- Children Ages: {customer_data.get('child1_age', '-')}, {customer_data.get('child2_age', '-')}
- Dependent Parents: {customer_data.get('dependent_parents', False)}
- Parents Senior Citizen: {customer_data.get('parents_senior_citizen', False)}
- Family Income: ₹{customer_data.get('family_income', 0):,.0f}
- Family Goals: {customer_data.get('family_goals', 'None specified')}

HDFC BANK PRODUCT CATALOGUE:
ACCOUNTS: Regular Savings, Savings Max, Senior Citizen, Kids Advantage, Women's Savings, Salary Account, Current Account
CREDIT CARDS: Millennia (min ₹3L income), Regalia Gold (min ₹12L, travel), Infinia (min ₹30L, super-premium), Diners Club Black (min ₹30L, dining), MoneyBack+ (cashback), IndianOil (fuel), Tata Neu Infinity (Tata ecosystem), Swiggy HDFC (food), Marriott Bonvoy (hotels), Business MoneyBack (business), BizGrow (SME)
LOANS: Personal Loan, Home Loan, Car Loan, Gold Loan, Education Loan, Loan Against Property, Business Loan, MSME Loan, Working Capital, Two Wheeler Loan
INVESTMENTS: Fixed Deposit, Recurring Deposit, SIP, Mutual Funds, Demat, NPS
INSURANCE: HDFC Life Insurance, HDFC Health Insurance, HDFC Term Insurance, HDFC Travel Insurance, HDFC Motor Insurance
DIGITAL: FASTag, PayZapp, Forex Card, Merchant QR, POS Machine

ANALYSIS REQUIREMENTS:
1. Gap Analysis: What critical products are MISSING? (Protection gap, investment gap, credit gap)
2. Life Stage Matching: What products match their CURRENT life stage?
3. Income Optimization: How can they get MORE value from their income?
4. Family Protection: Are family members adequately COVERED?
5. Goal Alignment: Which products help achieve their STATED goals?
6. Spending Patterns: High UPI = suggest credit card rewards. High cash = suggest business account.
7. Age-Appropriate: Don't suggest retirement products to 25-year-olds. Don't suggest growth products to 60+.

CONFIDENCE SCORING (be strict):
- 95-100: Perfect fit, customer almost certain to accept
- 85-94: Strong fit, high acceptance probability
- 75-84: Good fit, moderate acceptance
- Below 75: Weak fit, skip it

Return ONLY this JSON format:
{{
    "recommendations": [
        {{
            "product": "Exact Product Name",
            "category": "credit_cards|insurance|investments|loans|accounts|digital",
            "confidence": 95,
            "acceptance_probability": 92,
            "reason": "WHY this specific product for THIS specific customer. Reference their income, age, family, goals, and gaps.",
            "benefits": ["Specific benefit 1", "Specific benefit 2", "Specific benefit 3"],
            "eligibility_status": "eligible|conditionally_eligible",
            "monthly_cost": "₹X,XXX/month or N/A",
            "expected_roi": "description if investment/insurance"
        }}
    ],
    "customer_insights": {{
        "life_stage": "specific life stage description",
        "financial_health": "Excellent|Good|Average|Needs Attention",
        "key_needs": ["need1", "need2", "need3"],
        "protection_gap": "description of what's missing",
        "investment_gap": "description",
        "credit_gap": "description"
    }}
}}"""


async def get_gemini_recommendations(customer_data: dict) -> dict:
    try:
        if settings.GEMINI_API_KEY in ("your-gemini-api-key-here", "", "AIzaSyDummyKeyForNow"):
            print("[AI] Using fallback recommendation engine (no valid Gemini key)")
            return _fallback_recommendations(customer_data)

        print(f"[AI] Calling Gemini API for customer: {customer_data.get('name', 'unknown')}")
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = build_gemini_prompt(customer_data)
        response = model.generate_content(prompt)

        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            if text.endswith("```"):
                text = text[:-3]

        result = json.loads(text.strip())
        if "recommendations" not in result:
            print("[AI] Gemini response missing recommendations, using fallback")
            return _fallback_recommendations(customer_data)

        print(f"[AI] Gemini returned {len(result['recommendations'])} recommendations")
        return result

    except Exception as e:
        print(f"[AI] Gemini API error: {e}")
        return _fallback_recommendations(customer_data)


def _fallback_recommendations(data: dict) -> dict:
    age = data.get("age", 30)
    income = data.get("annual_income", 0)
    if not income:
        mi = data.get("monthly_income", 0)
        income = mi * 12 if mi else 500000
    credit_score = data.get("credit_score", 700)
    married = data.get("married", False) or str(data.get("marital_status", "")).lower() == "married"
    children = data.get("children", data.get("num_children", 0))
    existing = [str(p).lower() for p in data.get("current_products", [])]
    existing_text = " ".join(existing)
    occupation = str(data.get("occupation", "")).lower()
    city = str(data.get("city", "")).lower()
    risk = str(data.get("risk_appetite", "moderate")).lower()

    monthly_income = data.get("monthly_income", income / 12)
    monthly_expenses = data.get("monthly_expenses", monthly_income * 0.6)
    surplus = max(0, monthly_income - monthly_expenses)
    balance = data.get("current_balance", 0)
    fd = data.get("fd_amount", 0)
    upi = data.get("upi_monthly", 0)
    family_goals = str(data.get("family_goals", "")).lower()
    dependent_parents = data.get("dependent_parents", False)
    parents_senior = data.get("parents_senior_citizen", False)
    child1_age = data.get("child1_age", 0) or 0
    child2_age = data.get("child2_age", 0) or 0

    scored_products = []

    # ─── CREDIT CARDS ───
    has_cc = any(c in existing_text for c in ["credit card", "regalia", "infinia", "millennia", "diners", "moneyback", "bizgrow"])
    if not has_cc:
        if income >= 3000000 and credit_score >= 750:
            score = 96 if upi > 20000 else 93
            scored_products.append({
                "product": "Infinia Credit Card",
                "category": "credit_cards",
                "confidence": score,
                "acceptance_probability": min(99, score - 2),
                "reason": f"Elite profile: ₹{income/100000:.1f}L income + {credit_score} credit score. Infinia offers unlimited airport lounge, 10X reward points, dedicated concierge, and metal card. Your UPI spend of ₹{upi:,.0f}/month shows digital-first behavior - Infinia's SmartPay integration maximizes rewards.",
                "benefits": ["Unlimited airport lounge worldwide", "10X reward points on all spends", "Dedicated concierge service", "Metal card with contactless", "Golf program access"],
                "eligibility_status": "eligible",
                "monthly_cost": "₹12,500 annual fee (waived on ₹10L spend)",
                "expected_roi": "Up to 10% value back on travel bookings",
            })
        elif income >= 1200000 and credit_score >= 700:
            score = 97 if married and children > 0 else 94
            reason = f"Premium income ₹{income/100000:.1f}L with {credit_score} credit. "
            if married and children > 0:
                reason += f"Family of {children+2} benefits from Regalia's travel insurance (covers family) and airport lounge access for frequent family trips. "
            if upi > 15000:
                reason += f"Your ₹{upi:,.0f} UPI spending earns 6X reward points. "
            reason += "Regalia Gold is the #1 choice for India's premium segment."
            scored_products.append({
                "product": "Regalia Gold Credit Card",
                "category": "credit_cards",
                "confidence": score,
                "acceptance_probability": min(99, score - 1),
                "reason": reason,
                "benefits": ["Airport lounge access (domestic + international)", "6X reward points on all spends", "Complimentary travel insurance up to ₹1Cr", "Golf program at premium courses", "Buy 1 Get 1 on BookMyShow"],
                "eligibility_status": "eligible",
                "monthly_cost": "₹5,000 annual fee (waived on ₹5L spend)",
                "expected_roi": "Up to 6% value back on regular spends",
            })
        elif income >= 500000 and credit_score >= 700:
            reason = f"Solid income ₹{income/100000:.1f}L. "
            if upi > 10000:
                reason += f"High UPI usage (₹{upi:,.0f}/month) - MoneyBack+ gives 10% cashback on utility bills and 5% on shopping. "
            else:
                reason += "MoneyBack+ gives 10% cashback on utility bills and 5% on shopping - perfect for everyday savings. "
            reason += "No annual fee makes it risk-free to try."
            scored_products.append({
                "product": "MoneyBack+ Credit Card",
                "category": "credit_cards",
                "confidence": 92,
                "acceptance_probability": 90,
                "reason": reason,
                "benefits": ["10% cashback on utility bills", "5% on online shopping", "Fuel surcharge waiver", "No annual fee", "Contactless payments"],
                "eligibility_status": "eligible",
                "monthly_cost": "Free",
                "expected_roi": "Up to 10% cashback on utilities",
            })
        elif income >= 300000 and credit_score >= 650:
            reason = f"₹{income/100000:.1f}L income at age {age}. "
            if age <= 28:
                reason += "Millennia is designed for young professionals like you - 5% cashback on Amazon, Flipkart, and Swiggy. "
            else:
                reason += "Millennia offers the best value with 5% cashback on Amazon, contactless payments, and zero joining fee. "
            reason += "Great first credit card to build your credit history."
            scored_products.append({
                "product": "Millennia Credit Card",
                "category": "credit_cards",
                "confidence": 88,
                "acceptance_probability": 91,
                "reason": reason,
                "benefits": ["5% cashback on Amazon/Flipkart", "1% on all other spends", "Contactless technology", "Zero joining fee", "Fuel surcharge waiver"],
                "eligibility_status": "eligible",
                "monthly_cost": "₹1,000 annual fee (waived on ₹1L spend)",
                "expected_roi": "Up to 5% cashback on online shopping",
            })

    # ─── HEALTH INSURANCE ───
    has_health = any(i in existing_text for i in ["health", "medical", "health insurance"])
    if not has_health:
        family_factors = []
        if married: family_factors.append("married")
        if children > 0: family_factors.append(f"{children} children")
        if dependent_parents: family_factors.append("dependent parents")
        if parents_senior: family_factors.append("senior citizen parents")

        if family_factors:
            coverage = "₹10-15L" if income < 1000000 else "₹15-25L" if income < 2000000 else "₹25-50L"
            reason = f"CRITICAL GAP: No health insurance for a family ({', '.join(family_factors)}). "
            reason += f"Recommended cover: {coverage} for family of {children+2 if children else 2}. "
            if parents_senior:
                reason += "Senior citizen parents need separate top-up. "
            reason += "Cashless treatment at 13,000+ hospitals. One hospitalization can wipe out savings."
            scored_products.append({
                "product": "HDFC Health Insurance",
                "category": "insurance",
                "confidence": 96,
                "acceptance_probability": 93,
                "reason": reason,
                "benefits": [f"Coverage up to {coverage}", "Cashless treatment at 13,000+ hospitals", "No claim bonus up to 50%", "Pre & post hospitalization covered", "Day care procedures included", "Restoration of sum insured"],
                "eligibility_status": "eligible",
                "monthly_cost": f"₹{max(500, income // 10000)}/month for family",
                "expected_roi": "Protection against ₹5-50L hospital bills",
            })
        elif income >= 500000:
            reason = f"No health insurance despite ₹{income/100000:.1f}L income. "
            if age > 35:
                reason += f"At age {age}, premiums increase 10% every year. Lock in lower rate now. "
            reason += "Even a minor surgery costs ₹2-3L. Health insurance is non-negotiable."
            scored_products.append({
                "product": "HDFC Health Insurance",
                "category": "insurance",
                "confidence": 89,
                "acceptance_probability": 86,
                "reason": reason,
                "benefits": ["Cashless treatment at 13,000+ hospitals", "No claim bonus", "Pre/post hospitalization", "Day care procedures"],
                "eligibility_status": "eligible",
                "monthly_cost": f"₹{max(400, income // 12000)}/month",
                "expected_roi": "Protection against unexpected medical bills",
            })

    # ─── TERM INSURANCE ───
    has_term = any(i in existing_text for i in ["term", "life insurance", "term insurance"])
    if not has_term and income >= 500000 and (married or children > 0 or age > 25):
        cover = income * 10  # 10x annual income
        reason = f"₹{income/100000:.1f}L income earner with "
        dependents = []
        if married: dependents.append("spouse")
        if children > 0: dependents.append(f"{children} children")
        if dependent_parents: dependents.append("parents")
        reason += ", ".join(dependents) if dependents else "future financial obligations"
        reason += f" needs ₹{cover/100000:.0f}L life cover (10x income). "
        if age < 30:
            reason += f"At age {age}, term insurance costs just ₹500-800/month for ₹1Cr cover. "
        elif age < 40:
            reason += f"At age {age}, term insurance costs ₹800-1500/month for ₹1Cr cover. "
        else:
            reason += f"At age {age}, term insurance costs ₹1500-3000/month. Don't delay - premiums increase with age. "
        reason += "HDFC Term Insurance covers death, terminal illness, and accidental disability."
        scored_products.append({
            "product": "HDFC Term Insurance",
            "category": "insurance",
            "confidence": 94,
            "acceptance_probability": 91,
            "reason": reason,
            "benefits": [f"₹{cover/100000:.0f}L life cover", "Critical illness rider available", "Accidental death benefit", "Terminal illness benefit", "Tax benefit under 80C & 10(10D)"],
            "eligibility_status": "eligible",
            "monthly_cost": f"₹{max(600, int(income/100000 * 8))}/month",
            "expected_roi": f"₹{cover/100000:.0f}L protection for family",
        })

    # ─── SIP ───
    has_investment = any(i in existing_text for i in ["sip", "mutual fund", "investment", "mutual", "systematic"])
    if not has_investment and surplus > 10000 and credit_score >= 600:
        sip_amount = min(surplus * 0.4, 50000)
        years_to_goal = 10
        future_value = sip_amount * 12 * years_to_goal * 1.12  # rough 12% CAGR
        reason = f"Monthly surplus of ₹{surplus:,.0f} identified. "
        if sip_amount >= 20000:
            reason += f"₹{sip_amount:,.0f}/month SIP can grow to ~₹{future_value/100000:.0f}L in {years_to_goal} years at 12% returns. "
        else:
            reason += f"₹{sip_amount:,.0f}/month SIP can grow to ~₹{future_value/100000:.0f}L in {years_to_goal} years. "
        if family_goals:
            reason += f"Aligns with your goal: {data.get('family_goals', '')}. "
        reason += "Start with HDFC Flexi Cap or HDFC Mid-Cap fund for best long-term growth."
        scored_products.append({
            "product": "Systematic Investment Plan (SIP)",
            "category": "investments",
            "confidence": 91,
            "acceptance_probability": 89,
            "reason": reason,
            "benefits": [f"Potential ₹{future_value/100000:.0f}L in {years_to_goal} years", "Rupee cost averaging reduces risk", "Start with just ₹500/month", "Tax benefits under 80C (ELSS)", "Goal-based investing for children's education/marriage"],
            "eligibility_status": "eligible",
            "monthly_cost": f"₹{sip_amount:,.0f}/month",
            "expected_roi": f"~12-15% annualized (historical)",
        })

    # ─── FIXED DEPOSIT ───
    has_fd = any(i in existing_text for i in ["fd", "fixed deposit"])
    if not has_fd:
        idle = balance - (monthly_expenses * 3)  # keep 3 months expenses as emergency
        if idle > 200000:
            reason = f"Current balance ₹{balance/100000:.1f}L with ₹{idle/100000:.1f}L idle funds. "
            if age >= 60:
                reason += "Senior citizen FD offers extra 0.5% interest. "
            reason += f"₹{idle/100000:.1f}L FD at 6.5% earns ₹{idle*0.065/100000:.2f}L/year guaranteed. Loan available against FD if needed."
            scored_products.append({
                "product": "Fixed Deposit",
                "category": "investments",
                "confidence": 88,
                "acceptance_probability": 94,
                "reason": reason,
                "benefits": ["Guaranteed 6.5-7.25% returns", "Senior citizen gets extra 0.5%", "Loan up to 90% against FD", "Auto-renewal option", "Tax saving FD for 80C"],
                "eligibility_status": "eligible",
                "monthly_cost": f"One-time ₹{idle/100000:.1f}L",
                "expected_roi": "6.5-7.25% guaranteed",
            })

    # ─── HOME LOAN ───
    has_home = any(i in existing_text for i in ["home loan", "housing"])
    if not has_home and income >= 750000 and 25 <= age <= 50:
        eligibility = min(income * 60, 15000000)  # 60x monthly income, max 1.5Cr
        reason = f"Age {age} with ₹{income/100000:.1f}L income is ideal for home loan. "
        if married and children > 0:
            reason += f"Owning a home secures your family's future. "
        reason += f"Eligible for up to ₹{eligibility/100000:.0f}L at 8.5% interest. "
        reason += "Interest paid qualifies for ₹2L deduction under Section 24. Home loan is the cheapest loan available."
        scored_products.append({
            "product": "Home Loan",
            "category": "loans",
            "confidence": 86,
            "acceptance_probability": 84,
            "reason": reason,
            "benefits": [f"Eligible up to ₹{eligibility/100000:.0f}L", "Interest rate from 8.5%", "Tax benefit ₹2L/year (Section 24)", "Tax benefit ₹1.5L (Section 80C)", "Balance transfer available", "Top-up loan facility"],
            "eligibility_status": "eligible",
            "monthly_cost": f"~₹{int(eligibility*0.008/12):,}/month EMI",
            "expected_roi": "Property appreciation + tax savings",
        })

    # ─── CAR LOAN ───
    has_car = any(i in existing_text for i in ["car loan", "auto", "vehicle"])
    if not has_car and income >= 600000 and 23 <= age <= 55 and "business" not in occupation:
        max_car = min(income * 4, 2000000)
        reason = f"₹{income/100000:.1f}L income qualifies for up to ₹{max_car/100000:.0f}L car loan. "
        if married and children > 0:
            reason += "A family car provides safety and convenience for your family. "
        reason += "HDFC offers 8.75% interest with quick 3-day approval. Pre-approved offers may be available."
        scored_products.append({
            "product": "Car Loan",
            "category": "loans",
            "confidence": 81,
            "acceptance_probability": 82,
            "reason": reason,
            "benefits": [f"Up to ₹{max_car/100000:.0f}L financing", "Interest from 8.75%", "Up to 7 years tenure", "Quick 3-day approval", "Zero prepayment penalty"],
            "eligibility_status": "eligible",
            "monthly_cost": f"~₹{int(max_car*0.012):,}/month EMI",
            "expected_roi": "Asset ownership + convenience",
        })

    # ─── BUSINESS LOAN (for self-employed) ───
    has_biz_loan = any(i in existing_text for i in ["business loan", "msme", "working capital"])
    if not has_biz_loan and ("business" in occupation or "self" in occupation or "entrepreneur" in occupation) and income >= 1000000:
        max_loan = min(income * 3, 5000000)
        reason = f"Business owner with ₹{income/100000:.1f}L income. "
        if data.get("gst_registered"):
            reason += "GST-registered businesses get higher loan eligibility. "
        reason += f"Business loan up to ₹{max_loan/100000:.0f}L for expansion, working capital, or new equipment."
        scored_products.append({
            "product": "Business Loan",
            "category": "loans",
            "confidence": 85,
            "acceptance_probability": 83,
            "reason": reason,
            "benefits": [f"Up to ₹{max_loan/100000:.0f}L loan", "Competitive interest rates", "Flexible repayment up to 5 years", "Minimal documentation for existing customers", "Working capital OD facility"],
            "eligibility_status": "eligible",
            "monthly_cost": f"~₹{int(max_loan*0.015):,}/month",
            "expected_roi": "Business growth + revenue expansion",
        })

    # ─── EDUCATION LOAN ───
    has_edu = any(i in existing_text for i in ["education loan"])
    child_ages = [child1_age, child2_age]
    approaching_college = [a for a in child_ages if 14 <= a <= 18]
    if not has_edu and approaching_college:
        reason = f"Child aged {approaching_college[0]} will need college funds in {18-approaching_college[0]} years. "
        reason += "Education loan covers tuition + living expenses with moratorium period (no EMI during studies). "
        reason += "Interest paid qualifies for 80E tax deduction (no limit). Start planning now."
        scored_products.append({
            "product": "HDFC Education Loan",
            "category": "loans",
            "confidence": 87,
            "acceptance_probability": 85,
            "reason": reason,
            "benefits": ["Covers tuition + living + travel", "Moratorium period (no EMI during studies)", "Tax benefit under 80E (no limit)", "Loan up to ₹20L for India, ₹1Cr for abroad", "Flexible repayment up to 15 years"],
            "eligibility_status": "eligible",
            "monthly_cost": "EMI starts after course completion",
            "expected_roi": "Child's future career + earning potential",
        })

    # ─── NPS ───
    has_nps = any(i in existing_text for i in ["nps", "pension", "national pension"])
    if not has_nps and income >= 500000 and 25 <= age <= 55:
        reason = f"Additional ₹50,000 tax deduction under 80CCD(1B) - on top of 80C. "
        if age >= 35:
            reason += f"At age {age}, retirement planning becomes critical. "
        reason += f"₹5,000/month NPS can build ₹1-2Cr corpus by retirement. Low-cost, government-regulated, market-linked returns."
        scored_products.append({
            "product": "NPS (National Pension System)",
            "category": "investments",
            "confidence": 82,
            "acceptance_probability": 80,
            "reason": reason,
            "benefits": ["Extra ₹50,000 tax deduction (80CCD(1B))", "Lowest fund management fee (0.01%)", "Market-linked 10-12% returns", "Additional 80C benefit up to ₹1.5L", "Annuity options for guaranteed pension"],
            "eligibility_status": "eligible",
            "monthly_cost": "₹5,000-10,000/month",
            "expected_roi": "10-12% annualized (long-term)",
        })

    # ─── FASTag ───
    has_fastag = "fastag" in existing_text
    if not has_fastag:
        scored_products.append({
            "product": "FASTag",
            "category": "digital",
            "confidence": 85,
            "acceptance_probability": 93,
            "reason": "FASTag is mandatory for all vehicles in India. Enables cashless toll payments, fuel purchases, and parking. Recharge online instantly. Avoids ₹2x toll penalty at plazas.",
            "benefits": ["Mandatory - avoid penalties", "Cashless toll payments", "Fuel payment at select pumps", "Online recharge via PayZapp/UPI", "Travel history tracking"],
            "eligibility_status": "eligible",
            "monthly_cost": "₹200 one-time + recharge as needed",
            "expected_roi": "Avoid ₹2x toll penalties",
        })

    # ─── DEMAT ACCOUNT ───
    has_demat = any(i in existing_text for i in ["demat", "trading", "stock"])
    if not has_demat and income >= 500000 and risk in ["aggressive", "moderate"] and age <= 50:
        reason = f"₹{income/100000:.1f}L income with {risk} risk appetite. "
        if risk == "aggressive":
            reason += "Demat account gives access to direct equity, IPOs, and ETFs for potentially higher returns than FDs. "
        else:
            reason += "Demat account allows diversified investing across equity, bonds, and gold ETFs. "
        reason += "Free account opening, zero maintenance for 1 year."
        scored_products.append({
            "product": "Demat Account",
            "category": "investments",
            "confidence": 78,
            "acceptance_probability": 76,
            "reason": reason,
            "benefits": ["Direct equity investing", "IPO access (apply from app)", "ETFs and bonds", "Free account opening", "Integrated with NetBanking"],
            "eligibility_status": "eligible",
            "monthly_cost": "Free for 1st year",
            "expected_roi": "Market-linked (12-15% historical equity average)",
        })

    # ─── TRAVEL INSURANCE ───
    has_travel = any(i in existing_text for i in ["travel insurance"])
    if not has_travel and income >= 1000000 and not has_travel:
        reason = f"High-income profile (₹{income/100000:.1f}L) likely travels frequently. "
        if city in ["mumbai", "delhi", "bangalore", "hyderabad", "pune", "chennai"]:
            reason += f"Based in {city.title()} - frequent domestic/international travel expected. "
        reason += "Travel insurance covers trip cancellation, medical emergency abroad, baggage loss, and flight delay. Costs just ₹500-1000 per trip."
        scored_products.append({
            "product": "HDFC Travel Insurance",
            "category": "insurance",
            "confidence": 75,
            "acceptance_probability": 73,
            "reason": reason,
            "benefits": ["Trip cancellation coverage", "Medical emergency up to $50,000", "Baggage loss protection", "Flight delay compensation", "Emergency evacuation"],
            "eligibility_status": "eligible",
            "monthly_cost": "₹500-1,500 per trip",
            "expected_roi": "Protection against ₹5-50L medical bills abroad",
        })

    # ─── SCORE & RANK ───
    scored_products.sort(key=lambda x: x["confidence"], reverse=True)
    top_3 = scored_products[:3]

    # Generate insights
    has_protection = has_health or has_term
    has_invest = has_investment or has_fd or has_nps
    has_credit = has_cc

    needs = []
    if not has_credit: needs.append("Credit Building")
    if not has_protection: needs.append("Family Protection")
    if not has_invest: needs.append("Wealth Creation")
    if children > 0 and not has_edu: needs.append("Education Planning")
    if "home" in family_goals and not has_home: needs.append("Home Ownership")
    if "retirement" in family_goals and not has_nps: needs.append("Retirement Planning")
    if not needs: needs.append("Portfolio Optimization")

    protection_gap = "No health or life insurance" if not has_protection else ("No life insurance" if not has_term else "No health insurance" if not has_health else "Adequately covered")
    investment_gap = "No SIP or investment products" if not has_investment and not has_fd else "Consider diversifying investments"
    credit_gap = "No credit card" if not has_cc else "Good credit product mix"

    return {
        "recommendations": top_3,
        "customer_insights": {
            "life_stage": _get_life_stage(age, married, children),
            "financial_health": _get_financial_health(income, credit_score, surplus),
            "key_needs": needs,
            "protection_gap": protection_gap,
            "investment_gap": investment_gap,
            "credit_gap": credit_gap,
        },
    }


def _get_life_stage(age, married, children):
    if age < 25:
        return "Young Professional - Early career, building foundation"
    elif 25 <= age <= 35 and married and children == 0:
        return "Newly Married - Family planning phase"
    elif married and children > 0 and age <= 45:
        return "Family Builder - Peak earning, children's education"
    elif age > 45 and age <= 55:
        return "Pre-Retirement - Wealth preservation, retirement planning"
    elif age > 55:
        return "Retirement Phase - Income protection, health focus"
    elif not married and age > 30:
        return "Single Professional - Personal wealth building"
    return "Established Professional"


def _get_financial_health(income, credit_score, surplus):
    if income >= 2000000 and credit_score >= 750 and surplus > 30000:
        return "Excellent - High income, strong credit, healthy surplus"
    elif income >= 1000000 and credit_score >= 700 and surplus > 15000:
        return "Good - Stable income, decent credit, positive cash flow"
    elif income >= 500000 and credit_score >= 650:
        return "Average - Building wealth, room for optimization"
    return "Needs Attention - Focus on income growth and credit improvement"
