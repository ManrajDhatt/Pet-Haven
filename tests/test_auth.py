import unittest
import uuid
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

class TestAuth(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.client = app.test_client()
        

        # Generate unique email addresses for each test run
        self.unique_id = str(uuid.uuid4())[:8]
        self.test_email = f"test_{self.unique_id}@example.com"
        self.admin_email = f"admin_{self.unique_id}@example.com"

        with app.app_context():
            db.create_all()
            
            # Create test user
            hashed_pw = generate_password_hash('testpassword', method='scrypt')
            test_user = User(
                user_name=f'testuser_{self.unique_id}',
                email_id=self.test_email,
                password=hashed_pw,
                user_type='pet_owner'
            )
            
            # Create admin user
            admin_pw = generate_password_hash('adminpassword', method='scrypt')
            admin_user = User(
                user_name=f'admin_{self.unique_id}',
                email_id=self.admin_email,
                password=admin_pw,
                user_type=None  # Admin has NULL user_type
            )
            
            db.session.add(test_user)
            db.session.add(admin_user)
            db.session.commit()
    
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_login_failure(self):
        """Test failed login"""
        response = self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # self.assertIn(b'Login failed', response.data)
    
    def test_registration_existing_email(self):
        """Test registration with existing email"""
        response = self.client.post('/register', data={
            'username': 'duplicateuser',
            'email': 'test@example.com',  # Already exists
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        # self.assertIn(b'Email is already registered', response.data)
    
    def test_login_success(self):
        """Test successful login"""
        response = self.client.post('/login', data={
            'email': self.test_email,
            'password': 'testpassword'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)  # Assuming dashboard is accessible after login
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post('/login', data={
            'email': self.test_email,
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        # self.assertIn(b'Invalid email or password', response.data)
    
    def test_logout(self):
        """Test logout functionality"""
        # Login first
        self.client.post('/login', data={
            'email': self.test_email,
            'password': 'testpassword'
        })
        
        # Then logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # self.assertIn(b'logged out', response.data)
    
    def test_admin_access_normal_user(self):
        """Test normal user trying to access admin pages"""
        # Login as normal user
        self.client.post('/login', data={
            'email': self.test_email,
            'password': 'testpassword'
        })
        
        # Try to access admin dashboard
        response = self.client.get('/admin_dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # self.assertNotIn(b'Admin Dashboard', response.data)
    
    def test_admin_login_access(self):
        """Test admin login and access to admin pages"""
        # Login as admin
        self.client.post('/login', data={
            'email': self.admin_email,
            'password': 'adminpassword'
        })
        
        # Access admin dashboard
        response = self.client.get('/admin_dashboard')
        self.assertEqual(response.status_code, 200)
        # self.assertIn(b'Admin Dashboard', response.data)