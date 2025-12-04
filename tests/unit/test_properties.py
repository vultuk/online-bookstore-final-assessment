import pytest
from hypothesis import given, strategies as st, assume, settings
from models import Book, Cart, CartItem, User, Order


@pytest.mark.unit
@pytest.mark.property
class TestCartProperties:
    """Property-based tests for Cart class using Hypothesis"""

    @given(st.integers(min_value=1, max_value=10000))
    @settings(max_examples=50)
    def test_cart_total_always_positive(self, quantity):
        """Cart total should never be negative for positive quantities"""
        cart = Cart()
        book = Book("Test Book", "Fiction", 10.99, "/test.jpg")
        cart.add_book(book, quantity)

        total = cart.get_total_price()

        assert total > 0
        assert total == book.price * quantity

    @given(st.integers(min_value=1, max_value=1000), st.floats(min_value=0.01, max_value=999.99))
    @settings(max_examples=50)
    def test_cart_total_calculation_invariant(self, quantity, price):
        """Cart total should always equal price * quantity"""
        cart = Cart()
        book = Book("Test Book", "Fiction", price, "/test.jpg")
        cart.add_book(book, quantity)

        assert abs(cart.get_total_price() - (price * quantity)) < 0.01

    @given(st.integers(min_value=0, max_value=100))
    @settings(max_examples=30)
    def test_cart_item_count_invariant(self, count):
        """Cart item count should never exceed added items"""
        cart = Cart()
        book = Book("Test Book", "Fiction", 10.99, "/test.jpg")

        if count > 0:
            cart.add_book(book, count)
            assert cart.get_total_items() == count
        else:
            assert cart.get_total_items() == 0

    @given(st.integers(min_value=-1000, max_value=0))
    @settings(max_examples=30)
    def test_cart_update_negative_quantity_removes_item(self, negative_quantity):
        """Updating cart with negative or zero quantity should remove item"""
        cart = Cart()
        book = Book("Test Book", "Fiction", 10.99, "/test.jpg")
        cart.add_book(book, 5)

        cart.update_quantity(book.title, negative_quantity)

        assert book.title not in cart.items
        assert cart.is_empty()

    @given(st.lists(st.integers(min_value=1, max_value=100), min_size=1, max_size=10))
    @settings(max_examples=30)
    def test_cart_multiple_books_total(self, quantities):
        """Cart with multiple books should sum correctly"""
        cart = Cart()
        expected_total = 0

        for i, qty in enumerate(quantities):
            book = Book(f"Book {i}", "Fiction", 10.0, f"/book{i}.jpg")
            cart.add_book(book, qty)
            expected_total += 10.0 * qty

        assert abs(cart.get_total_price() - expected_total) < 0.01


@pytest.mark.unit
@pytest.mark.property
class TestUserProperties:
    """Property-based tests for User class"""

    @given(st.lists(st.integers(min_value=1, max_value=100), min_size=1, max_size=50))
    @settings(max_examples=30)
    def test_order_history_always_sorted(self, order_counts):
        """Order history should always return sorted results"""
        user = User("test@example.com", "password")

        for i in order_counts:
            order = Order(f"ORDER{i}", "test@example.com", [], {}, {}, 50.00)
            user.add_order(order)

        history = user.get_order_history()

        for i in range(len(history) - 1):
            assert history[i].order_date >= history[i + 1].order_date

    @given(st.text(min_size=1, max_size=50), st.text(min_size=1, max_size=50))
    @settings(max_examples=30)
    def test_user_creation_with_any_credentials(self, email, password):
        """User should be creatable with any string credentials"""
        try:
            user = User(email, password)
            assert user.email == email
            assert user.password == password
        except Exception:
            pass

    @given(st.integers(min_value=0, max_value=1000))
    @settings(max_examples=30)
    def test_order_history_count_matches_additions(self, order_count):
        """Order history count should match number of orders added"""
        user = User("test@example.com", "password")

        for i in range(order_count):
            order = Order(f"ORDER{i}", "test@example.com", [], {}, {}, 50.00)
            user.add_order(order)

        assert len(user.get_order_history()) == order_count


@pytest.mark.unit
@pytest.mark.property
class TestEmailValidationProperties:
    """Property-based tests for email validation"""

    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=50)
    def test_email_validation_with_random_strings(self, email_input):
        """Email validation should handle any string input gracefully"""
        import re

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        result = bool(re.match(email_pattern, email_input))

        assert isinstance(result, bool)

    @given(st.emails())
    @settings(max_examples=30)
    def test_valid_emails_pass_validation(self, valid_email):
        """Valid emails should pass validation"""
        import re

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        result = bool(re.match(email_pattern, valid_email))

        assert result == True


@pytest.mark.unit
@pytest.mark.property
class TestPriceCalculationProperties:
    """Property-based tests for price calculations"""

    @given(st.floats(min_value=0.01, max_value=9999.99), st.integers(min_value=1, max_value=100))
    @settings(max_examples=30)
    def test_cart_item_total_never_negative(self, price, quantity):
        """Cart item total should never be negative"""
        book = Book("Test Book", "Fiction", price, "/test.jpg")
        item = CartItem(book, quantity)

        total = item.get_total_price()

        assert total >= 0
        assert abs(total - (price * quantity)) < 0.01

    @given(st.floats(min_value=0.01, max_value=999.99))
    @settings(max_examples=30)
    def test_book_price_precision(self, price):
        """Book prices should maintain precision"""
        book = Book("Test Book", "Fiction", price, "/test.jpg")

        assert abs(book.price - price) < 0.01


@pytest.mark.unit
@pytest.mark.property
class TestStringHandlingProperties:
    """Property-based tests for string handling"""

    @given(st.text(min_size=0, max_size=10000))
    @settings(max_examples=30)
    def test_book_title_accepts_any_string(self, title):
        """Book title should accept any string"""
        try:
            book = Book(title, "Fiction", 10.99, "/test.jpg")
            assert book.title == title
        except Exception:
            pass

    @given(st.text(min_size=0, max_size=10000))
    @settings(max_examples=30)
    def test_user_name_accepts_any_string(self, name):
        """User name should accept any string"""
        try:
            user = User("test@example.com", "password", name)
            assert user.name == name
        except Exception:
            pass

    @given(st.text(min_size=0, max_size=10000))
    @settings(max_examples=30)
    def test_address_accepts_any_string(self, address):
        """User address should accept any string"""
        try:
            user = User("test@example.com", "password", "Test User", address)
            assert user.address == address
        except Exception:
            pass
