from werkzeug.security import generate_password_hash
import uuid
import enum
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db=SQLAlchemy()
    
#******************************************* Dogs Ownership Table (Many-to-Many) **********************************
dog_ownership = db.Table(
    "dog_ownership",
    db.Column("user_id", db.String(36), db.ForeignKey("user.user_id"), primary_key=True),
    db.Column("dog_id", db.String(36), db.ForeignKey("dogs.dog_id"), primary_key=True)
)

#*************************************** User and ServiceProvider (Many-to-Many) Relationship ****************
user_service_provider = db.Table(
    "user_service_provider",
    db.Column("user_id", db.String(36), db.ForeignKey("user.user_id"), primary_key=True),
    db.Column("service_id", db.Integer, db.ForeignKey("service_provider.service_id"), primary_key=True)
)


class User(db.Model,UserMixin):
    __tablename__ = 'user'
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # Use UUID
    user_name = db.Column(db.String(50), nullable=False, unique=True)
    email_id = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Storing hashed password
    phone_number = db.Column(db.String(10), nullable=True)
    address = db.Column(db.String(50), nullable=True)
    user_type = db.Column(db.String(20), nullable=True)  # NULL for Admin, 'Pet Owner' or 'Service Provider' for users
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    orders = db.relationship("Order", backref="user", lazy=True)
    carts = db.relationship("Cart", backref="user", lazy=True)
    bookings = db.relationship("Booking", backref="user", lazy=True)
    service_providers = db.relationship("ServiceProvider", secondary=user_service_provider, back_populates="users")
    dogs = db.relationship("Dogs", secondary=dog_ownership, back_populates="owners")
    
    @property
    def is_admin(self):
        return self.user_type is None  

    def get_id(self):  
        return str(self.user_id)
    def __repr__(self):
        return f"<User {self.user_type} - {self.user_name}>"


class Service(db.Model):
    __tablename__ = 'services'
    service_id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(50))
    description = db.Column(db.Text)  # Added description column



# ****************************************** Dogs Table (Renamed from Dog) *******************************************
class Dogs(db.Model):
    __tablename__ = "dogs"

    dog_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(60), nullable=False)
    breed = db.Column(db.String(60), nullable=False)
    age = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    vaccinated = db.Column(db.String(3), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(200), nullable=False)

    order_details = db.relationship("OrderDetail", backref="dogs", lazy=True)
    cart_items = db.relationship("CartItem", back_populates="dog", lazy=True)
    owners = db.relationship("User", secondary=dog_ownership, back_populates="dogs")

    def __repr__(self):
        return f"<Dogs {self.name} - {self.breed}>"

# ****************************************** Service Provider Table *******************************************
class ServiceProviderStatus(enum.Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"

class ServiceProvider(db.Model):
    __tablename__ = "service_provider"
    
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), primary_key=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)    
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    service_name = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    hourly_rate = db.Column(db.Integer, nullable=False)
    experience = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum(ServiceProviderStatus), default=ServiceProviderStatus.PENDING, nullable=False)
    document_folder = db.Column(db.String(255), nullable=False)

    # Many-to-Many Relationship with Users
    users = db.relationship("User", secondary=user_service_provider, back_populates="service_providers")

    def __repr__(self):
        return f"<ServiceProvider {self.name}>"


# ****************************************** Booking Table ****************************************************
class Booking(db.Model):
    __tablename__ = "booking"

    booking_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("user.user_id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    duration = db.Column(db.Time, nullable=False)
    total_cost = db.Column(db.Integer, nullable=False)

    booking_details = db.relationship("BookingDetail", backref="booking", lazy=True)
    order_details = db.relationship("OrderDetail", back_populates="booking", lazy=True)
    cart_items = db.relationship("CartItem", back_populates="booking", lazy=True)

    def __repr__(self):
        return f"<Booking {self.booking_id} - User {self.user_id}>"

# ****************************************** Booking Details Table *******************************************
class BookingDetail(db.Model):
    __tablename__ = "booking_detail"

    booking_detail_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id = db.Column(db.String(36), db.ForeignKey("booking.booking_id"), nullable=False)
    # service_id = db.Column(db.String(36), nullable=False)
    service_id = db.Column(db.Integer, nullable=False)  # Changed to Integer

    user_id = db.Column(db.String(36), nullable=False)
    service_name = db.Column(db.String(100), nullable=False)
    service_price = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.ForeignKeyConstraint(
            ['service_id', 'user_id'],
            ['service_provider.service_id', 'service_provider.user_id']
        ),
    )

    def __repr__(self):
        return f"<BookingDetail {self.booking_detail_id} - Booking {self.booking_id}>"

# ********************************************* Order Table **************************************************
class PaymentStatus(enum.Enum):
    PENDING = "Pending"
    SUCCESS = "Success"

class Order(db.Model):
    __tablename__ = "order"

    order_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("user.user_id"), nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    shipping_address = db.Column(db.String(255), nullable=False)
    payment_status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    order_details = db.relationship("OrderDetail", back_populates="order", lazy=True)

    def __repr__(self):
        return f"<Order {self.order_id} - {self.total_amount}>"

