import unittest
from app import app, db
from models import User, Event, Registration, Result
from werkzeug.security import generate_password_hash
from datetime import datetime

class TestFunctional(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
            
            # Create test user
            hashed_pw = generate_password_hash('testpassword', method='scrypt')
            test_user = User(
                user_name='testuser',
                email_id='test@example.com',
                password=hashed_pw,
                user_type='pet_owner'
            )
            
            # Create admin user
            admin_pw = generate_password_hash('adminpassword', method='scrypt')
            admin_user = User(
                user_name='admin',
                email_id='admin@example.com',
                password=admin_pw,
                user_type=None
            )
            
            # Create test event
            test_event = Event(
                title='Test Event',
                description='Test description',
                date='2025-10-15',
                location='Test Location',
                prizes='Test Prizes',
                eligibility='Test Eligibility',
                fee=500,
                image_filename='default.jpg'
            )
            
            db.session.add(test_user)
            db.session.add(admin_user)
            db.session.add(test_event)
            db.session.commit()
    
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_complete_registration_flow(self):
        """Test the complete flow of user registration and event registration"""
        # Step 1: Login
        response = self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Step 2: View competitions
        response = self.client.get('/competitions')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Event', response.data)
        
        # Step 3: Get event ID for registration
        with app.app_context():
            event = Event.query.filter_by(title='Test Event').first()
            event_id = event.id
        
        # Step 4: Register for event
        response = self.client.post(f'/register/{event_id}', data={
            'pet_name': 'TestPet',
            'pet_type': 'Dog',
            'pet_age': '4'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Successfully registered', response.data)
        
        # Step 5: Check registrations page
        response = self.client.get('/registrations')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'TestPet', response.data)
        
        # Verify registration in database
        with app.app_context():
            registration = Registration.query.filter_by(pet_name='TestPet').first()
            self.assertIsNotNone(registration)
            self.assertEqual(registration.pet_type, 'Dog')
    
    def test_admin_event_management_flow(self):
        """Test the flow of admin creating and managing events"""
        # Step 1: Login as admin
        response = self.client.post('/login', data={
            'email': 'admin@example.com',
            'password': 'adminpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Add new event
        response = self.client.post('/add_event', data={
            'title': 'New Admin Event',
            'description': 'Created by admin',
            'location': 'Admin Location',
            'date': '2025-11-20',
            'eligibility': 'All pets',
            'prizes': 'Admin prizes',
            'fee': '750'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Event added successfully', response.data)
        
        # Verify event in database
        with app.app_context():
            event = Event.query.filter_by(title='New Admin Event').first()
            self.assertIsNotNone(event)
            event_id = event.id
        
        # Step 3: Edit event
        response = self.client.post(f'/edit_event/{event_id}', data={
            'title': 'Updated Event Title',
            'description': 'Updated description',
            'location': 'Updated location',
            'date': '2025-12-25',
            'eligibility': 'Updated eligibility',
            'prizes': 'Updated prizes',
            'fee': '1000'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Event updated successfully', response.data)
        
        # Verify event was updated
        with app.app_context():
            updated_event = Event.query.get(event_id)
            self.assertEqual(updated_event.title, 'Updated Event Title')
            self.assertEqual(updated_event.fee, 1000.0)