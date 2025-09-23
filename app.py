import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm, CSRFProtect
from flask_wtf.csrf import CSRFError
from wtforms import StringField, TextAreaField, SelectField, DecimalField, DateTimeField, PasswordField, EmailField, IntegerField
from wtforms.validators import DataRequired, Email, Length, NumberRange
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Numeric
from sqlalchemy.exc import IntegrityError
from functools import wraps
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET')
if not app.secret_key:
    raise ValueError("SESSION_SECRET environment variable is required")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Security configurations
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS in production

# Add ProxyFix for Replit environment
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize extensions
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore

# Set up Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# CSRF error handler
@app.errorhandler(CSRFError)
def csrf_error(error):
    flash('The form submission was invalid. Please try again.', 'error')
    return redirect(url_for('index'))

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Role-based access control decorators
def require_role(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role != role and current_user.role != 'admin':
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), default='user')  # user, club_manager, admin
    bio = db.Column(db.Text)
    city = db.Column(db.String(100))
    interests = db.Column(db.Text)  # JSON string of interests
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    managed_clubs = db.relationship('Club', backref='manager', lazy=True)
    created_events = db.relationship('Event', backref='creator', lazy=True)
    event_registrations = db.relationship('EventRegistration', backref='user', lazy=True)
    club_memberships = db.relationship('ClubMembership', backref='user', lazy=True)

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    events = db.relationship('Event', backref='club', lazy=True)
    memberships = db.relationship('ClubMembership', backref='club', lazy=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    price = db.Column(Numeric(10, 2), default=0.00)
    capacity = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(200))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    registrations = db.relationship('EventRegistration', backref='event', lazy=True)
    
    @property
    def available_spots(self):
        registered = EventRegistration.query.filter_by(event_id=self.id).count()
        return self.capacity - registered

class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, refunded
    stripe_payment_id = db.Column(db.String(100))
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one registration per user per event
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_user_event'),)

class ClubMembership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one membership per user per club
    __table_args__ = (db.UniqueConstraint('user_id', 'club_id', name='unique_user_club'),)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Forms
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=100)])

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=20)])
    category = SelectField('Category', choices=[
        ('sustainable', 'Sustainable Living'),
        ('cultural', 'Cultural Experiences'),
        ('entertainment', 'Entertainment & Networking')
    ], validators=[DataRequired()])
    date_time = DateTimeField('Date & Time', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(min=5, max=200)])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=100)])
    price = DecimalField('Price ($)', validators=[NumberRange(min=0, max=1000)])
    capacity = IntegerField('Capacity', validators=[DataRequired(), NumberRange(min=1, max=10000)])

class ClubForm(FlaskForm):
    name = StringField('Club Name', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=20)])
    category = SelectField('Category', choices=[
        ('sustainable', 'Sustainable Living'),
        ('cultural', 'Cultural Experiences'),
        ('entertainment', 'Entertainment & Networking')
    ], validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=100)])

# Simple CSRF-protected forms for POST actions
class EventRegistrationForm(FlaskForm):
    pass  # Only needs CSRF token

class ClubJoinForm(FlaskForm):
    pass  # Only needs CSRF token

class ContactForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=1000)])