# ****************************************** Order Details Table *******************************************
class OrderDetail(db.Model):
    __tablename__ = "order_detail"

    order_detail_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey("order.order_id"), nullable=False)
    dog_id = db.Column(db.String(36), db.ForeignKey("dogs.dog_id"), nullable=True)
    booking_id = db.Column(db.String(36), db.ForeignKey("booking.booking_id"), nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    booking = db.relationship("Booking", back_populates="order_details", lazy=True)
    dog = db.relationship("Dogs", back_populates="order_details", lazy=True, overlaps="dogs")
    order = db.relationship("Order", back_populates="order_details", lazy=True)

    def __repr__(self):
        return f"<OrderDetail {self.order_detail_id} - {self.quantity}>"

# ********************************************* Cart Table ***************************************************
class Cart(db.Model):
    __tablename__ = "cart"

    cart_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("user.user_id"), nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    cart_items = db.relationship("CartItem", back_populates="cart", lazy=True)

    def __repr__(self):
        return f"<Cart {self.cart_id} - {self.total_amount}>"

# ******************************************** Cart Items Table **********************************************
class CartItem(db.Model):
    __tablename__ = "cart_item"

    cart_item_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cart_id = db.Column(db.String(36), db.ForeignKey("cart.cart_id"), nullable=False)
    dog_id = db.Column(db.String(36), db.ForeignKey("dogs.dog_id"), nullable=True)
    booking_id = db.Column(db.String(36), db.ForeignKey("booking.booking_id"), nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    booking = db.relationship("Booking", back_populates="cart_items", lazy=True)
    dog = db.relationship("Dogs", back_populates="cart_items", lazy=True)
    cart = db.relationship("Cart", back_populates="cart_items", lazy=True)
    def __repr__(self):
        return f"<CartItem {self.cart_item_id} - {self.quantity}>"


class Event(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(50), nullable=False)
    location=db.Column(db.String(250),nullable=False)
    prizes=db.Column(db.String(200),nullable=False)
    eligibility=db.Column(db.String(250),nullable=False)
    fee = db.Column(db.Float, default=500)
    image_filename = db.Column(db.String(200), nullable=False, default="default.jpg") 


class Registration(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    event_id = db.Column(db.String(36), db.ForeignKey('event.id'), nullable=False)
    pet_name = db.Column(db.String(100), nullable=False)
    pet_type = db.Column(db.String(100), nullable=False)
    pet_age=db.Column(db.Integer,nullable=False)
    paid = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  
    
     # Relationship with Event
    event = db.relationship('Event', backref=db.backref('registrations', lazy=True))

    # Relationship with User 
    user = db.relationship('User', backref=db.backref('registrations', lazy=True))



class Result(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    registration_id = db.Column(db.String(36), db.ForeignKey('registration.id'), nullable=False, unique=True)
    attended = db.Column(db.Boolean, default=False, nullable=False)  # Present or Absent
    position = db.Column(db.Integer, nullable=True)  # 1,2,...
    points = db.Column(db.Float, default=0)  # Optional: Track performance points
    remarks = db.Column(db.Text, nullable=True)  # Any comments (e.g., "Great performance")

    # Relationship with Registration
    registration = db.relationship('Registration', backref=db.backref('result', uselist=False, lazy=True))


class Transaction(db.Model):
    __tablename__ = 'transaction'

    t_id = db.Column(db.String(50), primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    
    # Foreign key to the 'User' table
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)  

    # Composite foreign key (service_id, user_id) referencing ServiceProvider table
    service_id = db.Column(db.Integer, nullable=False)
    # provider_user_id = db.Column(db.Integer, nullable=False)
    provider_user_id = db.Column(db.String(36), nullable=False)

    __table_args__ = (
        db.ForeignKeyConstraint(
            ['service_id', 'provider_user_id'],
            ['service_provider.service_id', 'service_provider.user_id']
        ),
    )

    # Relationships
    user = db.relationship("User", backref="transactions", lazy=True)  
    service_provider = db.relationship("ServiceProvider", backref="transactions", lazy=True)

    def __repr__(self):
        return f"<Transaction {self.t_id} - User {self.user_id} - Service {self.service_id}>"


# Function to insert predefined data including admin
def insert_initial_data():
    if Service.query.count() == 0:
        services_data = [
            (1, "Grooming", "Keep your furry friends looking and feeling their best with our professional grooming services."),
            (2, "Therapies", "Enhance your pet’s well-being with specialized therapy services like physiotherapy and hydrotherapy."),
            (3, "Health", "Comprehensive health services including check-ups, vaccinations, and nutritional guidance."),
            (4, "Training", "Expert training programs for obedience, behavior correction, and skill development."),
            (5, "Spa", "Luxurious spa services including soothing baths, fur conditioning, and aromatherapy."),
        ]
        for service in services_data:
            db.session.add(Service(service_id=service[0], service_name=service[1], description=service[2]))
        db.session.commit()
        print("Inserted initial service data.")

    # Insert admin directly into User table
    admin_username = "Admin"
    admin_email = "admin@example.com"
    admin_password = "password@123"

    admin_user = User.query.filter_by(user_name=admin_username).first()
    if not admin_user:
        hashed_password = generate_password_hash(admin_password,method='scrypt')
        admin = User(
            user_name=admin_username,
            email_id=admin_email,
            password=hashed_password,
            phone_number=None,
            address=None,
            user_type=None,  # NULL for Admin
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Inserted default admin user.")
        



