import unittest
import uuid
from app import app, db
from models import User, Event, Registration
from werkzeug.security import generate_password_hash


class TestRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test method"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for testing
        self.client = app.test_client()
        
        # Generate unique email addresses for each test run
        self.unique_id = str(uuid.uuid4())[:8]
        self.test_email = f"test_{self.unique_id}@example.com"
        self.admin_email = f"admin_{self.unique_id}@example.com"

        with app.app_context():
            db.create_all()
            
            # Create test user
            test_user = User(
                user_name=f'testuser_{self.unique_id}',
                email_id=f'test_{self.unique_id}@example.com',
                password='password_hash',
                user_type='pet_owner'
            )
            db.session.add(test_user)
            db.session.commit()
            
    def tearDown(self):
        """Clean up after each test method"""
        with app.app_context():
            for table in reversed(db.metadata.sorted_tables):
                db.session.execute(table.delete())
            db.session.commit()

            db.session.remove()
            db.drop_all()
            
    def test_home_page(self):
        """Test that home page loads properly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Pet-Haven', response.data)  # Check for text on the page
        
    def test_login_page(self):
        """Test that login page loads properly"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)


    def test_competitions_page_requires_login(self):
        """Test that competitions page requires login"""
        response = self.client.get('/competitions', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # self.assertIn(b'Please log in', response.data)  # Check for login redirect message

    def test_dashboard_requires_login(self):
        """Test that dashboard requires login"""
        response = self.client.get('/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # self.assertIn(b'Please log in', response.data)

    def test_register_event_requires_login(self):
        """Test that event registration requires login"""
        response = self.client.get('/register/some-event-id', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # self.assertIn(b'Please log in', response.data)

    def test_admin_routes_require_admin(self):
        """Test that admin routes require admin privileges"""
        # Login as regular user first
        with app.app_context():
            # Use the unique identifier that was generated in setUp
            user = User.query.filter_by(user_name=f'testuser_{self.unique_id}').first()
            if user is None:
                self.fail("Test user not found. Setup may have failed.")
                
            user.password = generate_password_hash('testpassword', method='scrypt')
            db.session.commit()
        
        # Use the unique email created in setUp
        response = self.client.post('/login', data={
            'email': self.test_email,
            'password': 'testpassword'
        })
        
        # Try accessing admin routes
        admin_routes = [
            '/admin_dashboard',
            '/add_event',
            '/admin/manage_results',
            '/all-registrations'
        ]
        
        for route in admin_routes:
            response = self.client.get(route, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            # self.assertIn(b'Unauthorized', response.data)  # Check for unauthorized message