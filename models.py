from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    pin_code = db.Column(db.String(10))
    phone_number = db.Column(db.String(15))  # Added phone number
    experience = db.Column(db.Integer)
    service_type = db.Column(db.String(100))
    is_approved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)  # For blocking user
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    profile_image = db.Column(db.String(200))  # For storing profile image path
    document_verified = db.Column(db.Boolean, default=False)  # For professional verification
    avg_rating = db.Column(db.Float, default=0.0)  # Average rating for professionals
    
    service_request = db.relationship('ServiceRequest', backref='customer', foreign_keys='ServiceRequest.customer_id', cascade="all, delete-orphan")
    reviews = db.relationship('Review', backref='customer', foreign_keys='Review.customer_id', cascade="all, delete-orphan")


    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # Additional methods
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name,
            'is_approved': self.is_approved,
            'avg_rating': self.avg_rating
        }

class Service(db.Model):
    __tablename__ = 'service'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    time_required = db.Column(db.String(50))
    category = db.Column(db.String(50))
    image_url = db.Column(db.String(200))  # For service images
    is_active = db.Column(db.Boolean, default=True)  # To temporarily disable services
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    min_experience_required = db.Column(db.Integer, default=0)
    availability = db.Column(db.String(50), default='24/7')

class ServiceRequest(db.Model):
    __tablename__ = 'service_request'
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    preferred_time = db.Column(db.DateTime)  # Added preferred time slot
    date_of_completion = db.Column(db.DateTime)
    service_status = db.Column(db.String(20), default='requested')  # requested/assigned/in_progress/completed/cancelled
    remarks = db.Column(db.Text)
    rating = db.Column(db.Integer)
    review_text = db.Column(db.Text)  # Added detailed review
    payment_status = db.Column(db.String(20), default='pending')  # pending/completed
    total_amount = db.Column(db.Float)
    location_pin = db.Column(db.String(10))  # For location-based assignment

    reviews = db.relationship('Review', backref='service_request', cascade="all, delete-orphan")
    transactions = db.relationship('Transaction', backref='service_request', cascade="all, delete-orphan")

# Additional Models you might want to add:

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    professional_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rating = db.Column(db.Integer)
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50))  # E.g., credit card, cash
    payment_status = db.Column(db.String(20), default='completed')  # completed/failed/pending



class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)