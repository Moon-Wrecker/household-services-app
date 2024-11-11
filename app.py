from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from models import db, User, Service, ServiceRequest, Review
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///household_services.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    #return User.query.get(int(user_id))
    return db.session.get(User, int(user_id))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form['role']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        if role == 'professional':
            service_type = request.form['service_type']
            experience = request.form['experience']
            user = User(email=email, role=role, full_name=full_name, service_type=service_type, experience=experience)
        else:
            user = User(email=email, role=role, full_name=full_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

from sqlalchemy.orm import aliased

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        user_count = User.query.count()
        professional_count = User.query.filter_by(role='professional').count()
        customer_count = user_count - professional_count - 1
        service_count = Service.query.count()
        service_request_count = ServiceRequest.query.count()
        users = User.query.all()
        pending_professionals = User.query.filter_by(role='professional').all()
        services = Service.query.all()
        pending_requests= ServiceRequest.query.filter_by(service_status='requested').count()

        customer_alias = aliased(User)
        professional_alias = aliased(User)
    
        # Query with aliases for user joins
        service_requests = (
            db.session.query(ServiceRequest)
            .join(Service, ServiceRequest.service_id == Service.id)
            .join(customer_alias, ServiceRequest.customer_id == customer_alias.id)
            .outerjoin(professional_alias, ServiceRequest.professional_id == professional_alias.id)
            .add_columns(Service.name.label('service_name'), 
                         customer_alias.full_name.label('customer_name'),
                         professional_alias.full_name.label('professional_name'))
            .all()
        )
        active_services = ServiceRequest.query.count()
        pending_approvals = User.query.filter_by(document_verified=False).count()
        return render_template('admin_dashboard.html', users=users, services=services, service_requests=service_requests, service=services,
                               total_users=user_count, customer=customer_count, total_services=service_count, total_service_requests=service_request_count, 
                               pending_professionals = pending_professionals, active_services = active_services, pending_approvals=pending_approvals, pending_requests=pending_requests)
    elif current_user.role == 'professional':
        service_requests = ServiceRequest.query.filter_by(professional_id=current_user.id).all()
        return render_template('professional_dashboard.html', service_requests=service_requests)
    else:
        service_requests = ServiceRequest.query.filter_by(customer_id=current_user.id).all()
        return render_template('customer_dashboard.html', service_requests=service_requests)
    
@app.route('/approve_professional/<int:user_id>')
@login_required
def approve_professional():
    pass

@app.route('/services')
def services():
    services = Service.query.all()
    return render_template('services.html', services=services)

from datetime import datetime

@app.route('/service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def service(service_id):
    service = Service.query.get(service_id)
    if request.method == 'POST':
        service_request = ServiceRequest(
            service_id=service.id,
            customer_id=current_user.id,
            preferred_time=datetime.fromisoformat(request.form['preferred_time']),
            location_pin=current_user.pin_code,
            service_status='requested'
        )
        db.session.add(service_request)
        db.session.commit()
        flash('Service request created successfully.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('service.html', service=service)

@app.route('/service-requests')
@login_required
def service_requests():
    if current_user.role == 'admin':
        service_requests = ServiceRequest.query.all()
    elif current_user.role == 'professional':
        service_requests = ServiceRequest.query.filter_by(professional_id=current_user.id).all()
    else:
        service_requests = ServiceRequest.query.filter_by(customer_id=current_user.id).all()
    return render_template('service_requests.html', service_requests=service_requests)

@app.route('/service-request/<int:request_id>', methods=['GET', 'POST'])
@login_required
def service_request(request_id):
    service_request = ServiceRequest.query.get(request_id)
    if current_user.role == 'professional':
        if request.method == 'POST':
            if request.form['action'] == 'accept':
                service_request.professional_id = current_user.id
                service_request.service_status = 'assigned'
                db.session.commit()
                flash('Service request accepted.', 'success')
            elif request.form['action'] == 'reject':
                service_request.service_status = 'requested'
                service_request.professional_id = None
                db.session.commit()
                flash('Service request rejected.', 'success')
            return redirect(url_for('service_requests'))
    elif current_user.role == 'customer':
        if request.method == 'POST':
            if request.form['action'] == 'close':
                service_request.service_status = 'completed'
                service_request.date_of_completion = request.form['date_of_completion']
                service_request.rating = request.form['rating']
                service_request.review_text = request.form['review_text']
                db.session.commit()
                flash('Service request closed.', 'success')
            return redirect(url_for('service_requests'))
    return render_template('service_request.html', service_request=service_request)

@app.route('/admin/users')
@login_required
def admin_users():

    if current_user.role == 'admin':
        if request.method == 'POST':
            action = request.form.get('action')
            
            if action == 'verify':  # Edit an existing service
                user_id = request.form['user_id']
                user = Service.query.get(user_id)
                if user:
                    user.document_verified = True
                    db.session.commit()
                    flash('User Verified Successfully.', 'success')
                else:
                    flash('User Not Found.', 'danger')



    if current_user.role == 'admin':
        users = User.query.all()
        return render_template('admin_users.html', users=users)
    else:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('dashboard'))

# @app.route('/admin/services', methods=['GET', 'POST'])
# @login_required
# def admin_services():
#     if current_user.role == 'admin':
#         if request.method == 'POST':
#             name = request.form['name']
#             price = request.form['price']
#             description = request.form['description']
#             time_required = request.form['time_required']
#             category = request.form['category']
#             service = Service(name=name, price=price, description=description, time_required=time_required, category=category)
#             db.session.add(service)
#             db.session.commit()
#             flash('Service created successfully.', 'success')
#         services = Service.query.all()
#         return render_template('admin_services.html', services=services)
#     else:
#         flash('You are not authorized to access this page.', 'danger')
#         return redirect(url_for('dashboard'))

@app.route('/admin/services', methods=['GET', 'POST'])
@login_required
def admin_services():
    if current_user.role == 'admin':
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'edit':  # Edit an existing service
                service_id = request.form['service_id']
                service = Service.query.get(service_id)
                if service:
                    service.name = request.form['name']
                    service.price = request.form['price']
                    service.description = request.form['description']
                    service.time_required = request.form['time_required']
                    service.category = request.form['category']
                    db.session.commit()
                    flash('Service updated successfully.', 'success')
                else:
                    flash('Service not found.', 'danger')
            
            elif action == 'delete':  # Delete an existing service
                service_id = request.form['service_id']
                service = Service.query.get(service_id)
                if service:
                    db.session.delete(service)
                    db.session.commit()
                    flash('Service deleted successfully.', 'success')
                else:
                    flash('Service not found.', 'danger')
            else:
                  # Add a new service
                name = request.form['name']
                price = request.form['price']
                description = request.form['description']
                time_required = request.form['time_required']
                category = request.form['category']
                service = Service(name=name, price=price, description=description, time_required=time_required, category=category)
                db.session.add(service)
                db.session.commit()
                flash('Service created successfully.', 'success')
        
        # Retrieve all services for display
        services = Service.query.all()
        return render_template('admin_services.html', services=services)
    else:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=1478)