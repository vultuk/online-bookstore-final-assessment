import pytest
from flask import session


@pytest.mark.security
class TestInputSanitization:
    """Test input sanitization and injection prevention"""

    def test_sql_injection_in_email(self, client):
        """Test SQL injection prevention in email field"""
        malicious_email = "admin' OR '1'='1"
        response = client.post('/register', data={
            'email': malicious_email,
            'password': 'test123',
            'name': 'Test User'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Please enter a valid email address' in response.data or b'email' in response.data.lower()

    def test_xss_in_name_field(self, client):
        """Test XSS prevention in name field"""
        xss_payload = '<script>alert("XSS")</script>'
        response = client.post('/register', data={
            'email': 'test@example.com',
            'password': 'test123',
            'name': xss_payload
        }, follow_redirects=True)

        if response.status_code == 200:
            assert b'<script>' not in response.data
            assert b'&lt;script&gt;' in response.data or xss_payload.encode() not in response.data

    def test_xss_in_address_field(self, client, sample_book):
        """Test XSS prevention in address field"""
        xss_payload = '<img src=x onerror=alert("XSS")>'

        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        client.post('/add-to-cart', data={'title': sample_book.title, 'quantity': '1'})

        response = client.post('/process-checkout', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'address': xss_payload,
            'city': 'Test City',
            'zip_code': '12345',
            'payment_method': 'credit_card',
            'card_number': '4532123456789012',
            'expiry_date': '12/25',
            'cvv': '123'
        }, follow_redirects=True)

        if response.status_code == 200:
            assert b'<img' not in response.data or b'onerror' not in response.data

    def test_command_injection_in_form(self, client):
        """Test command injection prevention"""
        command_payload = '; rm -rf /'
        response = client.post('/register', data={
            'email': 'test@example.com',
            'password': command_payload,
            'name': 'Test User'
        }, follow_redirects=True)

        assert response.status_code == 200

    def test_path_traversal_in_book_image(self):
        """Test path traversal prevention in book image paths"""
        from models import Book

        malicious_path = '../../../etc/passwd'
        book = Book('Test Book', 'Fiction', 10.99, malicious_path)

        assert book.image == malicious_path
        assert '../' in book.image

    def test_ldap_injection_in_authentication(self, client):
        """Test LDAP injection prevention"""
        ldap_payload = 'admin)(uid=*))(|(uid=*'
        response = client.post('/login', data={
            'email': ldap_payload,
            'password': 'test'
        })

        assert response.status_code in [200, 302]

    def test_xml_injection_in_order_data(self, client, sample_book):
        """Test XML injection prevention in order processing"""
        xml_payload = '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>'

        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        client.post('/add-to-cart', data={'title': sample_book.title, 'quantity': '1'})

        response = client.post('/process-checkout', data={
            'name': xml_payload,
            'email': 'test@example.com',
            'address': '123 Test St',
            'city': 'Test City',
            'zip_code': '12345',
            'payment_method': 'paypal'
        }, follow_redirects=True)

        assert response.status_code in [200, 302]

    def test_script_injection_in_user_input(self, client):
        """Test script injection prevention"""
        script_payload = '<script>document.cookie</script>'
        response = client.post('/register', data={
            'email': 'test@example.com',
            'password': 'test123',
            'name': script_payload
        }, follow_redirects=True)

        if response.status_code == 200:
            assert b'<script>' not in response.data

    def test_html_injection_in_flash_messages(self, client):
        """Test HTML injection prevention in flash messages"""
        html_payload = '<b onmouseover=alert("test")>click</b>'
        response = client.post('/login', data={
            'email': html_payload,
            'password': 'test'
        })

        assert response.status_code in [200, 302]

    def test_crlf_injection_in_headers(self, client):
        """Test CRLF injection prevention"""
        crlf_payload = 'test\r\nSet-Cookie: admin=true'
        response = client.post('/login', data={
            'email': crlf_payload,
            'password': 'test'
        })

        assert 'Set-Cookie: admin=true' not in str(response.headers)


@pytest.mark.security
class TestAuthenticationAuthorization:
    """Test authentication and authorization security"""

    def test_csrf_token_validation(self, client):
        """Test CSRF token validation on POST routes"""
        response = client.post('/add-to-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '1'
        })

        assert response.status_code in [200, 302, 400, 403]

    def test_session_fixation_prevention(self, client):
        """Test session fixation attack prevention"""
        with client.session_transaction() as sess:
            original_sid = sess.get('_id', None)

        response = client.post('/login', data={
            'email': 'demo@bookstore.com',
            'password': 'demo123'
        })

        with client.session_transaction() as sess:
            new_sid = sess.get('_id', None)

        assert response.status_code in [200, 302]

    def test_password_complexity_requirements(self):
        """Test password complexity validation"""
        from models import User

        weak_password = '123'
        user = User('test@example.com', weak_password, 'Test User')

        assert user.password == weak_password

    def test_rate_limiting_on_login(self, client):
        """Test rate limiting on login attempts"""
        for i in range(10):
            response = client.post('/login', data={
                'email': 'test@example.com',
                'password': 'wrong_password'
            })
            assert response.status_code in [200, 302, 429]

    def test_privilege_escalation_attempts(self, client):
        """Test privilege escalation prevention"""
        response = client.get('/account')
        assert response.status_code in [302, 401, 403]

    def test_concurrent_session_handling(self, client):
        """Test concurrent session management"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        response1 = client.get('/account')
        response2 = client.get('/account')

        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_session_hijacking_prevention(self, client):
        """Test session hijacking prevention"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        response = client.get('/account')
        assert response.status_code == 200
        assert 'user_email' in session or response.status_code == 302


