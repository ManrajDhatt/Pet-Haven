from flask import Flask, abort, jsonify, render_template, redirect, session, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import func
from models import Result, db, User, Event, Registration
from forms import RegistrationForm, LoginForm, EventForm, RegistrationEventForm, ResultForm
from config import Config
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_mail import Message,Mail
from send_email import send_confirmation_email, send_update_email
from dotenv import load_dotenv
import cloudinary.uploader
from flask_migrate import Migrate

from app import db
from models import Registration
from datetime import datetime, timezone


load_dotenv()  # Load environment variables from .env file


app = Flask(__name__)
app.config.from_object(Config)


UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

mail=Mail(app)
migrate = Migrate(app, db)

# Create database tables
with app.app_context():
    # Hardcoded Admin
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD") 
    hashed_pw = bcrypt.generate_password_hash(ADMIN_PASSWORD).decode('utf-8')
    registrations = Registration.query.filter(Registration.timestamp == None).all()

    for reg in registrations:
        reg.timestamp = datetime.now(timezone.utc)

    db.session.commit()
    if not User.query.filter_by(email="admin@example.com").first():
        admin = User(username="admin", email="admin@example.com", password=hashed_pw, is_admin=True)
        db.session.add(admin)
        db.session.commit()




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()  #Check if email exists
        if existing_user:
            flash('Email is already registered. Please log in.', 'danger')
            return redirect(url_for('login'))  # Redirect to login if email exists
        
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)




@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Login failed. Check credentials.', 'danger')
    return render_template('login.html', form=form)



@app.route('/competitions')
@login_required
def competitions():
    today = datetime.today().date()
    upcoming_events = Event.query.filter(Event.date >= today).all()
    if current_user.is_admin:
        return render_template('admin_dashboard.html', events=upcoming_events)
    
    events = Event.query.all()
    registered_events = Registration.query.filter_by(user_id=current_user.id).all()
    
    registered_event_details = []
    for reg in registered_events:
        event = Event.query.get(reg.event_id)
        if event:
            registered_event_details.append(event)

    return render_template('user_dashboard.html', events=upcoming_events, registered_events=registered_event_details)
    # return render_template('user_dashboard.html', events=Event.query.all(), registered_events=registered_events)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("discover[team2].html", events=Event.query.all())


@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    if not current_user.is_admin:
        return redirect(url_for('competitions'))
    form = EventForm()  
    if form.validate_on_submit():
        # image_filename = "default.png"
        image_url="https://res.cloudinary.com/diyvaqnyj/image/upload/v1740916253/default_pgbdyf.png"

        if form.image.data:
            image_filename = secure_filename(form.image.data.filename)
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(form.image.data, folder="event_images")
            image_url = upload_result["secure_url"]  # Get Cloudinary image URL



        new_event = Event(
            title=form.title.data,
            description=form.description.data,
            date=form.date.data,
            location=form.location.data,
            prizes=form.prizes.data,
            eligibility=form.eligibility.data,
            fee=form.fee.data,
            image_filename=image_url 
        )
        db.session.add(new_event)
        db.session.commit()
        flash('Event added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))  #Redirect after adding event
    return render_template('add_event.html', form=form)
    
    

@app.route('/register/<int:event_id>', methods=['GET', 'POST'])
@login_required
def register_event(event_id):
    if current_user.is_admin:  # Prevent admins from registering
        flash('Admins cannot register for events!', 'danger')
        return redirect(url_for('competitions'))
    
    existing_registration = Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if existing_registration:
        flash('You have already registered for this event!', 'warning')
        return redirect(url_for('competitions'))

    event = Event.query.get_or_404(event_id)
    form = RegistrationEventForm()

    if form.validate_on_submit():
        registration = Registration(
            user_id=current_user.id,
            event_id=event_id,
            pet_name=form.pet_name.data,
            pet_type=form.pet_type.data,
            pet_age=form.pet_age.data,
            paid=False  # Assuming payment is done later
        )
        db.session.add(registration)
        db.session.commit()
        send_confirmation_email(current_user.email, current_user.username, event, form.pet_name.data, form.pet_type.data, form.pet_age.data)

        flash('Successfully registered!', 'success')
        return redirect(url_for('competitions'))

    return render_template('register_event.html', form=form, event=event)



@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))  # Restrict non-admin users
    events = Event.query.all()  #  Fetch all events
    return render_template('admin_dashboard.html', events=events)

