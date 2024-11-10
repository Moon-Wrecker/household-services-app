# from flask import Flask
# from models import db, User, Service, ServiceRequest, Review, Notification
# from werkzeug.security import generate_password_hash
# from datetime import datetime, timedelta, timezone
# 
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///household_services.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)
# 
# def seed_data():
#     with app.app_context():
#         # Create admin user
#         admin = User(
#             email='admin@example.com',
#             password='admin',
#             role='admin',
#             full_name='Admin User',
#             is_approved=True,
#             document_verified=True
#         )
#         admin.set_password(admin.password)
#         db.session.add(admin)
# 
#         # Create sample customers
#         customers = [
#             User(
#                 email='customer1@example.com',
#                 password='password',
#                 role='customer',
#                 full_name='John Doe',
#                 address='123 Main St',
#                 pin_code='12345',
#                 phone_number='1234567890',
#                 is_approved=True
#             ),
#             User(
#                 email='customer2@example.com',
#                 password='password',
#                 role='customer',
#                 full_name='Jane Smith',
#                 address='456 Oak St',
#                 pin_code='12346',
#                 phone_number='0987654321',
#                 is_approved=True
#             )
#         ]
#         for customer in customers:
#             customer.set_password(customer.password)
#             db.session.add(customer)
# 
#         # Create sample professionals
#         professionals = [
#             User(
#                 email='plumber@example.com',
#                 password='password',
#                 role='professional',
#                 full_name='Mike Wilson',
#                 service_type='Plumbing',
#                 experience=5,
#                 is_approved=True,
#                 document_verified=True,
#                 avg_rating=4.5
#             ),
#             User(
#                 email='electrician@example.com',
#                 password='password',
#                 role='professional',
#                 full_name='Sarah Johnson',
#                 service_type='Electrical',
#                 experience=3,
#                 is_approved=True,
#                 document_verified=True,
#                 avg_rating=4.0
#             )
#         ]
#         for professional in professionals:
#             professional.set_password(professional.password)
#             db.session.add(professional)
# 
#         # Create services with more details
#         services = [
#             Service(
#                 name='Plumbing',
#                 price=50.00,
#                 description='General plumbing services including repairs and installations',
#                 category='Home Repair',
#                 time_required='2-3 hours',
#                 min_experience_required=2
#             ),
#             Service(
#                 name='Electrical',
#                 price=60.00,
#                 description='Electrical repair and installation services',
#                 category='Home Repair',
#                 time_required='1-4 hours',
#                 min_experience_required=3
#             ),
#             Service(
#                 name='House Cleaning',
#                 price=40.00,
#                 description='Professional house cleaning services',
#                 category='Home Maintenance',
#                 time_required='2-4 hours',
#                 min_experience_required=1
#             )
#         ]
#         db.session.add_all(services)
# 
#         # Create sample service requests
#         service_requests = [
#             ServiceRequest(
#                 service_id=1,
#                 customer_id=2,
#                 professional_id=3,
#                 date_of_request=datetime.now(timezone.utc),
#                 preferred_time=datetime.now(timezone.utc) + timedelta(days=1),
#                 service_status='assigned',
#                 location_pin='12345'
#             ),
#             ServiceRequest(
#                 service_id=2,
#                 customer_id=2,
#                 service_status='requested',
#                 location_pin='12346'
#             )
#         ]
#         db.session.add_all(service_requests)
# 
#         # Create sample reviews
#         reviews = [
#             Review(
#                 service_request_id=1,
#                 customer_id=2,
#                 professional_id=3,
#                 rating=4,
#                 review_text="Great service, very professional!"
#             )
#         ]
#         db.session.add_all(reviews)
# 
#         db.session.commit()
#     print("Initial data seeded!")
# 
# if __name__ == '__main__':
#     with app.app_context():
#         db.drop_all()
#         db.create_all()
#         seed_data()




from flask import Flask
from models import db, User, Service, ServiceRequest, Review, Transaction, AuditLog
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///household_services.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def seed_data():
    with app.app_context():
        # Create admin user
        admin = User(
            email='admin@example.com',
            password='admin',
            role='admin',
            full_name='Admin User',
            is_approved=True,
            document_verified=True
        )
        admin.set_password(admin.password)
        db.session.add(admin)

        # Create sample customers
        customers = [
            User(
                email='customer1@example.com',
                password='password',
                role='customer',
                full_name='John Doe',
                address='123 Main St',
                pin_code='12345',
                phone_number='1234567890',
                is_approved=True
            ),
            User(
                email='customer2@example.com',
                password='password',
                role='customer',
                full_name='Jane Smith',
                address='456 Oak St',
                pin_code='12346',
                phone_number='0987654321',
                is_approved=True
            )
        ]
        for customer in customers:
            customer.set_password(customer.password)
            db.session.add(customer)

        # Create sample professionals
        professionals = [
            User(
                email='plumber@example.com',
                password='password',
                role='professional',
                full_name='Mike Wilson',
                service_type='Plumbing',
                experience=5,
                is_approved=True,
                document_verified=True,
                avg_rating=4.5
            ),
            User(
                email='electrician@example.com',
                password='password',
                role='professional',
                full_name='Sarah Johnson',
                service_type='Electrical',
                experience=3,
                is_approved=True,
                document_verified=True,
                avg_rating=4.0
            )
        ]
        for professional in professionals:
            professional.set_password(professional.password)
            db.session.add(professional)

        # Create services with more details
        services = [
            Service(
                name='Plumbing',
                price=50.00,
                description='General plumbing services including repairs and installations',
                category='Home Repair',
                time_required='2-3 hours',
                min_experience_required=2
            ),
            Service(
                name='Electrical',
                price=60.00,
                description='Electrical repair and installation services',
                category='Home Repair',
                time_required='1-4 hours',
                min_experience_required=3
            ),
            Service(
                name='House Cleaning',
                price=40.00,
                description='Professional house cleaning services',
                category='Home Maintenance',
                time_required='2-4 hours',
                min_experience_required=1
            )
        ]
        db.session.add_all(services)

        # Create sample service requests
        service_requests = [
            ServiceRequest(
                service_id=1,
                customer_id=2,
                professional_id=3,
                date_of_request=datetime.now(timezone.utc),
                preferred_time=datetime.now(timezone.utc) + timedelta(days=1),
                service_status='assigned',
                location_pin='12345'
            ),
            ServiceRequest(
                service_id=2,
                customer_id=2,
                service_status='requested',
                location_pin='12346'
            )
        ]
        db.session.add_all(service_requests)

        # Create sample reviews
        reviews = [
            Review(
                service_request_id=1,
                customer_id=2,
                professional_id=3,
                rating=4,
                review_text="Great service, very professional!"
            )
        ]
        db.session.add_all(reviews)

        # Create sample transactions
        transactions = [
            Transaction(
                service_request_id=1,
                amount=50.00,
                payment_method='credit card',
                payment_status='completed'
            )
        ]
        db.session.add_all(transactions)

        # Create sample audit logs
        audit_logs = [
            AuditLog(
                user_id=1,
                action='Created Service Request',
                timestamp=datetime.now(timezone.utc),
                details='Service request created for plumbing service.'
            )
        ]
        db.session.add_all(audit_logs)

        db.session.commit()
    print("Initial data seeded!")

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_data()