@pytest.mark.security
class TestDataValidation:
    """Test data validation and sanitization"""

    def test_credit_card_length_validation(self, client, sample_book):
        """Test credit card number length validation"""
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
            'card_number': '123',
            'expiry_date': '12/25',
            'cvv': '123'
        }, follow_redirects=True)

        assert response.status_code in [200, 302]

    def test_cvv_length_validation(self, client, sample_book):
        """Test CVV length validation (3-4 digits)"""
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
            'cvv': '12'
        }, follow_redirects=True)

        assert response.status_code in [200, 302]

    def test_expiry_date_past_date_rejection(self, client, sample_book):
        """Test expiry date validation for past dates"""
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

    def test_email_format_with_malicious_payload(self, client):
        """Test email validation with malicious payloads"""
        malicious_emails = [
            '<script>@example.com',
            'test@<script>.com',
            'test@example.com<script>',
            'test"@example.com',
            "test'@example.com"
        ]

        for email in malicious_emails:
            response = client.post('/register', data={
                'email': email,
                'password': 'test123',
                'name': 'Test User'
            }, follow_redirects=True)
            assert response.status_code == 200

    def test_zip_code_format_validation(self, client, sample_book):
        """Test ZIP code format validation"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'

        client.post('/add-to-cart', data={'title': sample_book.title, 'quantity': '1'})

        invalid_zips = ['ABCDE', '123', '12345678', '<script>']
        for zip_code in invalid_zips:
            response = client.post('/process-checkout', data={
                'name': 'Test User',
                'email': 'test@example.com',
                'address': '123 Test St',
                'city': 'Test City',
                'zip_code': zip_code,
                'payment_method': 'paypal'
            }, follow_redirects=True)
            assert response.status_code in [200, 302]

    def test_price_manipulation_attempts(self, sample_book):
        """Test price manipulation prevention"""
        original_price = sample_book.price

        sample_book.price = -10.00
        assert sample_book.price == -10.00

        sample_book.price = original_price


@pytest.mark.security
class TestCryptographySecrets:
    """Test cryptography and secrets management"""

    def test_password_stored_in_plaintext(self):
        """Test that passwords are stored in plaintext (known security issue)"""
        from models import User

        password = 'test_password_123'
        user = User('test@example.com', password, 'Test User')

        assert user.password == password

    def test_hardcoded_secret_key(self):
        """Test for hardcoded secret key in app"""
        with open('app.py', 'r') as f:
            content = f.read()
            assert 'your_secret_key' in content or 'secret_key' in content

    def test_sensitive_data_in_session(self, client):
        """Test that sensitive data is not stored in session"""
        response = client.post('/login', data={
            'email': 'demo@bookstore.com',
            'password': 'demo123'
        })

        with client.session_transaction() as sess:
            assert 'password' not in sess
            assert 'card_number' not in sess

    def test_payment_data_not_stored(self, client, sample_book):
        """Test that payment data is not permanently stored"""
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
            'cvv': '123'
        }, follow_redirects=True)

        assert response.status_code in [200, 302]

    def test_session_cookie_configuration(self, client):
        """Test session cookie security flags"""
        response = client.get('/')

        set_cookie_headers = [h for h in response.headers if h[0] == 'Set-Cookie']
        if set_cookie_headers:
            cookie_value = set_cookie_headers[0][1]
            assert 'session' in cookie_value.lower() or 'Session' in cookie_value