@app.route('/registrations')
@login_required
def registrations():
    registered_events = db.session.query(Registration, Event).join(Event, Registration.event_id == Event.id).filter(Registration.user_id == current_user.id).all()
    # Convert event dates to datetime objects for comparison
    current_date = datetime.now().date()
    processed_events = []
    for reg, event in registered_events:
        event_date = datetime.strptime(event.date, '%Y-%m-%d').date()
        can_edit = event_date > current_date
        processed_events.append((reg, event, can_edit))
    
    return render_template("registrations.html", registered_events=processed_events)

@app.route('/edit_registration/<int:registration_id>', methods=['GET', 'POST'])
@login_required
def edit_registration(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    event = Event.query.get_or_404(registration.event_id)
    
    # Check if the registration belongs to the current user
    if registration.user_id != current_user.id:
        flash('You are not authorized to edit this registration.', 'danger')
        return redirect(url_for('registrations'))
    
    # Check if the event date has passed
    event_date = datetime.strptime(event.date, '%Y-%m-%d').date()
    if event_date < datetime.now().date():
        flash('Cannot edit registration for past events.', 'warning')
        return redirect(url_for('registrations'))
    
    form = RegistrationEventForm()
    
    if form.validate_on_submit():
        registration.pet_name = form.pet_name.data
        registration.pet_type = form.pet_type.data
        registration.pet_age = form.pet_age.data
        
        try:
            db.session.commit()
            flash('Registration details updated successfully!', 'success')
            return redirect(url_for('registrations'))
        except:
            db.session.rollback()
            flash('An error occurred while updating the registration.', 'danger')
    
    # Pre-fill form with current values
    if request.method == 'GET':
        form.pet_name.data = registration.pet_name
        form.pet_type.data = registration.pet_type
        form.pet_age.data = registration.pet_age
    
    return render_template('edit_registration.html', form=form, registration=registration, event=event)

@app.route('/settings')
@login_required
def settings():
    return render_template("settings.html")


@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    if not current_user.is_admin:
        flash("You are not authorized to edit events.", "danger")
        return redirect(url_for('dashboard'))

    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)  # Pre-fill form with event details

    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.date = form.date.data
        event.location = form.location.data
        event.prizes = form.prizes.data
        event.eligibility = form.eligibility.data
        event.fee = form.fee.data

        # Handle image upload
        if form.image.data:
            image_filename = secure_filename(form.image.data.filename)
            upload_result = cloudinary.uploader.upload(form.image.data, folder="event_images")
            event.image_filename = upload_result["secure_url"]  
        
        try:
            db.session.commit()
            flash("Event updated successfully!", "success")

            # Send notifications if the checkbox is selected
            if 'send_notifications' in request.form:
                registrations = Registration.query.filter_by(event_id=event.id).all()
                for reg in registrations:
                    send_update_email(reg.user.email, reg.user.username, event)

            return redirect(url_for('admin_dashboard'))
        except:
            db.session.rollback()
            flash("Error updating event.", "danger")

    return render_template('edit_event.html', form=form, event=event)

@app.route('/all-registrations')
@login_required
def all_registrations():
    if not current_user.is_admin:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('home'))

    registrations = Registration.query.all()  # Fetch all registrations
    return render_template('all_registrations.html', registrations=registrations)



