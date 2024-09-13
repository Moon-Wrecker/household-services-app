from app import app, db
from models import User, Service, ServiceRequest
from werkzeug.security import generate_password_hash

def reset_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
    print("Database reset complete!")

def create_db():
    with app.app_context():
        db.create_all()
    print("Database created!")

def seed_data():
    with app.app_context():
        # Create an admin user
        admin = User(
            email='admin@example.com',
            password=generate_password_hash('admin_password', method='pbkdf2:sha256'),
            role='admin',
            full_name='Admin User',
            is_approved=True
        )
        db.session.add(admin)

        # Create some services
        services = [
            Service(name='Plumbing', price=50.00, description='General plumbing services', category='Home Repair'),
            Service(name='Electrical', price=60.00, description='Electrical repair and installation', category='Home Repair'),
            Service(name='Cleaning', price=40.00, description='House cleaning services', category='Home Maintenance')
        ]
        db.session.add_all(services)

        db.session.commit()
    print("Initial data seeded!")

if __name__ == '__main__':
    create_db()  # This will create the tables
    seed_data()  # This will add the initial data