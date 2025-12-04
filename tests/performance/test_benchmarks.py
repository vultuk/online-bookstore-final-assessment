import pytest
import timeit
import cProfile
import pstats
from io import StringIO
from models import Book, Cart, User, Order, PaymentGateway


@pytest.mark.performance
class TestPerformanceBenchmarks:
    """Performance benchmark tests using timeit and cProfile"""

    def test_cart_total_calculation_small_quantity(self, benchmark):
        """Benchmark cart total with small quantity (1 item)"""
        cart = Cart()
        book = Book("Test Book", "Fiction", 10.99, "/test.jpg")
        cart.add_book(book, 1)

        result = benchmark(cart.get_total_price)
        assert result > 0

    def test_cart_total_calculation_medium_quantity(self, benchmark):
        """Benchmark cart total with medium quantity (100 items)"""
        cart = Cart()
        book = Book("Test Book", "Fiction", 10.99, "/test.jpg")
        cart.add_book(book, 100)

        result = benchmark(cart.get_total_price)
        assert result > 0

    def test_cart_total_calculation_large_quantity(self, benchmark):
        """Benchmark cart total with large quantity (1000 items)"""
        cart = Cart()
        book = Book("Test Book", "Fiction", 10.99, "/test.jpg")
        cart.add_book(book, 1000)

        result = benchmark(cart.get_total_price)
        assert result > 0

    def test_cart_total_timeit_comparison(self):
        """Use timeit to compare cart total calculation performance"""
        cart = Cart()
        book = Book("Test Book", "Fiction", 10.99, "/test.jpg")

        # Test with different quantities
        quantities = [1, 10, 100, 1000]
        results = {}

        for qty in quantities:
            cart.clear()
            cart.add_book(book, qty)

            # Time the get_total_price operation
            time_taken = timeit.timeit(
                lambda: cart.get_total_price(),
                number=1000
            )
            results[qty] = time_taken

        # Print results for documentation
        print("\n=== Cart Total Calculation Performance (timeit) ===")
        for qty, time_val in results.items():
            print(f"Quantity {qty:4d}: {time_val:.6f} seconds (1000 iterations)")
        print("Note: O(n*m) complexity causes linear growth with quantity")

        # Performance should scale with quantity due to O(n*m) bug
        assert results[1000] > results[100] > results[10]

    def test_cart_total_cprofile_analysis(self):
        """Use cProfile to analyze cart total calculation"""
        cart = Cart()
        book = Book("Test Book", "Fiction", 10.99, "/test.jpg")
        cart.add_book(book, 1000)

        # Profile the function
        profiler = cProfile.Profile()
        profiler.enable()

        for _ in range(100):
            cart.get_total_price()

        profiler.disable()

        # Get stats
        stream = StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats('cumulative')
        stats.print_stats(10)

        profile_output = stream.getvalue()
        print("\n=== cProfile Analysis: Cart Total Calculation ===")
        print(profile_output)
        print("Note: High cumulative time due to nested loop O(n*m) inefficiency")

        # Assert profiling completed
        assert 'get_total_price' in profile_output

    def test_order_history_sorting_small(self, benchmark):
        """Benchmark order history with few orders (10 orders)"""
        user = User("test@example.com", "password")

        # Add 10 orders
        for i in range(10):
            order = Order(f"ORDER{i}", "test@example.com", [], {}, {}, 50.00)
            user.add_order(order)

        result = benchmark(user.get_order_history)
        assert len(result) == 10

    def test_order_history_sorting_medium(self, benchmark):
        """Benchmark order history with medium orders (100 orders)"""
        user = User("test@example.com", "password")

        # Add 100 orders
        for i in range(100):
            order = Order(f"ORDER{i}", "test@example.com", [], {}, {}, 50.00)
            user.add_order(order)

        result = benchmark(user.get_order_history)
        assert len(result) == 100

    def test_order_history_sorting_large(self, benchmark):
        """Benchmark order history with many orders (1000 orders)"""
        user = User("test@example.com", "password")

        # Add 1000 orders
        for i in range(1000):
            order = Order(f"ORDER{i}", "test@example.com", [], {}, {}, 50.00)
            user.add_order(order)

        result = benchmark(user.get_order_history)
        assert len(result) == 1000

    def test_order_sorting_timeit_comparison(self):
        """Use timeit to measure order sorting inefficiency"""
        results = {}

        for num_orders in [10, 100, 1000]:
            user = User("test@example.com", "password")

            # Pre-populate orders
            for i in range(num_orders):
                order = Order(f"ORDER{i}", "test@example.com", [], {}, {}, 50.00)
                user.orders.append(order)

            # Time adding one more order (triggers sort)
            new_order = Order("NEWORD", "test@example.com", [], {}, {}, 50.00)

            time_taken = timeit.timeit(
                lambda: user.add_order(new_order),
                number=100
            )
            results[num_orders] = time_taken

            # Remove the added order for next iteration
            user.orders.pop()

        print("\n=== Order Sorting Performance (timeit) ===")
        for num, time_val in results.items():
            print(f"{num:4d} orders: {time_val:.6f} seconds (100 iterations)")
        print("Note: Sort on every add_order call is inefficient")

        # Time should increase with more orders
        assert results[1000] > results[100] > results[10]

    def test_order_sorting_cprofile_analysis(self):
        """Use cProfile to analyze order sorting"""
        user = User("test@example.com", "password")

        profiler = cProfile.Profile()
        profiler.enable()

        # Add 500 orders (triggers sort each time)
        for i in range(500):
            order = Order(f"ORDER{i}", "test@example.com", [], {}, {}, 50.00)
            user.add_order(order)

        profiler.disable()

        stream = StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats('cumulative')
        stats.print_stats(10)

        profile_output = stream.getvalue()
        print("\n=== cProfile Analysis: Order Sorting ===")
        print(profile_output)
        print("Note: Sorting on every add_order call is inefficient")

        assert 'add_order' in profile_output

    def test_payment_processing_delay_timeit(self):
        """Use timeit to measure payment processing delay"""
        payment_info = {'card_number': '4532123456789012', 'payment_method': 'credit_card'}

        # Time with the sleep delay
        time_with_delay = timeit.timeit(
            lambda: PaymentGateway.process_payment(payment_info),
            number=10
        )

        print("\n=== Payment Processing Performance (timeit) ===")
        print(f"Time for 10 payments: {time_with_delay:.6f} seconds")
        print(f"Average per payment: {time_with_delay / 10:.6f} seconds")
        print("Note: time.sleep(0.1) adds unnecessary 0.1s delay per payment")

        # Should take at least 1 second due to sleep (0.1s * 10)
        assert time_with_delay >= 1.0

    def test_payment_processing_cprofile_analysis(self):
        """Use cProfile to analyze payment processing"""
        payment_info = {'card_number': '4532123456789012', 'payment_method': 'credit_card'}

        profiler = cProfile.Profile()
        profiler.enable()

        for _ in range(20):
            PaymentGateway.process_payment(payment_info)

        profiler.disable()

        stream = StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats('cumulative')
        stats.print_stats(10)

        profile_output = stream.getvalue()
        print("\n=== cProfile Analysis: Payment Processing ===")
        print(profile_output)
        print("Note: time.sleep dominates execution time")

        # Should show sleep in profile
        assert 'process_payment' in profile_output

    def test_book_search_linear_vs_helper(self):
        """Compare linear search vs using helper function"""
        from app import BOOKS, get_book_by_title

        book_title = "The Great Gatsby"

        # Time linear search (current buggy implementation in add_to_cart)
        def linear_search():
            book = None
            for b in BOOKS:
                if b.title == book_title:
                    book = b
                    break
            return book

        # Time helper function
        def helper_search():
            return get_book_by_title(book_title)

        time_linear = timeit.timeit(linear_search, number=10000)
        time_helper = timeit.timeit(helper_search, number=10000)

        print("\n=== Book Search Performance (timeit) ===")
        print(f"Linear search:  {time_linear:.6f} seconds (10000 iterations)")
        print(f"Helper function: {time_helper:.6f} seconds (10000 iterations)")
        print(f"Difference:     {abs(time_linear - time_helper):.6f} seconds")
        print("Note: Both use linear search, but helper function is more maintainable")

        # Both should complete successfully
        assert time_linear > 0
        assert time_helper > 0
