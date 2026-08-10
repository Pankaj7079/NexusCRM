"""Senior Indian Enterprise CRM Database Seeder Script.

Idempotent, production-grade seeder generating 50 Leading Indian Enterprise Companies,
150+ Executive Contacts with realistic Indian names & matching company domains,
100+ High-Value B2B Enterprise Deals, and 250+ Interaction Activity Logs.
"""

import asyncio
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
from sqlalchemy import select

from nexuscrm.core.db import engine, Base, AsyncSessionLocal
from nexuscrm.core.security import get_password_hash
from nexuscrm.models.user import User, UserRole
from nexuscrm.models.company import Company
from nexuscrm.models.contact import Contact, LeadStatus
from nexuscrm.models.deal import Deal, DealStage
from nexuscrm.models.activity import Activity, ActivityType

fake = Faker('en_IN')
Faker.seed(42)
random.seed(42)

# 50 Leading Indian Enterprise & Tech Companies
INDIAN_COMPANIES = [
    {"name": "Infosys Limited", "domain": "infosys.com", "industry": "IT Services & Consulting", "city": "Bengaluru", "employees": 320000, "revenue": 18200000000.0},
    {"name": "Tata Consultancy Services (TCS)", "domain": "tcs.com", "industry": "IT Services & Consulting", "city": "Mumbai", "employees": 615000, "revenue": 27900000000.0},
    {"name": "Wipro Limited", "domain": "wipro.com", "industry": "IT Services & Consulting", "city": "Bengaluru", "employees": 240000, "revenue": 11200000000.0},
    {"name": "HCLTech", "domain": "hcltech.com", "industry": "Technology Services", "city": "Noida", "employees": 225000, "revenue": 12600000000.0},
    {"name": "Tech Mahindra", "domain": "techmahindra.com", "industry": "Telecom & IT", "city": "Pune", "employees": 145000, "revenue": 6500000000.0},
    {"name": "Reliance Industries", "domain": "ril.com", "industry": "Energy & Digital Services", "city": "Mumbai", "employees": 389000, "revenue": 118000000000.0},
    {"name": "Jio Platforms", "domain": "jio.com", "industry": "Telecommunications & Cloud", "city": "Navi Mumbai", "employees": 75000, "revenue": 14000000000.0},
    {"name": "Razorpay Software", "domain": "razorpay.com", "industry": "Fintech & Payments", "city": "Bengaluru", "employees": 3500, "revenue": 380000000.0},
    {"name": "Zerodha Broking", "domain": "zerodha.com", "industry": "Financial Technology", "city": "Bengaluru", "employees": 1100, "revenue": 820000000.0},
    {"name": "Zomato Limited", "domain": "zomato.com", "industry": "E-Commerce & Food Tech", "city": "Gurugram", "employees": 4800, "revenue": 1400000000.0},
    {"name": "Swiggy (Bundl Technologies)", "domain": "swiggy.in", "industry": "Hyperlocal Delivery", "city": "Bengaluru", "employees": 6000, "revenue": 1100000000.0},
    {"name": "Freshworks India", "domain": "freshworks.com", "industry": "SaaS & Enterprise Software", "city": "Chennai", "employees": 5200, "revenue": 590000000.0},
    {"name": "Zoho Corporation", "domain": "zoho.com", "industry": "Cloud SaaS Software", "city": "Chennai", "employees": 15000, "revenue": 1000000000.0},
    {"name": "Postman Technologies", "domain": "postman.com", "industry": "API Infrastructure SaaS", "city": "Bengaluru", "employees": 1200, "revenue": 180000000.0},
    {"name": "Paytm (One97 Communications)", "domain": "paytm.com", "industry": "Financial Services", "city": "Noida", "employees": 10500, "revenue": 980000000.0},
    {"name": "PhonePe Private Limited", "domain": "phonepe.com", "industry": "Digital Payments & Wealth", "city": "Bengaluru", "employees": 5400, "revenue": 620000000.0},
    {"name": "CRED (Dreamplug Technologies)", "domain": "cred.club", "industry": "Fintech & Credit", "city": "Bengaluru", "employees": 950, "revenue": 210000000.0},
    {"name": "Flipkart Internet", "domain": "flipkart.com", "industry": "E-Commerce Enterprise", "city": "Bengaluru", "employees": 22000, "revenue": 7000000000.0},
    {"name": "Meesho Technologies", "domain": "meesho.com", "industry": "Social E-Commerce", "city": "Bengaluru", "employees": 2100, "revenue": 450000000.0},
    {"name": "InMobi Technologies", "domain": "inmobi.com", "industry": "AdTech & AI Marketing", "city": "Bengaluru", "employees": 2600, "revenue": 520000000.0},
    {"name": "Nykaa (FSN E-Commerce)", "domain": "nykaa.com", "industry": "Beauty & Retail Tech", "city": "Mumbai", "employees": 3400, "revenue": 750000000.0},
    {"name": "OYO Rooms (Oravel Stays)", "domain": "oyorooms.com", "industry": "Hospitality Tech", "city": "Gurugram", "employees": 4200, "revenue": 680000000.0},
    {"name": "Ola Electric Mobility", "domain": "olaelectric.com", "industry": "EV & Automotive Tech", "city": "Bengaluru", "employees": 4900, "revenue": 610000000.0},
    {"name": "Delhivery Limited", "domain": "delhivery.com", "industry": "Logistics & Supply Chain", "city": "Gurugram", "employees": 16500, "revenue": 920000000.0},
    {"name": "Pine Labs", "domain": "pinelabs.com", "industry": "Merchant Commerce", "city": "Noida", "employees": 3200, "revenue": 240000000.0},
    {"name": "Policybazaar (PB Fintech)", "domain": "policybazaar.com", "industry": "Insurtech", "city": "Gurugram", "employees": 12800, "revenue": 410000000.0},
    {"name": "Info Edge (Naukri.com)", "domain": "infoedge.in", "industry": "Internet & HR Tech", "city": "Noida", "employees": 5100, "revenue": 310000000.0},
    {"name": "Persistent Systems", "domain": "persistent.com", "industry": "Digital Engineering", "city": "Pune", "employees": 23000, "revenue": 1180000000.0},
    {"name": "Coforge Limited", "domain": "coforge.com", "industry": "IT Solutions", "city": "Noida", "employees": 24500, "revenue": 1100000000.0},
    {"name": "Mphasis Limited", "domain": "mphasis.com", "industry": "Cloud & Cognitive", "city": "Bengaluru", "employees": 34000, "revenue": 1650000000.0},
    {"name": "L&T Technology Services (LTTS)", "domain": "ltts.com", "industry": "Engineering & R&D", "city": "Vadodara", "employees": 23500, "revenue": 1120000000.0},
    {"name": "Cyient Limited", "domain": "cyient.com", "industry": "Intelligent Engineering", "city": "Hyderabad", "employees": 15000, "revenue": 780000000.0},
    {"name": "Titan Company", "domain": "titan.co.in", "industry": "Consumer Goods & Retail", "city": "Bengaluru", "employees": 8200, "revenue": 5200000000.0},
    {"name": "Tata Motors", "domain": "tatamotors.com", "industry": "Automotive Mobility", "city": "Mumbai", "employees": 81000, "revenue": 53000000000.0},
    {"name": "HDFC Bank", "domain": "hdfcbank.com", "industry": "Banking & Financials", "city": "Mumbai", "employees": 177000, "revenue": 25000000000.0},
    {"name": "ICICI Bank", "domain": "icicibank.com", "industry": "Banking & Financials", "city": "Mumbai", "employees": 130000, "revenue": 21000000000.0},
    {"name": "Axis Bank", "domain": "axisbank.com", "industry": "Banking & Financials", "city": "Mumbai", "employees": 95000, "revenue": 14500000000.0},
    {"name": "Bharti Airtel", "domain": "airtel.in", "industry": "Telecommunications", "city": "New Delhi", "employees": 19500, "revenue": 18000000000.0},
    {"name": "Sun Pharmaceutical", "domain": "sunpharma.com", "industry": "Pharmaceuticals", "city": "Mumbai", "employees": 38000, "revenue": 5400000000.0},
    {"name": "Dr. Reddy's Laboratories", "domain": "drreddys.com", "industry": "Pharmaceuticals", "city": "Hyderabad", "employees": 25000, "revenue": 3100000000.0},
    {"name": "Cipla Limited", "domain": "cipla.com", "industry": "Healthcare & Life Sciences", "city": "Mumbai", "employees": 26000, "revenue": 2800000000.0},
    {"name": "Biocon Limited", "domain": "biocon.com", "industry": "Biotechnology", "city": "Bengaluru", "employees": 13500, "revenue": 1400000000.0},
    {"name": "Mahindra & Mahindra", "domain": "mahindra.com", "industry": "Automotive & Farm", "city": "Mumbai", "employees": 260000, "revenue": 15000000000.0},
    {"name": "Bajaj Finance", "domain": "bajajfinserv.in", "industry": "NBFC & Consumer Lending", "city": "Pune", "employees": 41000, "revenue": 6200000000.0},
    {"name": "Larsen & Toubro (L&T)", "domain": "larsentoubro.com", "industry": "Engineering & Construction", "city": "Mumbai", "employees": 55000, "revenue": 26000000000.0},
    {"name": "Adani Enterprises", "domain": "adani.com", "industry": "Infrastructure & Energy", "city": "Ahmedabad", "employees": 29000, "revenue": 16000000000.0},
    {"name": "Asian Paints", "domain": "asianpaints.com", "industry": "Chemicals & Coatings", "city": "Mumbai", "employees": 8500, "revenue": 4200000000.0},
    {"name": "Godrej Consumer Products", "domain": "godrejcp.com", "industry": "FMCG Consumer Goods", "city": "Mumbai", "employees": 3100, "revenue": 1700000000.0},
    {"name": "Maruti Suzuki India", "domain": "marutisuzuki.com", "industry": "Automotive Manufacturing", "city": "New Delhi", "employees": 17500, "revenue": 14000000000.0},
    {"name": "Havells India", "domain": "havells.com", "industry": "Electrical Equipment", "city": "Noida", "employees": 6800, "revenue": 2200000000.0},
]

