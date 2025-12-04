import pytest


@pytest.mark.integration
class TestAccountRoutes:
    """Integration tests for account management routes"""

    def test_account_page_requires_login(self, client):
        """Test that account page requires login"""
        response = client.get('/account', follow_redirects=True)

        assert response.status_code == 200
        assert b'login' in response.data.lower()

    def test_account_page_when_logged_in(self, client, registered_user):
        """Test accessing account page when logged in"""
        # Login first
        client.post('/login', data={
            'email': registered_user.email,
            'password': registered_user.password
        })

        response = client.get('/account')

        assert response.status_code == 200
        assert b'account' in response.data.lower()

    def test_account_shows_user_info(self, client, registered_user):
        """Test that account page shows user information"""
        client.post('/login', data={
            'email': registered_user.email,
            'password': registered_user.password
        })

        response = client.get('/account')

        assert registered_user.name.encode() in response.data
        assert registered_user.email.encode() in response.data

    def test_account_shows_order_history(self, client, registered_user, sample_order):
        """Test that account page shows order history"""
        # Add order to user
        registered_user.add_order(sample_order)

        # Login
        client.post('/login', data={
            'email': registered_user.email,
            'password': registered_user.password
        })

        response = client.get('/account')

        assert response.status_code == 200
        # Should show order information
        assert sample_order.order_id.encode() in response.data

    def test_update_profile_requires_login(self, client):
        """Test that updating profile requires login"""
        response = client.post('/update-profile', data={
            'name': 'New Name',
            'address': 'New Address'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'login' in response.data.lower()

    def test_update_profile_name_and_address(self, client, registered_user):
        """Test updating user name and address"""
        # Login
        client.post('/login', data={
            'email': registered_user.email,
            'password': registered_user.password
        })

        # Update profile
        response = client.post('/update-profile', data={
            'name': 'Updated Name',
            'address': 'Updated Address'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'updated' in response.data.lower()

        # Verify changes
        assert registered_user.name == 'Updated Name'
        assert registered_user.address == 'Updated Address'

    def test_update_profile_password(self, client, registered_user):
        """Test updating user password"""
        # Login
        client.post('/login', data={
            'email': registered_user.email,
            'password': registered_user.password
        })

        new_password = 'newpassword123'

        # Update password
        response = client.post('/update-profile', data={
            'name': registered_user.name,
            'address': registered_user.address,
            'new_password': new_password
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'password' in response.data.lower() and b'updated' in response.data.lower()

        # Verify password was changed
        assert registered_user.password == new_password

    def test_update_profile_without_password_change(self, client, registered_user):
        """Test updating profile without changing password"""
        original_password = registered_user.password

        # Login
        client.post('/login', data={
            'email': registered_user.email,
            'password': registered_user.password
        })

        # Update without new_password field
        response = client.post('/update-profile', data={
            'name': 'New Name',
            'address': registered_user.address
        }, follow_redirects=True)

        assert response.status_code == 200

        # Password should remain unchanged
        assert registered_user.password == original_password

    def test_update_profile_partial_data(self, client, registered_user):
        """Test updating only some profile fields"""
        original_address = registered_user.address

        # Login
        client.post('/login', data={
            'email': registered_user.email,
            'password': registered_user.password
        })

        # Update only name
        response = client.post('/update-profile', data={
            'name': 'Only Name Changed'
        }, follow_redirects=True)

        assert response.status_code == 200

        # Name should change, address should remain
        assert registered_user.name == 'Only Name Changed'

    def test_login_required_decorator(self, client):
        """Test that login_required decorator protects routes"""
        protected_routes = [
            '/account',
            '/update-profile'
        ]

        for route in protected_routes:
            if route == '/update-profile':
                response = client.post(route, follow_redirects=True)
            else:
                response = client.get(route, follow_redirects=True)

            assert response.status_code == 200
            assert b'login' in response.data.lower()
