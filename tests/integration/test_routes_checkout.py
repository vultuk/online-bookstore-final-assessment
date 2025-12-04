import pytest
from app import cart, orders


@pytest.mark.integration
class TestCheckoutRoutes:
    """Integration tests for checkout-related routes"""

    def test_checkout_page_with_items(self, client):
        """Test accessing checkout page with items in cart"""
        # Add item to cart first
        client.post('/add-to-cart', data={'title': 'The Great Gatsby', 'quantity': '1'})

        response = client.get('/checkout')

        assert response.status_code == 200
        assert b'checkout' in response.data.lower()

    def test_checkout_page_empty_cart_redirects(self, client):
        """Test that checkout with empty cart redirects"""
        response = client.get('/checkout', follow_redirects=True)

        assert response.status_code == 200
        assert b'empty' in response.data.lower()

    def test_process_checkout_valid_data(self, client, valid_checkout_form):
        """Test processing checkout with valid data"""
        # Add item to cart
        client.post('/add-to-cart', data={'title': 'The Great Gatsby', 'quantity': '1'})

        response = client.post('/process-checkout', data=valid_checkout_form, follow_redirects=True)

        assert response.status_code == 200
        assert b'successful' in response.data.lower() or b'confirmed' in response.data.lower()

    def test_process_checkout_creates_order(self, client, valid_checkout_form):
        """Test that checkout creates an order"""
        client.post('/add-to-cart', data={'title': 'The Great Gatsby', 'quantity': '1'})

        initial_order_count = len(orders)
        client.post('/process-checkout', data=valid_checkout_form, follow_redirects=True)

        assert len(orders) == initial_order_count + 1

    def test_process_checkout_clears_cart(self, client, valid_checkout_form):
        """Test that successful checkout clears the cart"""
        client.post('/add-to-cart', data={'title': 'The Great Gatsby', 'quantity': '2'})

        client.post('/process-checkout', data=valid_checkout_form, follow_redirects=True)

        assert cart.is_empty()

    def test_checkout_with_save10_discount(self, client, valid_checkout_form):
        """Test checkout with SAVE10 discount code (10% off)"""
        client.post('/add-to-cart', data={'title': 'The Great Gatsby', 'quantity': '1'})

        valid_checkout_form['discount_code'] = 'SAVE10'
        response = client.post('/process-checkout', data=valid_checkout_form, follow_redirects=True)

        assert response.status_code == 200
        assert b'saved' in response.data.lower() or b'discount' in response.data.lower()

    def test_checkout_with_welcome20_discount(self, client, valid_checkout_form):
        """Test checkout with WELCOME20 discount code (20% off)"""
        client.post('/add-to-cart', data={'title': 'The Great Gatsby', 'quantity': '1'})

        valid_checkout_form['discount_code'] = 'WELCOME20'
        response = client.post('/process-checkout', data=valid_checkout_form, follow_redirects=True)

        assert response.status_code == 200
        assert b'saved' in response.data.lower() or b'discount' in response.data.lower()

    @pytest.mark.bug
    def test_checkout_discount_case_insensitive(self, client, valid_checkout_form):
        """BUG #3: Test that discount codes should be case-insensitive"""
        client.post('/add-to-cart', data={'title': 'The Great Gatsby', 'quantity': '1'})

        # Lowercase version should work
        valid_checkout_form['discount_code'] = 'save10'
        response = client.post('/process-checkout', data=valid_checkout_form, follow_redirects=True)

        # Expected: discount should be applied
        # Actual: discount is case-sensitive and won't be applied
        assert b'saved' in response.data.lower() or b'discount' in response.data.lower(), \
            "Bug: Discount codes are case-sensitive"

    @pytest.mark.bug
    def test_checkout_discount_mixed_case(self, client, valid_checkout_form):
        """BUG #3: Test discount codes with mixed case"""
        client.post('/add-to-cart', data={'title': 'The Great Gatsby', 'quantity': '1'})

        valid_checkout_form['discount_code'] = 'WeLcOmE20'
        response = client.post('/process-checkout', data=valid_checkout_form, follow_redirects=True)

        # Should apply discount but won't due to case sensitivity
        assert b'saved' in response.data.lower() or b'discount' in response.data.lower(), \
            "Bug: Discount codes are case-sensitive"

    def test_checkout_invalid_discount_code(self, client, valid_checkout_form):
        """Test checkout with invalid discount code"""
        client.post('/add-to-cart', data={'title': 'The Great Gatsby', 'quantity': '1'})

        valid_checkout_form['discount_code'] = 'INVALID123'
        response = client.post('/process-checkout', data=valid_checkout_form, follow_redirects=True)

        assert response.status_code == 200
        assert b'invalid' in response.data.lower()

    def test_checkout_missing_required_fields(self, client):
        """Test checkout with missing required fields"""
        client.post('/add-to-cart', data={'title': 'The Great Gatsby', 'quantity': '1'})

        response = client.post('/process-checkout', data={
            'name': 'John Doe',
            # Missing other required fields
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should show error about missing fields

    def test_checkout_missing_name(self, client, valid_checkout_form):
        """Test checkout with missing name field"""
        client.post('/add-to-cart', data={'title': 'The Great Gatsby', 'quantity': '1'})

        valid_checkout_form['name'] = ''
        response = client.post('/process-checkout', data=valid_checkout_form, follow_redirects=True)

        assert response.status_code == 200
        assert b'name' in response.data.lower()

    def test_checkout_payment_failure(self, client, valid_checkout_form, failing_payment_card):
        """Test checkout with payment failure (card ending in 1111)"""
        client.post('/add-to-cart', data={'title': 'The Great Gatsby', 'quantity': '1'})

        # Use failing card
        valid_checkout_form.update(failing_payment_card)
        response = client.post('/process-checkout', data=valid_checkout_form, follow_redirects=True)

        assert response.status_code == 200
        assert b'failed' in response.data.lower() or b'invalid' in response.data.lower()

    def test_checkout_paypal_payment(self, client, valid_checkout_form):
        """Test checkout with PayPal payment method"""
        client.post('/add-to-cart', data={'title': 'The Great Gatsby', 'quantity': '1'})

        valid_checkout_form['payment_method'] = 'paypal'
        # PayPal doesn't need card details
        valid_checkout_form['card_number'] = ''
        valid_checkout_form['expiry_date'] = ''
        valid_checkout_form['cvv'] = ''

        response = client.post('/process-checkout', data=valid_checkout_form, follow_redirects=True)

        assert response.status_code == 200

    def test_checkout_empty_cart_redirects(self, client, valid_checkout_form):
        """Test that checkout with empty cart redirects"""
        response = client.post('/process-checkout', data=valid_checkout_form, follow_redirects=True)

        assert response.status_code == 200
        assert b'empty' in response.data.lower()

    def test_order_confirmation_page(self, client, valid_checkout_form):
        """Test accessing order confirmation page after checkout"""
        client.post('/add-to-cart', data={'title': 'The Great Gatsby', 'quantity': '1'})

        response = client.post('/process-checkout', data=valid_checkout_form, follow_redirects=True)

        assert response.status_code == 200
        assert b'order' in response.data.lower()
        assert b'confirmation' in response.data.lower() or b'confirmed' in response.data.lower()

    def test_order_confirmation_shows_details(self, client, valid_checkout_form):
        """Test that order confirmation shows order details"""
        client.post('/add-to-cart', data={'title': 'The Great Gatsby', 'quantity': '1'})

        response = client.post('/process-checkout', data=valid_checkout_form, follow_redirects=True)

        assert b'The Great Gatsby' in response.data
        # Should show order ID and other details
