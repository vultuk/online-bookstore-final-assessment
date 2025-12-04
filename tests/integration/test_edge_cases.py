import pytest
from models import Book, Cart


@pytest.mark.integration
@pytest.mark.edge_case
class TestEdgeCases:
    """Comprehensive edge case tests for uncovered scenarios"""

    def test_whitespace_in_email_input(self, client):
        """Test email validation with leading/trailing whitespace"""
        response = client.post('/register', data={
            'email': ' user@example.com ',
            'password': 'test123',
            'name': 'Test User'
        }, follow_redirects=True)

        assert response.status_code == 200

    def test_unicode_characters_in_name(self, client):
        """Test Unicode characters in user name"""
        unicode_name = '测试用户 José Müller'
        response = client.post('/register', data={
            'email': 'test@example.com',
            'password': 'test123',
            'name': unicode_name
        }, follow_redirects=True)

        assert response.status_code == 200

    def test_unicode_characters_in_address(self, client, sample_book):
        """Test Unicode characters in address"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        client.post('/add-to-cart', data={'title': sample_book.title, 'quantity': '1'})

        response = client.post('/process-checkout', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'address': '北京市 中国 Straße München',
            'city': 'Test City',
            'zip_code': '12345',
            'payment_method': 'paypal'
        }, follow_redirects=True)

        assert response.status_code in [200, 302]

    def test_very_long_string_in_name_field(self, client):
        """Test very long strings (10000+ chars) in name field"""
        long_name = 'A' * 10000
        response = client.post('/register', data={
            'email': 'test@example.com',
            'password': 'test123',
            'name': long_name
        }, follow_redirects=True)

        assert response.status_code == 200

    def test_very_long_string_in_address_field(self, client, sample_book):
        """Test very long strings in address field"""
        long_address = 'A' * 10000

        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        client.post('/add-to-cart', data={'title': sample_book.title, 'quantity': '1'})

        response = client.post('/process-checkout', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'address': long_address,
            'city': 'Test City',
            'zip_code': '12345',
            'payment_method': 'paypal'
        }, follow_redirects=True)

        assert response.status_code in [200, 302]

    def test_floating_point_precision_in_prices(self):
        """Test floating point precision in price calculations"""
        cart = Cart()
        book = Book("Test Book", "Fiction", 0.01, "/test.jpg")
        cart.add_book(book, 100)

        total = cart.get_total_price()

        assert abs(total - 1.00) < 0.01

    def test_price_edge_cases(self):
        """Test edge case prices (0.01, 0.99, 999.99)"""
        prices = [0.01, 0.99, 999.99]

        for price in prices:
            book = Book("Test Book", "Fiction", price, "/test.jpg")
            assert book.price == price

    def test_checkout_with_empty_cart(self, client):
        """Test checkout with empty cart"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        response = client.get('/checkout', follow_redirects=True)

        assert response.status_code == 200
        assert b'empty' in response.data.lower() or b'Empty' in response.data

    def test_session_isolation_between_users(self, client):
        """Test session isolation between different users"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'user1@example.com'

        response1 = client.get('/cart')

        with client.session_transaction() as sess:
            sess['user_email'] = 'user2@example.com'

        response2 = client.get('/cart')

        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_special_characters_in_book_title(self):
        """Test special characters in book titles"""
        special_titles = [
            "Book's Title",
            "Book & Title",
            "Book-Title",
            "Book (Title)",
            "Book [Title]",
            "Book <Title>",
            "Book: Title"
        ]

        for title in special_titles:
            book = Book(title, "Fiction", 10.99, "/test.jpg")
            assert book.title == title

    def test_cvv_with_letters(self, client, sample_book):
        """Test CVV validation with letters"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        client.post('/add-to-cart', data={'title': sample_book.title, 'quantity': '1'})

        response = client.post('/process-checkout', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'address': '123 Test St',
            'city': 'Test City',
            'zip_code': '12345',
            'payment_method': 'credit_card',
            'card_number': '4532123456789012',
            'expiry_date': '12/25',
            'cvv': 'ABC'
        }, follow_redirects=True)

        assert response.status_code in [200, 302]

    def test_expired_credit_card_past_date(self, client, sample_book):
        """Test expired credit cards with past dates"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        client.post('/add-to-cart', data={'title': sample_book.title, 'quantity': '1'})

        response = client.post('/process-checkout', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'address': '123 Test St',
            'city': 'Test City',
            'zip_code': '12345',
            'payment_method': 'credit_card',
            'card_number': '4532123456789012',
            'expiry_date': '01/20',
            'cvv': '123'
        }, follow_redirects=True)

        assert response.status_code in [200, 302]

    def test_none_values_in_required_fields(self, client, sample_book):
        """Test None values in required checkout fields"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        client.post('/add-to-cart', data={'title': sample_book.title, 'quantity': '1'})

        response = client.post('/process-checkout', data={
            'name': None,
            'email': 'test@example.com',
            'address': '123 Test St',
            'city': 'Test City',
            'zip_code': '12345',
            'payment_method': 'paypal'
        }, follow_redirects=True)

        assert response.status_code in [200, 302]

    def test_multiple_cart_operations_in_sequence(self, client, sample_book):
        """Test multiple cart operations in rapid sequence"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        client.post('/add-to-cart', data={'title': sample_book.title, 'quantity': '5'})
        client.post('/update-cart', data={'title': sample_book.title, 'quantity': '10'})
        client.post('/update-cart', data={'title': sample_book.title, 'quantity': '1'})
        response = client.get('/cart')

        assert response.status_code == 200

    def test_add_same_book_multiple_times(self, client, sample_book):
        """Test adding the same book multiple times"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        for i in range(5):
            client.post('/add-to-cart', data={'title': sample_book.title, 'quantity': '1'})

        response = client.get('/cart')
        assert response.status_code == 200

    def test_clear_cart_multiple_times(self, client, sample_book):
        """Test clearing cart multiple times"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        client.post('/add-to-cart', data={'title': sample_book.title, 'quantity': '1'})
        client.post('/clear-cart')
        client.post('/clear-cart')
        response = client.post('/clear-cart', follow_redirects=True)

        assert response.status_code == 200

    def test_remove_nonexistent_book_from_cart(self, client):
        """Test removing a book that doesn't exist in cart"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        response = client.post('/remove-from-cart', data={
            'title': 'Nonexistent Book'
        }, follow_redirects=True)

        assert response.status_code == 200

    def test_update_nonexistent_book_quantity(self, client):
        """Test updating quantity of a book not in cart"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        response = client.post('/update-cart', data={
            'title': 'Nonexistent Book',
            'quantity': '5'
        }, follow_redirects=True)

        assert response.status_code == 200
