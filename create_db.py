from flask import Flask
from models import db, User, Service, ServiceRequest
from werkzeug.security import generate_password_hash

# Create and configure the app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///household_services.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

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
            password='admin',
            role='admin',
            full_name='Admin User',
        )
        admin.set_password(admin.password)
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
    create_db()  # Create the tables first
    seed_data()  # Then seed the data