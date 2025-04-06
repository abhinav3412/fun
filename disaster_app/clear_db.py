from disaster_app import create_app, db
from disaster_app.models import (
    User, Camp, Warehouse, Sensor, Request, 
    UserRequest, CampNotification, Volunteer,
    Donation, DonationAmount, Vehicle, ResourceRequest,
    UserActivity
)

def clear_db():
    app = create_app()
    with app.app_context():
        try:
            # Drop all tables
            db.drop_all()
            print("All tables dropped successfully!")
            
            # Recreate all tables
            db.create_all()
            print("Database tables recreated successfully!")
            
        except Exception as e:
            print(f"Error clearing database: {str(e)}")
            db.session.rollback()
        finally:
            db.session.close()

if __name__ == '__main__':
    clear_db() 