from flask import current_app, url_for
from flask_mail import Mail, Message
import base64
import os
def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

mail = Mail()  # Initialize Mail without app instance

def send_confirmation_email(email, username, event, pet_name, pet_type, pet_age):
    with current_app.app_context():  # Ensure the correct Flask context
        image_path = os.path.join(current_app.root_path, 'static/images', event.image_filename)
        image_base64 = encode_image(image_path)
        subject = f"Registration Confirmation for {event.title}"
        message_body = f"""
        <h2>Hi {username},</h2>

        <p>You have successfully registered for <strong>{event.title}</strong>.</p>

        <h3>Event Details:</h3>
        <p>
        <img src="data:image/jpeg;base64,{image_base64}" width="300">
        </p>
        <ul>
            <li><strong>Date:</strong> {event.date}</li>
            <li><strong>Location:</strong> {event.location}</li>
            <li><strong>Entry Fee:</strong> ₹{event.fee}</li>
        </ul>

        <h3>Your Pet Details:</h3>
        <ul>
            <li><strong>Name:</strong> {pet_name}</li>
            <li><strong>Type:</strong> {pet_type}</li>
            <li><strong>Age:</strong> {pet_age}</li>
        </ul>

        <p>Thank you for registering!</p>

        <p>Best Regards,</p>
        <p>Event Team</p>
        """

        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],  # Ensure sender is defined in config
            recipients=[email],
            html=message_body
        )

        mail.send(msg)  # Send the email
