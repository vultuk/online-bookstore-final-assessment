import pytest
import time
from models import Book, Cart, User, Order


@pytest.mark.performance
@pytest.mark.sla
class TestPerformanceSLA:
    """Performance tests with SLA assertions to ensure response times"""

    def test_cart_total_performance_sla(self):
        """Cart total calculation must complete under 1ms for 1000 items"""
        cart = Cart()
        book = Book("Test Book", "Fiction", 10.99, "/test.jpg")
        cart.add_book(book, 1000)

        start = time.perf_counter()
        total = cart.get_total_price()
        duration = time.perf_counter() - start

        assert duration < 0.001, f"Cart total took {duration}s, exceeded 1ms SLA"
        assert total > 0

    def test_checkout_response_time_sla(self, client, sample_book):
        """Checkout page must load under 100ms"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        client.post('/add-to-cart', data={'title': sample_book.title, 'quantity': '1'})

        start = time.perf_counter()
        response = client.get('/checkout')
        duration = time.perf_counter() - start

        assert duration < 0.1, f"Checkout took {duration}s, exceeded 100ms SLA"
        assert response.status_code in [200, 302]

    def test_login_response_time_sla(self, client):
        """Login must complete under 200ms"""
        start = time.perf_counter()
        response = client.post('/login', data={
            'email': 'demo@bookstore.com',
            'password': 'demo123'
        })
        duration = time.perf_counter() - start

        assert duration < 0.2, f"Login took {duration}s, exceeded 200ms SLA"
        assert response.status_code in [200, 302]

    def test_order_history_retrieval_sla(self):
        """Order history retrieval must complete under 50ms for 1000 orders"""
        user = User("test@example.com", "password")

        for i in range(1000):
            order = Order(f"ORDER{i}", "test@example.com", [], {}, {}, 50.00)
            user.add_order(order)

        start = time.perf_counter()
        history = user.get_order_history()
        duration = time.perf_counter() - start

        assert duration < 0.05, f"Order history took {duration}s, exceeded 50ms SLA"
        assert len(history) == 1000

    def test_book_search_performance_sla(self):
        """Book search must complete under 10ms"""
        from app import get_book_by_title

        start = time.perf_counter()
        book = get_book_by_title("The Great Gatsby")
        duration = time.perf_counter() - start

        assert duration < 0.01, f"Book search took {duration}s, exceeded 10ms SLA"
        assert book is not None

    def test_cart_update_performance_sla(self, client, sample_book):
        """Cart update must complete under 20ms"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        client.post('/add-to-cart', data={'title': sample_book.title, 'quantity': '5'})

        start = time.perf_counter()
        response = client.post('/update-cart', data={
            'title': sample_book.title,
            'quantity': '10'
        })
        duration = time.perf_counter() - start

        assert duration < 0.02, f"Cart update took {duration}s, exceeded 20ms SLA"
        assert response.status_code in [200, 302]

    def test_payment_processing_sla(self):
        """Payment processing must complete under 500ms (mock)"""
        from models import PaymentGateway

        payment_info = {
            'card_number': '4532123456789012',
            'payment_method': 'credit_card'
        }

        start = time.perf_counter()
        result = PaymentGateway.process_payment(payment_info)
        duration = time.perf_counter() - start

        assert duration < 0.5, f"Payment processing took {duration}s, exceeded 500ms SLA"
        assert result['success'] == True

    def test_order_confirmation_sla(self, client, sample_book):
        """Order confirmation must load under 100ms"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        client.post('/add-to-cart', data={'title': sample_book.title, 'quantity': '1'})

        response = client.post('/process-checkout', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'address': '123 Test St',
            'city': 'Test City',
            'zip_code': '12345',
            'payment_method': 'paypal'
        })

        if response.status_code == 302 and 'order-confirmation' in response.location:
            order_id = response.location.split('/')[-1]

            start = time.perf_counter()
            response = client.get(f'/order-confirmation/{order_id}')
            duration = time.perf_counter() - start

            assert duration < 0.1, f"Order confirmation took {duration}s, exceeded 100ms SLA"
            assert response.status_code == 200

    def test_profile_update_sla(self, client):
        """Profile update must complete under 50ms"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        start = time.perf_counter()
        response = client.post('/update-profile', data={
            'name': 'Updated Name',
            'address': 'Updated Address'
        })
        duration = time.perf_counter() - start

        assert duration < 0.05, f"Profile update took {duration}s, exceeded 50ms SLA"
        assert response.status_code in [200, 302]

    def test_catalog_load_sla(self, client):
        """Catalog page must load under 50ms"""
        start = time.perf_counter()
        response = client.get('/')
        duration = time.perf_counter() - start

        assert duration < 0.05, f"Catalog load took {duration}s, exceeded 50ms SLA"
        assert response.status_code == 200
