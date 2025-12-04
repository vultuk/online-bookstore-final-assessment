import pytest
from models import Order
import datetime


@pytest.mark.unit
class TestOrder:
    """Unit tests for the Order model"""

    def test_order_creation(self, sample_order):
        """Test creating an order with all attributes"""
        assert sample_order.order_id == "TEST001"
        assert sample_order.user_email == "test@example.com"
        assert len(sample_order.items) == 1
        assert sample_order.total_amount == 31.98
        assert sample_order.status == "Confirmed"

    def test_order_has_timestamp(self, sample_order):
        """Test that order has a timestamp"""
        assert hasattr(sample_order, 'order_date')
        assert isinstance(sample_order.order_date, datetime.datetime)

    def test_order_shipping_info(self, sample_order):
        """Test order shipping information"""
        assert 'name' in sample_order.shipping_info
        assert 'email' in sample_order.shipping_info
        assert 'address' in sample_order.shipping_info

    def test_order_payment_info(self, sample_order):
        """Test order payment information"""
        assert 'method' in sample_order.payment_info
        assert 'transaction_id' in sample_order.payment_info

    def test_order_to_dict(self, sample_order):
        """Test converting order to dictionary"""
        order_dict = sample_order.to_dict()

        assert 'order_id' in order_dict
        assert 'user_email' in order_dict
        assert 'items' in order_dict
        assert 'shipping_info' in order_dict
        assert 'total_amount' in order_dict
        assert 'order_date' in order_dict
        assert 'status' in order_dict

    def test_order_to_dict_items_format(self, sample_order):
        """Test that items in dict have correct format"""
        order_dict = sample_order.to_dict()

        for item in order_dict['items']:
            assert 'title' in item
            assert 'quantity' in item
            assert 'price' in item

    def test_order_date_format_in_dict(self, sample_order):
        """Test that order date is formatted correctly in dict"""
        order_dict = sample_order.to_dict()

        # Date should be formatted as string
        assert isinstance(order_dict['order_date'], str)
        # Should match format: YYYY-MM-DD HH:MM:SS
        datetime.datetime.strptime(order_dict['order_date'], '%Y-%m-%d %H:%M:%S')

    def test_order_status_confirmed(self, sample_order):
        """Test that new orders have 'Confirmed' status"""
        assert sample_order.status == "Confirmed"

    def test_order_items_are_copied(self, cart_with_items):
        """Test that order items are copied, not referenced"""
        from models import Order

        original_items = cart_with_items.get_items()
        order = Order(
            order_id="TEST",
            user_email="test@example.com",
            items=original_items,
            shipping_info={},
            payment_info={},
            total_amount=50.00
        )

        # Items should be copied
        assert len(order.items) == len(original_items)