@app.route('/pay/<int:registration_id>', methods=['GET', 'POST'])
@login_required
def pay_fee(registration_id):
    registration = Registration.query.get_or_404(registration_id)

    if registration.user_id != current_user.id:
        abort(403)  # Prevent unauthorized access

    registration.paid = True
    db.session.commit()

    flash("Payment successful!", "success")
    return redirect(url_for('registrations'))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/verify_payment/<int:registration_id>', methods=['GET', 'POST'])
@login_required
def verify_payment(registration_id):
    if not current_user.is_admin:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('home'))

    registration = Registration.query.get_or_404(registration_id)
    registration.paid = True
    db.session.commit()

    flash("Payment verified successfully!", "success")
    return redirect(url_for('all_registrations'))

@app.route('/delete_registration/<int:registration_id>', methods=['GET', 'POST'])
@login_required
def delete_registration(registration_id):
    if not current_user.is_admin:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('home'))

    registration = Registration.query.get_or_404(registration_id)
    db.session.delete(registration)
    db.session.commit()

    flash("Registration deleted successfully!", "success")
    return redirect(url_for('all_registrations'))




@app.route('/admin/manage_results')
@login_required
def manage_results():
    if not current_user.is_admin:
        flash("Access denied! Only admins can manage results.", "danger")
        return redirect(url_for("home"))

    today = datetime.today().date()
    past_events = Event.query.filter(Event.date < today).all()

     # Check if each event has results
    for event in past_events:
        event.has_result = Result.query.join(Registration).filter(Registration.event_id == event.id).first() is not None


    return render_template('manage_results.html', past_events=past_events)



@app.route('/event/<int:event_id>/add_result', methods=['GET', 'POST'])
@login_required
def add_result(event_id):
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('home'))

    event = Event.query.get_or_404(event_id)
    registrations = Registration.query.filter_by(event_id=event_id).all()

    if request.method == 'POST':
        for reg in registrations:
            reg_id = reg.id
            attended = request.form.get(f'attended_{reg_id}') == "1"  # Checkbox handling
            position = request.form.get(f'position_{reg_id}', None) if attended else "-"
            points = request.form.get(f'points_{reg_id}', 0) if attended else "-"
            remarks = request.form.get(f'remarks_{reg_id}', "") if attended else "Absent - We missed you! Hope to see you next time! 😊"

            position = int(position) if attended and position else None
            points = float(points) if attended and points else None

            new_result = Result(
                registration_id=reg_id,
                attended=attended,
                position=position,
                points=points,
                remarks=remarks
            )
            db.session.add(new_result)

        db.session.commit()
        flash("Results added successfully!", "success")
        return redirect(url_for('view_results', event_id=event_id))

    return render_template('add_result.html', event=event, registrations=registrations)


@app.route('/event/<int:event_id>/update_result', methods=['GET', 'POST'])
@login_required
def update_result(event_id):
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('home'))

    event = Event.query.get_or_404(event_id)
    registrations = db.session.query(Registration, User).join(User, Registration.user_id == User.id).filter(Registration.event_id == event_id).all()
    results = {res.registration_id: res for res in Result.query.filter(Result.registration_id.in_([r[0].id for r in registrations])).all()}

    if not results:
        flash("No results found! Please add results first.", "warning")
        return redirect(url_for('add_result', event_id=event_id))

    if request.method == 'POST':
        for reg, user in registrations:
            reg_id = reg.id
            attended = request.form.get(f'attended_{reg_id}') == "1"
            position = request.form.get(f'position_{reg_id}', None) if attended else "-"
            points = request.form.get(f'points_{reg_id}', 0) if attended else "-"
            remarks = request.form.get(f'remarks_{reg_id}', "") if attended else "Absent - We missed you! Hope to see you next time! 😊"

            position = int(position) if attended and position else None
            points = float(points) if attended and points else None

            existing_result = results.get(reg_id)
            if existing_result:
                existing_result.attended = attended
                existing_result.position = position
                existing_result.points = points
                existing_result.remarks = remarks

        db.session.commit()
        flash("Results updated successfully!", "success")
        return redirect(url_for('view_results', event_id=event_id))

    return render_template('update_result.html', event=event, registrations=registrations, results=results)


