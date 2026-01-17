from app.db.session import engine
from sqlalchemy import text
from app.db.base import Base
# Import models so Base.metadata knows about them
from app.models.service_provider import ServiceProvider, PortfolioProject, WorkExperience, Education, Certification

def update_schema():
    print("Beginning schema update...")
    with engine.connect() as connection:
        # 1. Add columns to ServiceProvider table
        columns_to_add_sp = [
            ("professional_title", "VARCHAR"),
            ("availability", "VARCHAR"),
            ("hourly_rate", "INTEGER"),
            ("skills", "VARCHAR"),
            ("kyc_file", "VARCHAR")
        ]
        
        for col_name, col_type in columns_to_add_sp:
            try:
                print(f"Adding '{col_name}' to 'service_provider'...")
                connection.execute(text(f"ALTER TABLE service_provider ADD COLUMN {col_name} {col_type}"))
                print(f"Success: Added {col_name}")
            except Exception as e:
                print(f"Skipped {col_name} (likely exists): {e}")

        # 2. Add columns to Client table
        columns_to_add_client = [
            ("profile_photo", "VARCHAR"),
            ("location_country", "VARCHAR"),
            ("location_city", "VARCHAR"),
            ("language", "VARCHAR"),
            ("bio", "VARCHAR"),
            ("company_name", "VARCHAR"),
            ("company_size", "VARCHAR"),
            ("industry", "VARCHAR"),
            ("website", "VARCHAR"),
            ("preferred_contact_method", "VARCHAR"),
            ("contact_email", "VARCHAR"),
            ("contact_phone", "VARCHAR"),
            ("timezone", "VARCHAR"),
            ("notes", "VARCHAR"),
            ("billing_name", "VARCHAR"),
            ("tax_gst_number", "VARCHAR"),
            ("billing_contact_email", "VARCHAR"),
            ("billing_contact_phone", "VARCHAR"),
            ("billing_address", "VARCHAR")
        ]

        for col_name, col_type in columns_to_add_client:
            try:
                print(f"Adding '{col_name}' to 'client'...")
                connection.execute(text(f"ALTER TABLE client ADD COLUMN {col_name} {col_type}"))
                print(f"Success: Added {col_name}")
            except Exception as e:
                print(f"Skipped {col_name}: {e}") # Simpler logging

    # 3. Create new tables if they don't exist
    print("Creating new tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Success: Tables created (if not existed).")
    except Exception as e:
        print(f"Error creating tables: {e}")


if __name__ == "__main__":
    update_schema()