INDIAN_FIRST_NAMES = [
    "Pankaj", "Ananya", "Rajesh", "Priya", "Vikram", "Neha", "Arjun", "Kavita",
    "Rohan", "Siddharth", "Meera", "Amitabh", "Deepak", "Sneha", "Aditya", "Pooja",
    "Rahul", "Divya", "Sanjay", "Anushka", "Aarav", "Ritu", "Gaurav", "Simran",
    "Karan", "Tanvi", "Vishal", "Shruti", "Manish", "Preeti", "Nikhil", "Swati",
]

INDIAN_LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Singh", "Kumar", "Gupta", "Reddy", "Iyer",
    "Joshi", "Malhotra", "Nair", "Chawla", "Deshmukh", "Sundaram", "Agarwal", "Rao",
    "Bhatnagar", "Chaudhary", "Kulkarni", "Mehta", "Saxena", "Trivedi", "Menon", "Sen",
]

EXECUTIVE_TITLES = [
    "Chief Technology Officer (CTO)",
    "VP of Enterprise Digital Transformation",
    "Head of Cloud Architecture & DevOps",
    "Director of Global Procurement",
    "VP of Customer Success & Revenue",
    "Chief Information Security Officer (CISO)",
    "Senior Vice President of Engineering",
    "Lead AI Solutions Architect",
    "Head of Strategic Alliances",
]

