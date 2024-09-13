from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    pin_code = db.Column(db.String(10))
    experience = db.Column(db.Integer)
    service_type = db.Column(db.String(100))
    is_approved = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email}>'

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    time_required = db.Column(db.String(50))
    category = db.Column(db.String(50))

    def __repr__(self):
        return f'<Service {self.name}>'

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    date_of_completion = db.Column(db.DateTime)
    service_status = db.Column(db.String(20), default='requested')
    remarks = db.Column(db.Text)
    rating = db.Column(db.Integer)

    service = db.relationship('Service', backref='requests')
    customer = db.relationship('User', foreign_keys=[customer_id], backref='customer_requests')
    professional = db.relationship('User', foreign_keys=[professional_id], backref='professional_requests')

    def __repr__(self):
        return f'<ServiceRequest {self.id}>'