from locust import HttpUser, task, between, events
import random


class BookstoreUser(HttpUser):
    """
    Load testing user simulation for Online Bookstore application.

    Simulates realistic user behavior with weighted tasks:
    - 50% browsing catalog
    - 30% adding items to cart
    - 15% viewing cart
    - 5% checkout process
    """

    wait_time = between(1, 3)
    host = "http://localhost:5000"

    def on_start(self):
        """Initialize user session on start"""
        self.books = [
            "The Great Gatsby",
            "1984",
            "I Ching",
            "Moby Dick"
        ]
        self.login()

    def login(self):
        """Login user before starting tasks"""
        self.client.post("/login", data={
            "email": "demo@bookstore.com",
            "password": "demo123"
        })

    @task(5)
    def browse_catalog(self):
        """Browse the main catalog page"""
        self.client.get("/")

    @task(3)
    def add_to_cart(self):
        """Add a random book to cart"""
        book_title = random.choice(self.books)
        quantity = random.randint(1, 3)

        self.client.post("/add-to-cart", data={
            "title": book_title,
            "quantity": str(quantity)
        })

    @task(2)
    def view_cart(self):
        """View the shopping cart"""
        self.client.get("/cart")

    @task(1)
    def update_cart(self):
        """Update cart quantity"""
        book_title = random.choice(self.books)
        new_quantity = random.randint(1, 5)

        self.client.post("/update-cart", data={
            "title": book_title,
            "quantity": str(new_quantity)
        })

    @task(1)
    def checkout_flow(self):
        """Complete checkout process"""
        self.client.get("/checkout")

        self.client.post("/process-checkout", data={
            "name": "Test User",
            "email": "test@example.com",
            "address": "123 Test Street",
            "city": "Test City",
            "zip_code": "12345",
            "payment_method": "paypal",
            "discount_code": random.choice(["", "SAVE10", "WELCOME20"])
        })

    @task(1)
    def view_account(self):
        """View user account page"""
        self.client.get("/account")


class StressTestUser(HttpUser):
    """
    Stress testing user with aggressive behavior for peak load simulation.

    Simulates high-stress scenarios with minimal wait time and rapid operations.
    """

    wait_time = between(0.1, 0.5)
    host = "http://localhost:5000"

    def on_start(self):
        """Initialize for stress testing"""
        self.books = ["The Great Gatsby", "1984", "I Ching", "Moby Dick"]
        self.client.post("/login", data={
            "email": "demo@bookstore.com",
            "password": "demo123"
        })

    @task(10)
    def rapid_catalog_access(self):
        """Rapidly access catalog"""
        self.client.get("/")

    @task(5)
    def rapid_cart_operations(self):
        """Rapid cart add/update/view operations"""
        book_title = random.choice(self.books)

        self.client.post("/add-to-cart", data={
            "title": book_title,
            "quantity": "1"
        })
        self.client.get("/cart")
        self.client.post("/update-cart", data={
            "title": book_title,
            "quantity": str(random.randint(1, 10))
        })


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Print test start information"""
    print(f"Load test starting on {environment.host}")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print test completion summary"""
    print("=" * 60)
    print("Load test completed")
    print(f"Total requests: {environment.stats.total.num_requests}")
    print(f"Total failures: {environment.stats.total.num_failures}")
    print(f"Average response time: {environment.stats.total.avg_response_time:.2f}ms")
    print(f"Requests per second: {environment.stats.total.total_rps:.2f}")
