import unittest
from app import app, db
from models import User, Event, Registration, Result
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class TestModels(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_creation(self):
        """Test User model creation"""
        user = User(
            user_name='testuser',
            email_id='test@example.com',
            password='password_hash',
            user_type='pet_owner'
        )
        db.session.add(user)
        db.session.commit()
        
        retrieved_user = User.query.filter_by(email_id='test@example.com').first()
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.user_name, 'testuser')
        
    def test_event_registration(self):
        """Test event registration"""
        # Create user
        user = User(
            user_name='testuser',
            email_id='test@example.com',
            password='password_hash',
            user_type='pet_owner'
        )
        db.session.add(user)
        
        # Create event
        event = Event(
            title='Test Event',
            description='Test Description',
            date='2025-05-01',
            location='Test Location',
            prizes='Test Prizes',
            eligibility='Test Eligibility',
            fee=500
        )
        db.session.add(event)
        db.session.commit()
        
        # Register for event
        registration = Registration(
            user_id=user.user_id,
            event_id=event.id,
            pet_name='Fluffy',
            pet_type='Dog',
            pet_age=3
        )
        db.session.add(registration)
        db.session.commit()
        
        # Check if registration was successful
        registrations = Registration.query.filter_by(user_id=user.user_id).all()
        self.assertEqual(len(registrations), 1)
        self.assertEqual(registrations[0].pet_name, 'Fluffy')

    def test_user_password_hashing(self):
        """Test password hashing functionality"""
        raw_password = 'test_password'
        hashed_password = generate_password_hash(raw_password, method='scrypt')
        
        user = User(
            user_name='passworduser',
            email_id='password@test.com',
            password=hashed_password,
            user_type='pet_owner'
        )
        db.session.add(user)
        db.session.commit()
        
        retrieved_user = User.query.filter_by(email_id='password@test.com').first()
        self.assertTrue(check_password_hash(retrieved_user.password, raw_password))
        self.assertFalse(check_password_hash(retrieved_user.password, 'wrong_password'))
    
    def test_event_creation_with_all_fields(self):
        """Test event creation with all fields"""
        event = Event(
            title='Comprehensive Event',
            description='Detailed description',
            date='2025-06-15',
            location='Central Park',
            prizes='Cash prizes',
            eligibility='All pets',
            fee=750.0,
            image_filename='test_image.jpg'
        )
        db.session.add(event)
        db.session.commit()
        
        retrieved_event = Event.query.filter_by(title='Comprehensive Event').first()
        self.assertEqual(retrieved_event.location, 'Central Park')
        self.assertEqual(retrieved_event.fee, 750.0)
    
    def test_registration_with_payment_status(self):
        """Test registration with payment status"""
        # Create user
        user = User(
            user_name='paymentuser',
            email_id='payment@test.com',
            password='hashed_password',
            user_type='pet_owner'
        )
        db.session.add(user)
        
        # Create event
        event = Event(
            title='Payment Test Event',
            description='Test Description',
            date='2025-07-01',
            location='Test Location',
            prizes='Test Prizes',
            eligibility='Test Eligibility',
            fee=1000
        )
        db.session.add(event)
        db.session.commit()
        
        # Create registration with paid status
        paid_registration = Registration(
            user_id=user.user_id,
            event_id=event.id,
            pet_name='Rex',
            pet_type='Dog',
            pet_age=5,
            paid=True
        )
        db.session.add(paid_registration)
        db.session.commit()
        
        # Check if payment status is saved correctly
        retrieved_registration = Registration.query.filter_by(pet_name='Rex').first()
        self.assertTrue(retrieved_registration.paid)
    
    def test_result_creation_and_relationship(self):
        """Test result creation and its relationships"""
        # Create user
        user = User(
            user_name='resultuser',
            email_id='result@test.com',
            password='hashed_password',
            user_type='pet_owner'
        )
        db.session.add(user)
        
        # Create event
        event = Event(
            title='Result Test Event',
            description='Test Description',
            date='2025-08-01',
            location='Test Location',
            prizes='Test Prizes',
            eligibility='Test Eligibility',
            fee=500
        )
        db.session.add(event)
        db.session.commit()
        
        # Create registration
        registration = Registration(
            user_id=user.user_id,
            event_id=event.id,
            pet_name='Champion',
            pet_type='Cat',
            pet_age=3,
            paid=True
        )
        db.session.add(registration)
        db.session.commit()
        
        # Create result
        result = Result(
            registration_id=registration.id,
            attended=True,
            position=1,
            points=100,
            remarks='Outstanding performance'
        )
        db.session.add(result)
        db.session.commit()
        
        # Verify result was created and linked correctly
        retrieved_result = Result.query.filter_by(registration_id=registration.id).first()
        self.assertEqual(retrieved_result.position, 1)
        self.assertEqual(retrieved_result.points, 100)
        
        # Verify the relationship between registration and result
        self.assertEqual(retrieved_result.registration_id, registration.id)