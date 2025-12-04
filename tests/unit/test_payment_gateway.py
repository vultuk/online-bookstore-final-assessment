import pytest
from models import PaymentGateway


@pytest.mark.unit
class TestPaymentGateway:
    """Unit tests for the PaymentGateway model"""

    def test_process_payment_success(self, valid_payment_card):
        """Test successful payment processing"""
        result = PaymentGateway.process_payment(valid_payment_card)

        assert result['success'] is True
        assert 'transaction_id' in result
        assert result['transaction_id'] is not None
        assert result['message'] == 'Payment processed successfully'

    def test_process_payment_failing_card(self, failing_payment_card):
        """Test payment failure with card ending in 1111"""
        result = PaymentGateway.process_payment(failing_payment_card)

        assert result['success'] is False
        assert result['transaction_id'] is None
        assert 'Invalid card number' in result['message']

    def test_process_payment_generates_transaction_id(self, valid_payment_card):
        """Test that transaction ID is generated"""
        result = PaymentGateway.process_payment(valid_payment_card)

        assert result['success'] is True
        assert result['transaction_id'].startswith('TXN')
        assert len(result['transaction_id']) == 9  # TXN + 6 digits

    def test_process_payment_different_cards(self):
        """Test processing multiple different cards"""
        card1 = {'card_number': '4532123456789012', 'payment_method': 'credit_card'}
        card2 = {'card_number': '5432123456789012', 'payment_method': 'credit_card'}

        result1 = PaymentGateway.process_payment(card1)
        result2 = PaymentGateway.process_payment(card2)

        assert result1['success'] is True
        assert result2['success'] is True
        # Transaction IDs should be different
        assert result1['transaction_id'] != result2['transaction_id']

    @pytest.mark.bug
    def test_paypal_payment_no_validation(self):
        """BUG #10: Test PayPal payment method has no validation (empty pass statement)"""
        paypal_payment = {
            'payment_method': 'paypal',
            'card_number': '',  # PayPal doesn't need card number
        }

        result = PaymentGateway.process_payment(paypal_payment)

        # No validation occurs for PayPal, just passes through
        # This is a bug: no PayPal-specific validation is done
        assert result['success'] is True

    def test_payment_with_empty_card_number(self):
        """Test payment with empty card number"""
        payment = {
            'payment_method': 'credit_card',
            'card_number': '',
        }

        result = PaymentGateway.process_payment(payment)

        # Empty card number doesn't end in 1111, so it passes
        # This is a validation gap
        assert result['success'] is True

    @pytest.mark.performance
    @pytest.mark.bug
    def test_payment_processing_has_delay(self, valid_payment_card):
        """BUG #10: Test payment processing has unnecessary time.sleep delay"""
        import time

        start_time = time.time()
        PaymentGateway.process_payment(valid_payment_card)
        end_time = time.time()

        elapsed_time = end_time - start_time

        # There's a time.sleep(0.1) in the code (line 139)
        # This is unnecessary in a mock payment gateway
        assert elapsed_time >= 0.1, "Payment processing has artificial delay"

    def test_payment_card_ending_patterns(self):
        """Test various card ending patterns"""
        # Success cases
        assert PaymentGateway.process_payment({'card_number': '1234'})['success'] is True
        assert PaymentGateway.process_payment({'card_number': '9999'})['success'] is True

        # Failure case
        assert PaymentGateway.process_payment({'card_number': '1111'})['success'] is False
        assert PaymentGateway.process_payment({'card_number': '4532111'})['success'] is False

    def test_payment_returns_all_required_fields(self, valid_payment_card):
        """Test that payment result contains all required fields"""
        result = PaymentGateway.process_payment(valid_payment_card)

        assert 'success' in result
        assert 'message' in result
        assert 'transaction_id' in result
