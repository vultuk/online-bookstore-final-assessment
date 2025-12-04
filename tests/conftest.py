import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app, users, orders, cart, BOOKS
from models import Book, Cart, User, Order, CartItem


@pytest.fixture
def app():
    """Create and configure a Flask app instance for testing"""
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test-secret-key'
    flask_app.config['WTF_CSRF_ENABLED'] = False
    yield flask_app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app"""
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_test_data():
    """Automatically clean up test data before each test"""
    yield
    # Clear cart after each test
    cart.clear()
    # Clear users except demo user
    users.clear()
    from app import demo_user
    users[demo_user.email] = demo_user
    # Clear orders
    orders.clear()


@pytest.fixture
def sample_book():
    """Create a sample book for testing"""
    return Book("Test Book", "Fiction", 15.99, "/images/test.jpg")


@pytest.fixture
def sample_books():
    """Return the list of sample books from the app"""
    return BOOKS


@pytest.fixture
def empty_cart():
    """Create a fresh empty cart"""
    test_cart = Cart()
    return test_cart


@pytest.fixture
def cart_with_items(sample_book):
    """Create a cart with some test items"""
    test_cart = Cart()
    test_cart.add_book(sample_book, 2)
    return test_cart


@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    return User(
        email="test@example.com",
        password="testpass123",
        name="Test User",
        address="123 Test St, Test City, TC 12345"
    )


@pytest.fixture
def registered_user(sample_user):
    """Register a sample user and return it"""
    users[sample_user.email] = sample_user
    return sample_user


@pytest.fixture
def logged_in_session(client, registered_user):
    """Create a logged-in session for testing protected routes"""
    with client.session_transaction() as sess:
        sess['user_email'] = registered_user.email
    return client


@pytest.fixture
def sample_order(sample_user, cart_with_items):
    """Create a sample order for testing"""
    shipping_info = {
        'name': sample_user.name,
        'email': sample_user.email,
        'address': sample_user.address,
        'city': 'Test City',
        'zip_code': '12345'
    }
    payment_info = {
        'method': 'credit_card',
        'transaction_id': 'TXN123456'
    }
    order = Order(
        order_id="TEST001",
        user_email=sample_user.email,
        items=cart_with_items.get_items(),
        shipping_info=shipping_info,
        payment_info=payment_info,
        total_amount=31.98
    )
    return order


@pytest.fixture
def valid_checkout_form():
    """Create valid checkout form data"""
    return {
        'name': 'John Doe',
        'email': 'john@example.com',
        'address': '456 Main St',
        'city': 'Springfield',
        'zip_code': '54321',
        'payment_method': 'credit_card',
        'card_number': '4532123456789012',
        'expiry_date': '12/25',
        'cvv': '123'
    }


@pytest.fixture
def valid_registration_form():
    """Create valid registration form data"""
    return {
        'email': 'newuser@example.com',
        'password': 'securepass123',
        'name': 'New User',
        'address': '789 New St, New City'
    }


@pytest.fixture
def failing_payment_card():
    """Card number that fails payment (ends in 1111)"""
    return {
        'payment_method': 'credit_card',
        'card_number': '4532123456781111',
        'expiry_date': '12/25',
        'cvv': '123'
    }


@pytest.fixture
def valid_payment_card():
    """Card number that succeeds payment"""
    return {
        'payment_method': 'credit_card',
        'card_number': '4532123456789012',
        'expiry_date': '12/25',
        'cvv': '123'
    }
