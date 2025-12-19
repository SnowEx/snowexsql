"""
Configuration for deployment/integration tests.
These tests use Lambda and don't need the local DB session fixtures.
"""
import pytest


# Override the session-scoped fixtures from parent conftest.py
@pytest.fixture(scope="session")
def test_db_info():
    """No-op: Integration tests don't use local DB"""
    return None


@pytest.fixture(scope="session")
def sqlalchemy_engine():
    """No-op: Integration tests don't use local DB engine"""
    return None


@pytest.fixture(scope="session")
def connection():
    """No-op: Integration tests don't use local DB connection"""
    return None


@pytest.fixture(scope="function")
def db_session():
    """No-op: Integration tests don't use local DB session"""
    pass


@pytest.fixture(scope="function")
def db_test_session():
    """No-op: Integration tests don't use local DB session"""
    pass


@pytest.fixture(scope="function")
def db_test_connection():
    """No-op: Integration tests don't use local DB connection"""
    pass


@pytest.fixture(scope="module")
def lambda_client():
    """Fixture to provide a SnowExLambdaClient instance for all tests"""
    from snowexsql.lambda_client import SnowExLambdaClient
    return SnowExLambdaClient()