from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from models import Event, Registration
from send_email import send_reminder_email

def send_reminders(app):
    with app.app_context():
        events = Event.query.all()
        for event in events:
            reminder_time = event.date - timedelta(days=1)  # Send reminder 1 day before the event
            if datetime.now() >= reminder_time:
                registrations = Registration.query.filter_by(event_id=event.id).all()
                for reg in registrations:
                    send_reminder_email(reg.user.email, reg.user.username, event)

def start_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: send_reminders(app), 'interval', hours=24)  # Check every 24 hours
    scheduler.start()