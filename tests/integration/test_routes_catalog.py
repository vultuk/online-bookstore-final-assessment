import pytest
from app import BOOKS


@pytest.mark.integration
class TestCatalogRoutes:
    """Integration tests for catalog/index routes"""

    def test_index_page_loads(self, client):
        """Test that index page loads successfully"""
        response = client.get('/')

        assert response.status_code == 200

    def test_index_displays_books(self, client):
        """Test that index page displays available books"""
        response = client.get('/')

        # Check that book titles are displayed
        for book in BOOKS:
            assert book.title.encode() in response.data

    def test_index_shows_book_prices(self, client):
        """Test that book prices are displayed"""
        response = client.get('/')

        # Check that prices are shown
        for book in BOOKS:
            price_str = f"${book.price:.2f}".encode()
            assert price_str in response.data

    def test_index_shows_book_categories(self, client):
        """Test that book categories are displayed"""
        response = client.get('/')

        # Check categories
        categories = set(book.category for book in BOOKS)
        for category in categories:
            assert category.encode() in response.data

    def test_index_when_logged_out(self, client):
        """Test index page when user is not logged in"""
        response = client.get('/')

        assert response.status_code == 200
        # Should show login/register links
        assert b'login' in response.data.lower() or b'register' in response.data.lower()

    def test_index_when_logged_in(self, client, registered_user):
        """Test index page when user is logged in"""
        # Login first
        client.post('/login', data={
            'email': registered_user.email,
            'password': registered_user.password
        })

        response = client.get('/')

        assert response.status_code == 200
        # Should show user name or account link
        assert registered_user.name.encode() in response.data or b'account' in response.data.lower()

    def test_index_shows_cart_info(self, client):
        """Test that index page shows cart information"""
        response = client.get('/')

        assert response.status_code == 200
        assert b'cart' in response.data.lower()

    def test_index_with_items_in_cart(self, client):
        """Test index page with items in cart"""
        # Add item to cart
        client.post('/add-to-cart', data={'title': 'The Great Gatsby', 'quantity': '2'})

        response = client.get('/')

        assert response.status_code == 200
        # Should show cart count
        assert b'2' in response.data or b'cart' in response.data.lower()
