import pytest
from app import users


@pytest.mark.integration
class TestAuthRoutes:
    """Integration tests for authentication routes"""

    def test_register_page_get(self, client):
        """Test accessing registration page"""
        response = client.get('/register')

        assert response.status_code == 200
        assert b'register' in response.data.lower()

    def test_register_valid_user(self, client, valid_registration_form):
        """Test registering a new user with valid data"""
        response = client.post('/register', data=valid_registration_form, follow_redirects=True)

        assert response.status_code == 200
        assert b'success' in response.data.lower() or b'logged in' in response.data.lower()
        assert valid_registration_form['email'] in users

    def test_register_creates_user_in_storage(self, client, valid_registration_form):
        """Test that registration adds user to users dictionary"""
        initial_user_count = len(users)

        client.post('/register', data=valid_registration_form, follow_redirects=True)

        assert len(users) == initial_user_count + 1

    def test_register_logs_user_in(self, client, valid_registration_form):
        """Test that registration automatically logs user in"""
        client.post('/register', data=valid_registration_form, follow_redirects=True)

        # User should be logged in (session should have user_email)
        with client.session_transaction() as sess:
            assert 'user_email' in sess
            assert sess['user_email'] == valid_registration_form['email']

    def test_register_duplicate_email(self, client, valid_registration_form):
        """Test registering with an email that already exists"""
        # Register once
        client.post('/register', data=valid_registration_form)

        # Try to register again with same email
        response = client.post('/register', data=valid_registration_form, follow_redirects=True)

        assert response.status_code == 200
        assert b'exists' in response.data.lower() or b'already' in response.data.lower()

    @pytest.mark.bug
    def test_register_duplicate_email_different_case(self, client, valid_registration_form):
        """BUG #5: Test that emails should be case-insensitive"""
        # Register with lowercase
        client.post('/register', data=valid_registration_form)

        # Try to register with same email in uppercase
        uppercase_form = valid_registration_form.copy()
        uppercase_form['email'] = valid_registration_form['email'].upper()

        response = client.post('/register', data=uppercase_form, follow_redirects=True)

        # Expected: should detect duplicate and show error
        # Actual: creates duplicate user due to case-sensitive check
        assert b'exists' in response.data.lower() or b'already' in response.data.lower(), \
            "Bug: Email checking is case-sensitive, allows duplicates"

    @pytest.mark.bug
    def test_register_invalid_email_format(self, client, valid_registration_form):
        """BUG #4: Test that email format should be validated"""
        invalid_emails = [
            'notanemail',
            'missing@domain',
            '@nodomain.com',
            'spaces in@email.com',
            'double@@domain.com'
        ]

        for invalid_email in invalid_emails:
            valid_registration_form['email'] = invalid_email
            response = client.post('/register', data=valid_registration_form, follow_redirects=True)

            # Expected: should reject invalid email
            # Actual: accepts any string as email
            # This assertion will fail, demonstrating the bug
            assert b'invalid' in response.data.lower() or b'valid email' in response.data.lower(), \
                f"Bug: No email validation for '{invalid_email}'"

    def test_register_missing_required_fields(self, client):
        """Test registration with missing required fields"""
        response = client.post('/register', data={
            'email': 'test@example.com'
            # Missing password and name
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'required' in response.data.lower()

    def test_register_missing_email(self, client):
        """Test registration without email"""
        response = client.post('/register', data={
            'password': 'password123',
            'name': 'Test User'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'required' in response.data.lower()

    def test_login_page_get(self, client):
        """Test accessing login page"""
        response = client.get('/login')

        assert response.status_code == 200
        assert b'login' in response.data.lower()

    def test_login_valid_credentials(self, client, registered_user):
        """Test logging in with valid credentials"""
        response = client.post('/login', data={
            'email': registered_user.email,
            'password': registered_user.password
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'success' in response.data.lower() or b'logged in' in response.data.lower()

    def test_login_sets_session(self, client, registered_user):
        """Test that login sets user_email in session"""
        client.post('/login', data={
            'email': registered_user.email,
            'password': registered_user.password
        })

        with client.session_transaction() as sess:
            assert 'user_email' in sess
            assert sess['user_email'] == registered_user.email

    def test_login_invalid_email(self, client):
        """Test login with email that doesn't exist"""
        response = client.post('/login', data={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'invalid' in response.data.lower()

    def test_login_wrong_password(self, client, registered_user):
        """Test login with wrong password"""
        response = client.post('/login', data={
            'email': registered_user.email,
            'password': 'wrongpassword'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'invalid' in response.data.lower()

    def test_logout(self, client, registered_user):
        """Test logging out"""
        # Login first
        client.post('/login', data={
            'email': registered_user.email,
            'password': registered_user.password
        })

        # Then logout
        response = client.get('/logout', follow_redirects=True)

        assert response.status_code == 200
        assert b'logged out' in response.data.lower()

    def test_logout_clears_session(self, client, registered_user):
        """Test that logout clears session"""
        # Login first
        client.post('/login', data={
            'email': registered_user.email,
            'password': registered_user.password
        })

        # Logout
        client.get('/logout')

        # Session should not have user_email
        with client.session_transaction() as sess:
            assert 'user_email' not in sess

    def test_logout_when_not_logged_in(self, client):
        """Test logout when no user is logged in"""
        response = client.get('/logout', follow_redirects=True)

        assert response.status_code == 200
