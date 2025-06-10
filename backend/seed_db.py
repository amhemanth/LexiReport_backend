from app.db.session import SessionLocal
from app.db.seed import seed_roles_and_permissions

def main():
    db = SessionLocal()
    try:
        print("Seeding roles and permissions...")
        seed_roles_and_permissions(db)
        print("Seeding completed successfully!")
    except Exception as e:
        print(f"Error during seeding: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 