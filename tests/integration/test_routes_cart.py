import pytest
from app import cart


@pytest.mark.integration
class TestCartRoutes:
    """Integration tests for cart-related routes"""

    def test_view_cart_page(self, client):
        """Test viewing the cart page"""
        response = client.get('/cart')

        assert response.status_code == 200
        assert b'cart' in response.data.lower()

    def test_add_to_cart_valid_book(self, client):
        """Test adding a valid book to cart"""
        response = client.post('/add-to-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '2'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Added' in response.data
        assert cart.get_total_items() == 2

    def test_add_to_cart_default_quantity(self, client):
        """Test adding book with default quantity of 1"""
        response = client.post('/add-to-cart', data={
            'title': '1984'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert cart.get_total_items() == 1

    @pytest.mark.bug
    def test_add_to_cart_non_numeric_quantity(self, client):
        """BUG #2: Test adding book with non-numeric quantity crashes"""
        # This should handle the error gracefully, but will crash
        with pytest.raises(ValueError):
            client.post('/add-to-cart', data={
                'title': 'The Great Gatsby',
                'quantity': 'abc'
            })

    @pytest.mark.bug
    def test_add_to_cart_empty_quantity(self, client):
        """BUG #2: Test adding book with empty quantity string crashes"""
        # Empty string will be caught by default value, but '' still causes issues
        with pytest.raises(ValueError):
            client.post('/add-to-cart', data={
                'title': 'The Great Gatsby',
                'quantity': ''
            })

    def test_add_to_cart_nonexistent_book(self, client):
        """Test adding a book that doesn't exist"""
        response = client.post('/add-to-cart', data={
            'title': 'Nonexistent Book',
            'quantity': '1'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'not found' in response.data.lower()

    def test_add_same_book_multiple_times(self, client):
        """Test adding the same book multiple times"""
        client.post('/add-to-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '2'
        })
        client.post('/add-to-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '3'
        })

        assert cart.get_total_items() == 5

    def test_update_cart_valid_quantity(self, client):
        """Test updating cart quantity to valid number"""
        # First add a book
        client.post('/add-to-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '2'
        })

        # Then update quantity
        response = client.post('/update-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '5'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Updated' in response.data
        assert cart.get_total_items() == 5

    @pytest.mark.bug
    def test_update_cart_to_zero(self, client):
        """BUG #1: Test updating cart quantity to zero should remove item"""
        # Add a book first
        client.post('/add-to-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '3'
        })

        # Update to zero should remove it
        response = client.post('/update-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '0'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Expected: item removed from cart
        # Actual: item remains with quantity 0
        assert cart.is_empty(), "Bug: Item not removed when quantity updated to 0"

    @pytest.mark.bug
    def test_update_cart_to_negative(self, client):
        """BUG #1: Test updating cart to negative quantity"""
        client.post('/add-to-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '2'
        })

        response = client.post('/update-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '-1'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should remove item when negative
        assert cart.is_empty(), "Bug: Item not removed when quantity updated to negative"

    @pytest.mark.bug
    def test_update_cart_non_numeric_quantity(self, client):
        """BUG #2: Test updating cart with non-numeric quantity crashes"""
        client.post('/add-to-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '2'
        })

        # This will crash due to int() conversion without try-catch
        with pytest.raises(ValueError):
            client.post('/update-cart', data={
                'title': 'The Great Gatsby',
                'quantity': 'invalid'
            })

    def test_remove_from_cart(self, client):
        """Test removing a book from cart"""
        # Add a book first
        client.post('/add-to-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '2'
        })

        # Remove it
        response = client.post('/remove-from-cart', data={
            'title': 'The Great Gatsby'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Removed' in response.data
        assert cart.is_empty()

    def test_remove_nonexistent_book_from_cart(self, client):
        """Test removing a book that isn't in cart"""
        response = client.post('/remove-from-cart', data={
            'title': 'Nonexistent Book'
        }, follow_redirects=True)

        assert response.status_code == 200

    def test_clear_cart(self, client):
        """Test clearing entire cart"""
        # Add multiple books
        client.post('/add-to-cart', data={'title': 'The Great Gatsby', 'quantity': '2'})
        client.post('/add-to-cart', data={'title': '1984', 'quantity': '1'})

        # Clear cart
        response = client.post('/clear-cart', follow_redirects=True)

        assert response.status_code == 200
        assert b'cleared' in response.data.lower()
        assert cart.is_empty()

    def test_cart_operations_sequence(self, client):
        """Test a sequence of cart operations"""
        # Add item
        client.post('/add-to-cart', data={'title': 'The Great Gatsby', 'quantity': '3'})
        assert cart.get_total_items() == 3

        # Update quantity
        client.post('/update-cart', data={'title': 'The Great Gatsby', 'quantity': '5'})
        assert cart.get_total_items() == 5

        # Add another book
        client.post('/add-to-cart', data={'title': '1984', 'quantity': '2'})
        assert cart.get_total_items() == 7

        # Remove one book
        client.post('/remove-from-cart', data={'title': '1984'})
        assert cart.get_total_items() == 5

        # Clear all
        client.post('/clear-cart')
        assert cart.is_empty()
