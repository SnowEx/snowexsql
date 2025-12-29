"""Fixtures for Lambda integration tests."""
import pytest

@pytest.fixture(scope="module")
def lambda_client():
    """Fixture to provide a SnowExLambdaClient instance"""
    from snowexsql.lambda_client import SnowExLambdaClient
    return SnowExLambdaClient()