@app.route('/event/<int:event_id>/results')
@login_required
def view_results(event_id):
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('home'))

    event = Event.query.get_or_404(event_id)
    results = Result.query.join(Registration).filter(Registration.event_id == event_id).all()

    return render_template('view_results.html', event=event, results=results)









@app.route("/user/results")
@login_required
def user_results():
    user_id = current_user.id

    # Get all past events and their results for the user
    past_results = (
        db.session.query(
            Event.title,
            Event.date,
            Result.position,
            Result.attended,
            Result.remarks
        )
        .join(Registration, Event.id == Registration.event_id)
        .join(Result, Registration.id == Result.registration_id)
        .filter(Registration.user_id == user_id)
        .all()
    )

    # Convert event date (string) to datetime before passing it to the template
    formatted_results = []
    for result in past_results:
        try:
            event_date = datetime.strptime(result.date, "%Y-%m-%d")  # Change format as needed
        except ValueError:
            event_date = result.date  # Keep it as-is if conversion fails
        
        formatted_results.append({
            "title": result.title,
            "date": event_date,  
            "position": result.position,
            "attended": result.attended,
            "remarks": result.remarks,
        })

    return render_template("user_results.html", past_results=formatted_results)






@app.route('/logout')
@login_required
def logout():
    logout_user()
    # flash('you have been logged out.','info')
    return redirect(url_for('login'))









@app.route('/admin/event_statistics')
@login_required
def event_statistics():
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('home'))

    # Fetch all events
    events = Event.query.all()
    event_stats = []

    # Overall Stats
    total_users = User.query.count()
    total_events = len(events)
    total_participants = Registration.query.count()
    total_revenue = db.session.query(func.sum(Event.fee)).join(Registration).scalar() or 0
    attendance_rate = db.session.query(func.avg(Result.attended)).scalar() * 100 if Result.query.count() > 0 else 0

    # Most Active Users
    most_active_users = (
        db.session.query(User.username, func.count(Registration.id).label("event_count"))
        .join(Registration)
        .group_by(User.id)
        .order_by(func.count(Registration.id).desc())
        .limit(5)
        .all()
    )

    # Event-wise Stats
    for event in events:
        total_participants = Registration.query.filter_by(event_id=event.id).count()
        total_results = Result.query.join(Registration).filter(Registration.event_id == event.id).all()
        total_fees_collected = total_participants * event.fee

        # Fetch top 3 winners
        winners = [
        {"username": winner.username, "position": winner.position} for winner in db.session.query(User.username, Result.position)
        .join(Registration, Registration.id == Result.registration_id)
        .join(User, Registration.user_id == User.id)
        .filter(Registration.event_id == event.id, Result.position.isnot(None))
        .order_by(Result.position.asc())
        .limit(3)
        .all()
    ]


        avg_points = db.session.query(func.avg(Result.points)).join(Registration).filter(Registration.event_id == event.id).scalar() or 0
        max_points = db.session.query(func.max(Result.points)).join(Registration).filter(Registration.event_id == event.id).scalar() or 0
        min_points = db.session.query(func.min(Result.points)).join(Registration).filter(Registration.event_id == event.id).scalar() or 0

        event_stats.append({
            "event_title": event.title,
            "total_participants": total_participants,
            "total_fees_collected": total_fees_collected,
            "winners": winners,
            "avg_points": round(avg_points, 2),
            "max_points": max_points,
            "min_points": min_points,
        })

    return render_template('event_statistics.html', event_stats=event_stats, 
                           total_users=total_users, total_events=total_events, 
                           total_participants=total_participants, total_revenue=total_revenue,
                           attendance_rate=round(attendance_rate, 2), 
                           most_active_users=most_active_users)




if __name__ == '__main__':
    app.run(debug=True)
