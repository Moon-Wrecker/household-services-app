from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///household_services.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # Set a strong secret key

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Import models after db is defined
from models import User, Service, ServiceRequest

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        full_name = request.form['full_name']

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, password=hashed_password, role=role, full_name=full_name)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        user = User.query.filter_by(email=email, role=role).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        services = Service.query.all()
        pending_professionals = User.query.filter_by(role='professional', approved=False).all()
        return render_template('admin_dashboard.html', services=services, pending_professionals=pending_professionals)
    elif current_user.role == 'professional':
        service_requests = ServiceRequest.query.filter_by(professional_id=current_user.id).all()
        services = Service.query.all()
        return render_template('professional_dashboard.html', service_requests=service_requests, services=services)
    else:
        service_requests = ServiceRequest.query.filter_by(customer_id=current_user.id).all()
        return render_template('customer_dashboard.html', service_requests=service_requests)

# Service management routes for Admin
@app.route('/create_service', methods=['POST'])
@login_required
def create_service():
    if current_user.role == 'admin':
        name = request.form['service_name']
        price = request.form['price']
        description = request.form['description']
        
        new_service = Service(name=name, price=price, description=description)
        db.session.add(new_service)
        db.session.commit()
        
        flash('Service created successfully!')
        return redirect(url_for('dashboard'))

@app.route('/edit_service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    if current_user.role == 'admin':
        service = Service.query.get_or_404(service_id)
        if request.method == 'POST':
            service.name = request.form['service_name']
            service.price = request.form['price']
            service.description = request.form['description']
            db.session.commit()
            flash('Service updated successfully!')
            return redirect(url_for('dashboard'))
        return render_template('edit_service.html', service=service)

@app.route('/delete_service/<int:service_id>', methods=['POST'])
@login_required
def delete_service(service_id):
    if current_user.role == 'admin':
        service = Service.query.get_or_404(service_id)
        db.session.delete(service)
        db.session.commit()
        flash('Service deleted successfully!')
        return redirect(url_for('dashboard'))

# Professional management routes for Admin
@app.route('/approve_professional/<int:user_id>', methods=['POST'])
@login_required
def approve_professional(user_id):
    if current_user.role == 'admin':
        professional = User.query.get_or_404(user_id)
        professional.approved = True
        db.session.commit()
        flash('Professional approved!')
        return redirect(url_for('dashboard'))

@app.route('/search')
def search():
    return render_template('search.html')  

@app.route('/summary')
def summary():
    return render_template('summary.html') 

@app.route('/reject_professional/<int:user_id>', methods=['POST'])
@login_required
def reject_professional(user_id):
    if current_user.role == 'admin':
        professional = User.query.get_or_404(user_id)
        db.session.delete(professional)
        db.session.commit()
        flash('Professional rejected!')
        return redirect(url_for('dashboard'))

# Customer actions
@app.route('/search_services', methods=['GET'])
@login_required
def search_services():
    search_query = request.args.get('search', '')
    if search_query:
        services = Service.query.filter(Service.name.ilike(f'%{search_query}%')).all()
    else:
        services = Service.query.all()
    return render_template('search_services.html', services=services)

@app.route('/request_service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def request_service(service_id):
    if current_user.role == 'customer':
        service = Service.query.get_or_404(service_id)
        new_request = ServiceRequest(service_id=service_id, customer_id=current_user.id, service_status='requested')
        db.session.add(new_request)
        db.session.commit()
        flash(f'Service {service.name} requested successfully!')
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)