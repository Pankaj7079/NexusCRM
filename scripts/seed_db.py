"""Database Seeder Script using Faker."""

import asyncio
import random
from faker import Faker

from nexuscrm.core.db import engine, Base, AsyncSessionLocal
from nexuscrm.core.security import get_password_hash
from nexuscrm.models.user import User, UserRole
from nexuscrm.models.company import Company
from nexuscrm.models.contact import Contact, LeadStatus
from nexuscrm.models.deal import Deal, DealStage
from nexuscrm.models.activity import Activity, ActivityType

fake = Faker()


async def seed_database():
    """Seed initial sample data into the database."""
    print("Creating database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Create Default Admin & Sales User
        print("Seeding default users...")
        admin = User(
            email="admin@nexuscrm.io",
            hashed_password=get_password_hash("admin123"),
            full_name="System Admin",
            role=UserRole.ADMIN,
        )
        sales_rep = User(
            email="rep@nexuscrm.io",
            hashed_password=get_password_hash("rep123"),
            full_name="Alex Sales",
            role=UserRole.SALES_REP,
        )
        session.add_all([admin, sales_rep])
        await session.commit()

        # 2. Seed Companies
        print("Seeding 10 companies...")
        companies = []
        industries = ["Technology", "Healthcare", "Finance", "Manufacturing", "Retail", "Education"]
        for _ in range(10):
            c = Company(
                name=fake.company(),
                domain=fake.domain_name(),
                industry=random.choice(industries),
                employee_count=random.randint(10, 5000),
                annual_revenue=round(random.uniform(100000, 50000000), 2),
                city=fake.city(),
                country=fake.country(),
            )
            companies.append(c)
        session.add_all(companies)
        await session.commit()

        # Refresh to get IDs
        for c in companies:
            await session.refresh(c)

        # 3. Seed Contacts
        print("Seeding 30 contacts...")
        contacts = []
        statuses = list(LeadStatus)
        for i in range(30):
            comp = random.choice(companies) if random.random() > 0.2 else None
            cnt = Contact(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.unique.email(),
                phone=fake.phone_number(),
                job_title=fake.job(),
                lead_status=random.choice(statuses),
                lead_score=round(random.uniform(10, 95), 1),
                churn_risk=round(random.uniform(0.05, 0.85), 2),
                company_id=comp.id if comp else None,
            )
            contacts.append(cnt)
        session.add_all(contacts)
        await session.commit()

        for cnt in contacts:
            await session.refresh(cnt)

        # 4. Seed Deals
        print("Seeding 20 deals...")
        deals = []
        stages = list(DealStage)
        for cnt in contacts:
            if random.random() > 0.4:
                d = Deal(
                    title=f"{cnt.first_name} - {fake.catch_phrase()} Opportunity",
                    value=round(random.uniform(5000, 150000), 2),
                    stage=random.choice(stages),
                    win_probability=round(random.uniform(0.1, 0.9), 2),
                    expected_close_date=fake.future_datetime(),
                    contact_id=cnt.id,
                    company_id=cnt.company_id,
                )
                deals.append(d)
        session.add_all(deals)
        await session.commit()

        for d in deals:
            await session.refresh(d)

        # 5. Seed Activities
        print("Seeding 50 customer activities...")
        activities = []
        act_types = list(ActivityType)
        for _ in range(50):
            cnt = random.choice(contacts)
            deal = random.choice(deals) if (deals and random.random() > 0.5) else None
            act = Activity(
                type=random.choice(act_types),
                subject=fake.sentence(nb_words=6),
                content=fake.paragraph(nb_sentences=3),
                sentiment_score=round(random.uniform(-0.8, 0.9), 2),
                contact_id=cnt.id,
                deal_id=deal.id if deal else None,
            )
            activities.append(act)
        session.add_all(activities)
        await session.commit()

        print("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
