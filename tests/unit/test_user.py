import pytest
from models import User, Order


@pytest.mark.unit
class TestUser:
    """Unit tests for the User model"""

    def test_user_creation_full(self):
        """Test creating a user with all attributes"""
        user = User(
            email="user@example.com",
            password="password123",
            name="John Doe",
            address="123 Main St"
        )

        assert user.email == "user@example.com"
        assert user.password == "password123"
        assert user.name == "John Doe"
        assert user.address == "123 Main St"
        assert user.orders == []

    def test_user_creation_minimal(self):
        """Test creating a user with minimal attributes"""
        user = User(email="user@example.com", password="pass123")

        assert user.email == "user@example.com"
        assert user.password == "pass123"
        assert user.name == ""
        assert user.address == ""

    @pytest.mark.bug
    def test_unused_attributes_removed(self):
        """FIXED BUG #7: Verify that unused attributes temp_data and cache were removed"""
        user = User("test@example.com", "password")

        # These attributes should no longer exist after bug fix
        assert not hasattr(user, 'temp_data'), "temp_data attribute should have been removed"
        assert not hasattr(user, 'cache'), "cache attribute should have been removed"

        # Verify that essential attributes still exist
        assert hasattr(user, 'email')
        assert hasattr(user, 'orders')
        assert hasattr(user, '_orders_sorted')

    def test_add_order(self, sample_user, sample_order):
        """Test adding an order to user"""
        sample_user.add_order(sample_order)

        assert len(sample_user.orders) == 1
        assert sample_user.orders[0] == sample_order

    @pytest.mark.bug
    @pytest.mark.performance
    def test_add_order_sorting_inefficiency(self, sample_user, sample_order):
        """BUG #8: Test that orders are sorted on every add (inefficient)"""
        # Adding multiple orders triggers sort on each add
        order1 = sample_order
        order2 = Order("TEST002", "test@example.com", [], {}, {}, 50.00)
        order3 = Order("TEST003", "test@example.com", [], {}, {}, 75.00)

        sample_user.add_order(order1)
        sample_user.add_order(order2)
        sample_user.add_order(order3)

        # Orders should be sorted by date
        assert len(sample_user.orders) == 3
        # Note: This sort happens on EVERY add_order call (inefficient)

    def test_add_multiple_orders(self, sample_user, sample_order):
        """Test adding multiple orders"""
        order2 = Order("TEST002", "test@example.com", [], {}, {}, 50.00)
        order3 = Order("TEST003", "test@example.com", [], {}, {}, 75.00)

        sample_user.add_order(sample_order)
        sample_user.add_order(order2)
        sample_user.add_order(order3)

        assert len(sample_user.orders) == 3

    def test_get_order_history(self, sample_user, sample_order):
        """Test getting order history"""
        order2 = Order("TEST002", "test@example.com", [], {}, {}, 50.00)

        sample_user.add_order(sample_order)
        sample_user.add_order(order2)

        history = sample_user.get_order_history()

        assert len(history) == 2
        assert all(isinstance(order, Order) for order in history)

    def test_get_order_history_empty(self, sample_user):
        """Test getting order history when no orders exist"""
        history = sample_user.get_order_history()

        assert history == []

    @pytest.mark.performance
    def test_get_order_history_creates_new_list(self, sample_user, sample_order):
        """BUG #8: Test that get_order_history creates unnecessary new list"""
        sample_user.add_order(sample_order)

        history1 = sample_user.get_order_history()
        history2 = sample_user.get_order_history()

        # Each call creates a new list (inefficient)
        # Note: This is documented as inefficiency in INSTRUCTOR_BUGS_LIST.md
        assert isinstance(history1, list)
        assert isinstance(history2, list)

    def test_user_password_storage(self):
        """Test that passwords are stored (note: plaintext storage is a known issue)"""
        user = User("user@example.com", "secretpassword")

        # Note: Password is stored in plaintext (security issue)
        assert user.password == "secretpassword"

    def test_user_with_special_characters_in_email(self):
        """Test user with special characters in email"""
        user = User("user+test@example.com", "password")

        assert user.email == "user+test@example.com"
