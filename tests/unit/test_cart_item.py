import pytest
from models import Book, CartItem


@pytest.mark.unit
class TestCartItem:
    """Unit tests for the CartItem model"""

    def test_cart_item_creation(self, sample_book):
        """Test creating a cart item with a book"""
        cart_item = CartItem(sample_book, quantity=3)

        assert cart_item.book == sample_book
        assert cart_item.quantity == 3

    def test_cart_item_default_quantity(self, sample_book):
        """Test cart item with default quantity of 1"""
        cart_item = CartItem(sample_book)

        assert cart_item.quantity == 1

    def test_cart_item_get_total_price(self, sample_book):
        """Test calculating total price for a cart item"""
        cart_item = CartItem(sample_book, quantity=2)

        expected_total = sample_book.price * 2
        assert cart_item.get_total_price() == expected_total

    def test_cart_item_total_price_single_quantity(self, sample_book):
        """Test total price with quantity of 1"""
        cart_item = CartItem(sample_book, quantity=1)

        assert cart_item.get_total_price() == sample_book.price

    def test_cart_item_total_price_large_quantity(self):
        """Test total price with large quantity"""
        book = Book("Expensive Book", "Premium", 99.99, "/test.jpg")
        cart_item = CartItem(book, quantity=10)

        assert cart_item.get_total_price() == 999.90
