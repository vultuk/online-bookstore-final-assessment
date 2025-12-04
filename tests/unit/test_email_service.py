import pytest
from models import EmailService
from io import StringIO
import sys


@pytest.mark.unit
class TestEmailService:
    """Unit tests for the EmailService model"""

    def test_send_order_confirmation(self, sample_order, capsys):
        """Test sending order confirmation email"""
        result = EmailService.send_order_confirmation("test@example.com", sample_order)

        assert result is True

        # Check that email was printed to console
        captured = capsys.readouterr()
        assert "EMAIL SENT" in captured.out
        assert "test@example.com" in captured.out
        assert sample_order.order_id in captured.out

    def test_email_contains_order_details(self, sample_order, capsys):
        """Test that email contains order details"""
        EmailService.send_order_confirmation("customer@example.com", sample_order)

        captured = capsys.readouterr()
        assert "Order Confirmation" in captured.out
        assert f"Order #{sample_order.order_id}" in captured.out
        assert f"${sample_order.total_amount:.2f}" in captured.out

    def test_email_contains_items(self, sample_order, capsys):
        """Test that email contains order items"""
        EmailService.send_order_confirmation("customer@example.com", sample_order)

        captured = capsys.readouterr()
        assert "Items:" in captured.out

        # Check each item is listed
        for item in sample_order.items:
            assert item.book.title in captured.out

    def test_email_contains_shipping_address(self, sample_order, capsys):
        """Test that email contains shipping address"""
        EmailService.send_order_confirmation("customer@example.com", sample_order)

        captured = capsys.readouterr()
        assert "Shipping Address:" in captured.out
        assert sample_order.shipping_info.get('address', '') in captured.out

    def test_email_service_returns_true(self, sample_order):
        """Test that email service returns True on success"""
        result = EmailService.send_order_confirmation("test@example.com", sample_order)

        assert result is True

    def test_email_with_multiple_items(self, capsys):
        """Test email with order containing multiple items"""
        from models import Order, Book, CartItem

        book1 = Book("Book 1", "Fiction", 10.00, "/test1.jpg")
        book2 = Book("Book 2", "Fiction", 15.00, "/test2.jpg")

        items = [CartItem(book1, 2), CartItem(book2, 1)]

        order = Order(
            order_id="MULTI001",
            user_email="test@example.com",
            items=items,
            shipping_info={'address': '123 Main St'},
            payment_info={},
            total_amount=35.00
        )

        EmailService.send_order_confirmation("test@example.com", order)

        captured = capsys.readouterr()
        assert "Book 1" in captured.out
        assert "Book 2" in captured.out
        assert "x2" in captured.out
        assert "x1" in captured.out
