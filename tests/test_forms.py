import unittest
from forms import RegistrationForm, LoginForm, EventForm, RegistrationEventForm, ResultForm
from flask_wtf.csrf import generate_csrf
from app import app
from datetime import date, timedelta

class TestForms(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app_context = app.app_context()
        self.app_context.push()
        
    def tearDown(self):
        self.app_context.pop()
        
    def test_registration_form_validation(self):
        """Test registration form validation"""
        # Valid form data
        form = RegistrationForm(
            username='newuser',
            email='new@example.com',
            password='password123',
            confirm_password='password123'
        )
        self.assertTrue(form.validate())
        
        # Invalid email
        form = RegistrationForm(
            username='newuser',
            email='notanemail',
            password='password123',
            confirm_password='password123'
        )
        self.assertFalse(form.validate())
        
        # Password mismatch
        form = RegistrationForm(
            username='newuser',
            email='new@example.com',
            password='password123',
            confirm_password='different'
        )
        self.assertFalse(form.validate())
        
    def test_login_form_validation(self):
        """Test login form validation"""
        # Valid form data
        form = LoginForm(
            email='user@example.com',
            password='password'
        )
        self.assertTrue(form.validate())
        
        # Missing email
        form = LoginForm(
            email='',
            password='password'
        )
        self.assertFalse(form.validate())
        
    def test_event_form_validation(self):
        """Test event form validation"""
        # Create a valid future date
        future_date = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Valid form data
        form = EventForm(
            title='Test Event',
            description='Test description',
            location='Test Location',
            date=future_date,
            eligibility='All pet owners',
            prizes='Trophy and certificate',
            fee=500.0
        )
        self.assertTrue(form.validate())
        
        # Missing required field
        form = EventForm(
            title='',
            description='Test description',
            location='Test Location',
            date=future_date,
            eligibility='All pet owners',
            prizes='Trophy and certificate',
            fee=500.0
        )
        self.assertFalse(form.validate())
        
    def test_registration_event_form(self):
        """Test event registration form validation"""
        # Valid data
        form = RegistrationEventForm(
            pet_name='Buddy',
            pet_type='Dog',
            pet_age='3'
        )
        self.assertTrue(form.validate())
        
        # Invalid data (missing fields)
        form = RegistrationEventForm(
            pet_name='',
            pet_type='Dog',
            pet_age='3'
        )
        self.assertFalse(form.validate())
    
    def test_result_form_validation(self):
        """Test result form validation"""
        # Valid data
        form = ResultForm(
            attended=True,
            position=1,
            points=10,
            remarks='Excellent performance'
        )
        self.assertTrue(form.validate())
        
        # Invalid position (negative)
        form = ResultForm(
            attended=True,
            position=-1,
            points=10,
            remarks='Excellent performance'
        )
        self.assertFalse(form.validate())