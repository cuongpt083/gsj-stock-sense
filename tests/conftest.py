"""
Pytest configuration and fixtures.
Cung cấp database độc lập cho mỗi test function.
"""
import pytest
from data.init_database import init_database


@pytest.fixture(autouse=True, scope="function")
def reset_db_before_each_test():
    """Đảm bảo database được reset sạch trước mỗi test function để tránh side-effects."""
    init_database()
    yield