# Routes
@app.route('/')
def index():
    # Get data for all sections of the landing page
    recent_events = Event.query.filter(Event.date_time > datetime.now()).order_by(Event.date_time.asc()).limit(6).all()
    featured_clubs = Club.query.order_by(Club.created_at.desc()).limit(6).all()
    
    # Calculate statistics for the footprint section
    stats = {
        'total_events': Event.query.count(),
        'total_clubs': Club.query.count(),
        'total_cities': db.session.query(Event.city).distinct().count(),
        'total_members': User.query.count()
    }
    
    # Team members data
    team_members = [
        {
            'name': 'Sarah Chen',
            'role': 'Founder & Cultural Director',
            'image': 'team-sarah.jpg',
            'bio': 'Cultural heritage preservation expert with 15 years of experience in Morocco'
        },
        {
            'name': 'Ahmed Ben Ali',
            'role': 'Community Manager',
            'image': 'team-ahmed.jpg',
            'bio': 'Local community liaison and traditional crafts specialist'
        },
        {
            'name': 'Emily Rodriguez',
            'role': 'Experience Curator',
            'image': 'team-emily.jpg',
            'bio': 'Travel experience designer focused on authentic cultural immersion'
        },
        {
            'name': 'Omar Fassi',
            'role': 'Heritage Guide',
            'image': 'team-omar.jpg',
            'bio': 'Certified cultural guide and storyteller from Fes medina'
        }
    ]
    
    # Testimonials data
    testimonials = [
        {
            'name': 'Amira Hassan',
            'role': 'Cultural Arts Enthusiast',
            'content': 'Learning traditional pottery from a master craftsman in Fes was transformative. The connection to centuries-old traditions gave me a profound appreciation for Moroccan artistry.',
            'rating': 5
        },
        {
            'name': 'Carlos Rodriguez',
            'role': 'Culinary Explorer',
            'content': 'The traditional cooking class opened my eyes to the rich history behind every spice and technique. Now I can recreate authentic Moroccan flavors at home.',
            'rating': 5
        },
        {
            'name': 'Fatima Al-Zahra',
            'role': 'Heritage Preservationist',
            'content': 'Joining the community has connected me with like-minded individuals who share my passion for preserving Morocco\'s cultural legacy for future generations.',
            'rating': 5
        }
    ]
    
    # Contact form
    contact_form = ContactForm()
    
    return render_template('index.html', 
                         events=recent_events, 
                         clubs=featured_clubs,
                         stats=stats,
                         team_members=team_members,
                         testimonials=testimonials,
                         contact_form=contact_form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please login instead.', 'error')
            return redirect(url_for('login'))
        
        # Create new user
        user = User()
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.city = form.city.data
        password = form.password.data
        if password:
            user.password_hash = generate_password_hash(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Registration successful! Welcome to Moroccan Journey!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('auth/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        password = form.password.data
        if user and user.password_hash and password and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's upcoming events
    upcoming_events = db.session.query(Event).join(EventRegistration).filter(
        EventRegistration.user_id == current_user.id,
        Event.date_time > datetime.now()
    ).order_by(Event.date_time.asc()).all()
    
    # Get user's clubs
    user_clubs = db.session.query(Club).join(ClubMembership).filter(
        ClubMembership.user_id == current_user.id
    ).all()
    
    return render_template('dashboard.html', 
                         upcoming_events=upcoming_events, 
                         user_clubs=user_clubs)

@app.route('/events')
def events():
    # Get filter parameters
    category = request.args.get('category', '')
    city = request.args.get('city', '')
    
    # Build query
    query = Event.query.filter(Event.date_time > datetime.now())
    
    if category:
        query = query.filter(Event.category == category)
    if city:
        query = query.filter(Event.city.ilike(f'%{city}%'))
    
    events = query.order_by(Event.date_time.asc()).all()
    return render_template('events/list.html', events=events, 
                         selected_category=category, selected_city=city)

@app.route('/events/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    is_registered = False
    if current_user.is_authenticated:
        registration = EventRegistration.query.filter_by(
            user_id=current_user.id, 
            event_id=event_id
        ).first()
        is_registered = registration is not None
    
    registration_form = EventRegistrationForm()
    return render_template('events/detail.html', event=event, is_registered=is_registered, registration_form=registration_form)

@app.route('/events/create', methods=['GET', 'POST'])
@login_required
@require_role('club_manager')
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        event = Event()
        event.title = form.title.data
        event.description = form.description.data
        event.category = form.category.data
        event.date_time = form.date_time.data
        event.location = form.location.data
        event.city = form.city.data
        event.price = form.price.data or 0
        event.capacity = form.capacity.data
        event.creator_id = current_user.id
        db.session.add(event)
        db.session.commit()
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('event_detail', event_id=event.id))
    
    return render_template('events/create.html', form=form)

@app.route('/clubs')
def clubs():
    category = request.args.get('category', '')
    city = request.args.get('city', '')
    
    query = Club.query
    if category:
        query = query.filter(Club.category == category)
    if city:
        query = query.filter(Club.city.ilike(f'%{city}%'))
    
    clubs = query.order_by(Club.created_at.desc()).all()
    return render_template('clubs/list.html', clubs=clubs,
                         selected_category=category, selected_city=city)

@app.route('/clubs/<int:club_id>')
def club_detail(club_id):
    club = Club.query.get_or_404(club_id)
    is_member = False
    if current_user.is_authenticated:
        membership = ClubMembership.query.filter_by(
            user_id=current_user.id,
            club_id=club_id
        ).first()
        is_member = membership is not None
    
    # Get club events
    club_events = Event.query.filter_by(club_id=club_id).filter(
        Event.date_time > datetime.now()
    ).order_by(Event.date_time.asc()).all()
    
    join_form = ClubJoinForm()
    return render_template('clubs/detail.html', club=club, 
                         is_member=is_member, club_events=club_events, join_form=join_form)

@app.route('/clubs/create', methods=['GET', 'POST'])
@login_required
def create_club():
    form = ClubForm()
    if form.validate_on_submit():
        club = Club()
        club.name = form.name.data
        club.description = form.description.data
        club.category = form.category.data
        club.city = form.city.data
        club.manager_id = current_user.id
        db.session.add(club)
        db.session.commit()
        
        # Update user role to club_manager if they're a regular user
        if current_user.role == 'user':
            current_user.role = 'club_manager'
            db.session.add(current_user)
        
        # Auto-join creator as member
        membership = ClubMembership()
        membership.user_id = current_user.id
        membership.club_id = club.id
        db.session.add(membership)
        db.session.commit()
        
        flash('Club created successfully!', 'success')
        return redirect(url_for('club_detail', club_id=club.id))
    
    return render_template('clubs/create.html', form=form)

@app.route('/events/<int:event_id>/register', methods=['POST'])
@login_required
def register_for_event(event_id):
    form = EventRegistrationForm()
    if not form.validate_on_submit():
        flash('Invalid request. Please try again.', 'error')
        return redirect(url_for('event_detail', event_id=event_id))
    try:
        with db.session.begin():
            # Lock the event row to prevent race conditions
            event = Event.query.with_for_update().get(event_id)
            if not event:
                flash('Event not found.', 'error')
                return redirect(url_for('events'))
            
            # Check capacity atomically within the transaction
            current_registrations = EventRegistration.query.filter_by(event_id=event_id).count()
            if current_registrations >= event.capacity:
                flash('Sorry, this event is full.', 'error')
                return redirect(url_for('event_detail', event_id=event_id))
            
            # Create registration
            registration = EventRegistration()
            registration.user_id = current_user.id
            registration.event_id = event_id
            registration.payment_status = 'paid' if event.price == 0 else 'pending'
            db.session.add(registration)
            # Commit happens automatically when exiting the 'with' block
        
        if event.price > 0:
            # TODO: Integrate Stripe checkout here
            flash('Registration pending payment. Payment integration coming soon!', 'info')
        else:
            flash('Successfully registered for the event!', 'success')
    
    except IntegrityError:
        db.session.rollback()
        flash('You are already registered for this event.', 'warning')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred during registration. Please try again.', 'error')
    
    return redirect(url_for('event_detail', event_id=event_id))

@app.route('/clubs/<int:club_id>/join', methods=['POST'])
@login_required
def join_club(club_id):
    form = ClubJoinForm()
    if not form.validate_on_submit():
        flash('Invalid request. Please try again.', 'error')
        return redirect(url_for('club_detail', club_id=club_id))
    
    club = Club.query.get_or_404(club_id)
    
    try:
        # Create membership with database constraint handling
        membership = ClubMembership()
        membership.user_id = current_user.id
        membership.club_id = club_id
        db.session.add(membership)
        db.session.commit()
        
        flash('Successfully joined the club!', 'success')
    
    except IntegrityError:
        db.session.rollback()
        flash('You are already a member of this club.', 'warning')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while joining the club. Please try again.', 'error')
    
    return redirect(url_for('club_detail', club_id=club_id))

@app.route('/contact', methods=['POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        try:
            # Create new contact message
            contact_message = ContactMessage()
            contact_message.name = form.name.data
            contact_message.email = form.email.data
            contact_message.message = form.message.data
            db.session.add(contact_message)
            db.session.commit()
            
            flash('Thank you for your message! We\'ll get back to you soon.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while sending your message. Please try again.', 'error')
    else:
        flash('Please fill out all fields correctly.', 'error')
    
    return redirect(url_for('index') + '#contact')

# Ensure database tables are created (works with both direct run and Gunicorn)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Configure debug mode from environment
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', '').lower() in ('true', '1', 'yes')
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])