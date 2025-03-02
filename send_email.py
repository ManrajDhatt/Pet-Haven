from flask import current_app
from flask_mail import Mail, Message

mail = Mail()  # Initialize Mail without app instance

def send_confirmation_email(email, username, event, pet_name, pet_type, pet_age):
    with current_app.app_context():  # Ensure the correct Flask context
        
        subject = f"🎉 Registration Confirmation for {event.title}!"

        message_body = f"""
        <div style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; border-radius: 10px;">
            <div style="background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #ff6600; text-align: center;">🎊 {event.title} 🎊</h1>
                
                <p style="font-size: 16px; color: #333;">Hi <strong>{username}</strong>,</p>
                
                <p style="font-size: 16px; color: #333;">
                    You have successfully registered for <strong>{event.title}</strong>. Below are the details of your registration.
                </p>
                
                <h2 style="color: #ff6600; text-align: center;">📅 Event Details</h2>
                
                <div style="text-align: center;">
                    <img src="https://pet-haven-0fux.onrender.com/static/images/{event.image_filename}" 
                         alt="Event Image" width="400" 
                         style="border-radius: 10px; box-shadow: 0px 0px 8px rgba(0,0,0,0.1);">
                </div>
                
                <p style="font-size: 14px; color: #555; text-align: center;">
                    <em>{event.description}</em>
                </p>

                <ul style="list-style-type: none; padding: 0; text-align: center;">
                    <li><strong>📅 Date:</strong> {event.date}</li>
                    <li><strong>📍 Location:</strong> {event.location}</li>
                    <li><strong>💰 Entry Fee:</strong> ₹{event.fee:.2f}</li>
                    <li><strong>🏆 Prizes:</strong> {event.prizes}</li>
                    <li><strong>✔ Eligibility:</strong> {event.eligibility}</li>
                </ul>

                <hr style="border: 1px solid #ddd; margin: 20px 0;">

                <h2 style="color: #ff6600; text-align: center;">🐶 Your Pet Details</h2>
                
                <ul style="list-style-type: none; padding: 0; text-align: center;">
                    <li><strong>📛 Name:</strong> {pet_name}</li>
                    <li><strong>🦴 Type:</strong> {pet_type}</li>
                    <li><strong>🎂 Age:</strong> {pet_age} years</li>
                </ul>

                <p style="text-align: center; font-size: 16px; color: #333;">
                    We are excited to have you and <strong>{pet_name}</strong> at the event! 🐕🐾
                </p>

                <div style="text-align: center; margin-top: 20px;">
                    <a href="https://pet-haven-0fux.onrender.com" 
                       style="background-color: #ff6600; color: white; padding: 10px 20px; 
                              text-decoration: none; border-radius: 5px; font-size: 16px;">
                        Visit Event Page
                    </a>
                </div>

                <p style="text-align: center; font-size: 14px; color: #666; margin-top: 20px;">
                    📩 If you have any questions, feel free to contact us!
                </p>

                <p style="text-align: center; font-size: 16px; font-weight: bold; color: #333;">
                    Best Regards, <br>
                    🐾 Pet Haven Team 🐾
                </p>
            </div>
        </div>
        """

        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],  # Ensure sender is defined in config
            recipients=[email],
            html=message_body
        )

        mail.send(msg)  # Send the email
