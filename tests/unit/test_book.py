import pytest
from models import Book


@pytest.mark.unit
class TestBook:
    """Unit tests for the Book model"""

    def test_book_creation(self):
        """Test creating a book with all attributes"""
        book = Book("The Great Gatsby", "Fiction", 10.99, "/images/gatsby.jpg")

        assert book.title == "The Great Gatsby"
        assert book.category == "Fiction"
        assert book.price == 10.99
        assert book.image == "/images/gatsby.jpg"

    def test_book_with_different_types(self):
        """Test book creation with different data types"""
        book = Book("1984", "Dystopia", 8.99, "/images/1984.jpg")

        assert isinstance(book.title, str)
        assert isinstance(book.category, str)
        assert isinstance(book.price, float)
        assert isinstance(book.image, str)

    def test_book_price_is_positive(self):
        """Test that book price is a positive number"""
        book = Book("Test Book", "Test", 15.50, "/test.jpg")

        assert book.price > 0