ACTIVITY_SUBJECTS = [
    "Q3 Enterprise Contract Renewal & Volume Pricing Strategy",
    "Executive Technical Demo: Agentic Harness & MCP Integration",
    "ISO 27001 & SOC2 Type II Security Compliance Audit Review",
    "Deep-Dive Architecture: PageIndex Hybrid RAG Implementation",
    "Support Ticket Escalation: High Concurrency API Latency Triage",
    "Quarterly Business Review (QBR) & Multi-Year Expansion Roadmap",
    "POC Evaluation Sign-Off: Lead Scoring & Churn Risk ML Models",
]


async def seed_database():
    """Seed 50 Indian Enterprise Companies, 150+ Contacts, 100+ Deals, and 250+ Activities."""
    print("Refreshing database schema for Indian Enterprise CRM Dataset...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Seed Default Users
        print("Seeding production admin & sales users...")
        admin = User(
            email="admin@nexuscrm.io",
            hashed_password=get_password_hash("admin123"),
            full_name="Pankaj Kumar (System Admin)",
            role=UserRole.ADMIN,
        )
        sales_rep = User(
            email="rep@nexuscrm.io",
            hashed_password=get_password_hash("rep123"),
            full_name="Alex Sales Rep",
            role=UserRole.SALES_REP,
        )
        session.add_all([admin, sales_rep])
        await session.commit()

        # 2. Seed 50 Indian Companies
        print(f"Seeding {len(INDIAN_COMPANIES)} leading Indian enterprise companies...")
        company_objs = []
        for item in INDIAN_COMPANIES:
            c = Company(
                name=item["name"],
                domain=item["domain"],
                industry=item["industry"],
                employee_count=item["employees"],
                annual_revenue=item["revenue"],
                city=item["city"],
                country="India",
            )
            company_objs.append(c)
        session.add_all(company_objs)
        await session.commit()

        for c in company_objs:
            await session.refresh(c)

        # 3. Seed 150+ Contacts (Realistic Indian Names & Matching Company Domains)
        print("Seeding 150+ Indian executive contacts with company-domain emails...")
        contact_objs = []
        statuses = list(LeadStatus)
        total_contacts = 150

        # Featured Test Contact for Real Email & Agent Testing
        primary_comp = company_objs[0]
        test_cnt = Contact(
            first_name="Pankaj",
            last_name="Singh",
            email="pankajsingh341035@gmail.com",
            phone="+91-9876543210",
            job_title="Head of Enterprise AI & Technology",
            lead_status=LeadStatus.QUALIFIED,
            lead_score=95.0,
            churn_risk=0.75,  # High Churn Risk to test Retain Agent Workflow
            company_id=primary_comp.id,
        )
        contact_objs.append(test_cnt)

        for i in range(1, total_contacts):
            comp = company_objs[i % len(company_objs)]
            first_name = random.choice(INDIAN_FIRST_NAMES)
            last_name = random.choice(INDIAN_LAST_NAMES)
            email = f"{first_name.lower()}.{last_name.lower()}{i+1}@{comp.domain}"

            cnt = Contact(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=f"+91-{random.choice([98, 99, 97, 96, 95])}{random.randint(10000000, 99999999)}",
                job_title=random.choice(EXECUTIVE_TITLES),
                lead_status=statuses[i % len(statuses)],
                lead_score=round(random.uniform(40.0, 99.0), 1),
                churn_risk=round(random.uniform(0.02, 0.70), 2),
                company_id=comp.id,
            )
            contact_objs.append(cnt)
        session.add_all(contact_objs)
        await session.commit()

        for cnt in contact_objs:
            await session.refresh(cnt)

        # 4. Seed 100+ Enterprise B2B Deals
        print("Seeding 100+ high-value B2B enterprise deals...")
        deal_objs = []
        stages = list(DealStage)
        total_deals = 100

        for i in range(total_deals):
            cnt = contact_objs[i % len(contact_objs)]
            comp = next((c for c in company_objs if c.id == cnt.company_id), None)
            deal_name = f"{comp.name if comp else cnt.first_name} - {random.choice(['Global IT Migration', 'AI Agentic Harness Modernization', 'Multi-Year SaaS License', 'Cloud Infrastructure Transformation', 'API Gateway Security SLA'])}"

            d = Deal(
                title=deal_name,
                value=round(random.uniform(50000.0, 850000.0), 2),
                stage=stages[i % len(stages)],
                win_probability=round(random.uniform(0.25, 0.95), 2),
                expected_close_date=datetime.now(timezone.utc) + timedelta(days=random.randint(7, 120)),
                contact_id=cnt.id,
                company_id=cnt.company_id,
            )
            deal_objs.append(d)
        session.add_all(deal_objs)
        await session.commit()

        for d in deal_objs:
            await session.refresh(d)

        # 5. Seed 250+ Interaction Activity Logs
        print("Seeding 250+ customer activity interaction logs...")
        activity_objs = []
        act_types = list(ActivityType)
        total_activities = 250

        for i in range(total_activities):
            cnt = random.choice(contact_objs)
            deal = random.choice(deal_objs) if random.random() > 0.25 else None
            days_ago = random.randint(1, 90)

            act = Activity(
                type=act_types[i % len(act_types)],
                subject=random.choice(ACTIVITY_SUBJECTS),
                content=f"Interaction logged with {cnt.first_name} {cnt.last_name} ({cnt.job_title}). Discussed solution architecture, technical SLA guarantees, and licensing terms.",
                sentiment_score=round(random.uniform(-0.3, 0.95), 2),
                contact_id=cnt.id,
                deal_id=deal.id if deal else None,
                created_at=datetime.now(timezone.utc) - timedelta(days=days_ago),
            )
            activity_objs.append(act)
        session.add_all(activity_objs)
        await session.commit()

        print("\n[SUCCESS] Senior Indian Enterprise Database Seeding Completed!")
        print("------------------------------------------------------------")
        print("Default Admin Login:     admin@nexuscrm.io / admin123")
        print("Default Sales Rep Login:  rep@nexuscrm.io / rep123")
        print("Total Companies (India): 50")
        print("Total Contacts:          150")
        print("Total Deals:             100")
        print("Total Activity Logs:     250")
        print("------------------------------------------------------------")


if __name__ == "__main__":
    asyncio.run(seed_database())
