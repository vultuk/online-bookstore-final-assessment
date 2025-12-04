import pytest
from models import Book, Cart, CartItem


@pytest.mark.unit
class TestCart:
    """Unit tests for the Cart model"""

    def test_cart_initialization(self, empty_cart):
        """Test creating an empty cart"""
        assert empty_cart.is_empty()
        assert len(empty_cart.items) == 0

    def test_add_book_to_empty_cart(self, empty_cart, sample_book):
        """Test adding a book to an empty cart"""
        empty_cart.add_book(sample_book, 1)

        assert not empty_cart.is_empty()
        assert sample_book.title in empty_cart.items
        assert empty_cart.items[sample_book.title].quantity == 1

    def test_add_book_with_multiple_quantity(self, empty_cart, sample_book):
        """Test adding multiple quantities of a book"""
        empty_cart.add_book(sample_book, 5)

        assert empty_cart.items[sample_book.title].quantity == 5

    def test_add_same_book_multiple_times(self, empty_cart, sample_book):
        """Test adding the same book multiple times increments quantity"""
        empty_cart.add_book(sample_book, 2)
        empty_cart.add_book(sample_book, 3)

        assert empty_cart.items[sample_book.title].quantity == 5

    def test_remove_book_from_cart(self, empty_cart, sample_book):
        """Test removing a book from cart"""
        empty_cart.add_book(sample_book, 2)
        empty_cart.remove_book(sample_book.title)

        assert sample_book.title not in empty_cart.items
        assert empty_cart.is_empty()

    def test_remove_nonexistent_book(self, empty_cart):
        """Test removing a book that doesn't exist"""
        # Should not raise an error
        empty_cart.remove_book("Nonexistent Book")
        assert empty_cart.is_empty()

    @pytest.mark.bug
    def test_update_quantity_to_zero(self, empty_cart, sample_book):
        """BUG #1: Test updating quantity to zero should remove item"""
        empty_cart.add_book(sample_book, 5)
        empty_cart.update_quantity(sample_book.title, 0)

        # Expected: item should be removed from cart
        # Actual: item remains with quantity 0
        assert sample_book.title not in empty_cart.items, "Bug: Item not removed when quantity set to 0"

    @pytest.mark.bug
    def test_update_quantity_to_negative(self, empty_cart, sample_book):
        """BUG #1: Test updating quantity to negative should remove item"""
        empty_cart.add_book(sample_book, 3)
        empty_cart.update_quantity(sample_book.title, -1)

        # Expected: item should be removed from cart
        # Actual: item remains with negative quantity
        assert sample_book.title not in empty_cart.items, "Bug: Item not removed when quantity set to negative"

    def test_update_quantity_valid(self, empty_cart, sample_book):
        """Test updating quantity to a valid positive number"""
        empty_cart.add_book(sample_book, 2)
        empty_cart.update_quantity(sample_book.title, 10)

        assert empty_cart.items[sample_book.title].quantity == 10

    def test_get_total_items(self, empty_cart, sample_book):
        """Test getting total number of items in cart"""
        book2 = Book("Another Book", "Fiction", 12.99, "/test2.jpg")

        empty_cart.add_book(sample_book, 3)
        empty_cart.add_book(book2, 2)

        assert empty_cart.get_total_items() == 5

    def test_get_total_items_empty_cart(self, empty_cart):
        """Test total items for empty cart"""
        assert empty_cart.get_total_items() == 0

    @pytest.mark.performance
    @pytest.mark.bug
    def test_get_total_price(self, empty_cart):
        """BUG #6: Test total price calculation (documents O(n*m) inefficiency)"""
        # Create books with different prices
        book1 = Book("Book 1", "Fiction", 10.00, "/test1.jpg")
        book2 = Book("Book 2", "Fiction", 15.50, "/test2.jpg")
        book3 = Book("Book 3", "Fiction", 8.99, "/test3.jpg")

        empty_cart.add_book(book1, 2)
        empty_cart.add_book(book2, 3)
        empty_cart.add_book(book3, 1)

        # Expected: 10.00*2 + 15.50*3 + 8.99*1 = 20.00 + 46.50 + 8.99 = 75.49
        expected_total = 75.49
        actual_total = empty_cart.get_total_price()

        assert abs(actual_total - expected_total) < 0.01

    @pytest.mark.performance
    def test_get_total_price_large_quantities(self, empty_cart, sample_book):
        """Test total price with large quantities (exposes performance issue)"""
        # This test will be slow due to O(n*m) implementation
        empty_cart.add_book(sample_book, 1000)

        expected_total = sample_book.price * 1000
        actual_total = empty_cart.get_total_price()

        assert abs(actual_total - expected_total) < 0.01

    def test_clear_cart(self, empty_cart, sample_book):
        """Test clearing all items from cart"""
        empty_cart.add_book(sample_book, 5)
        empty_cart.clear()

        assert empty_cart.is_empty()
        assert len(empty_cart.items) == 0

    def test_get_items(self, empty_cart, sample_book):
        """Test getting list of cart items"""
        book2 = Book("Another Book", "Fiction", 12.99, "/test2.jpg")

        empty_cart.add_book(sample_book, 2)
        empty_cart.add_book(book2, 1)

        items = empty_cart.get_items()

        assert len(items) == 2
        assert all(isinstance(item, CartItem) for item in items)

    def test_is_empty_with_items(self, cart_with_items):
        """Test is_empty returns False when cart has items"""
        assert not cart_with_items.is_empty()

    def test_multiple_operations_sequence(self, empty_cart, sample_book):
        """Test a sequence of cart operations"""
        # Add item
        empty_cart.add_book(sample_book, 3)
        assert empty_cart.get_total_items() == 3

        # Update quantity
        empty_cart.update_quantity(sample_book.title, 5)
        assert empty_cart.get_total_items() == 5

        # Add more
        empty_cart.add_book(sample_book, 2)
        assert empty_cart.get_total_items() == 7

        # Remove
        empty_cart.remove_book(sample_book.title)
        assert empty_cart.is_empty()
