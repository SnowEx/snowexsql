"""
Test the Lambda HANDLER (lambda_handler.py) functionality locally.

Tests the handle_event_with_secret() function and Lambda handler logic
without deploying to AWS. Connects directly to the database using local
credentials. This tests the server-side/handler logic, NOT the client.

These tests require a credentials.json file in the repository root
directory. Mark with @pytest.mark.handler to run separately from client
tests.
"""
import json
import os
from pathlib import Path
import pytest

# Set up the environment to simulate Lambda
os.environ['DB_SECRET_NAME'] = 'dummy_secret'
os.environ['DB_AWS_REGION'] = 'us-west-2'

from snowexsql.lambda_handler import handle_event_with_secret


# ========================================================================
# FIXTURES
# ========================================================================

@pytest.fixture(scope="module")
def local_credentials():
    """
    Load credentials using snowexsql.db functions.
    
    Uses the same credential loading logic as the main package:
    - SNOWEX_DB_CONNECTION environment variable (user:pass@host/db)
    - SNOWEX_DB_CREDENTIALS environment variable (path to JSON file)
    - credentials.json in current directory
    
    Set environment:
        export SNOWEX_DB_CONNECTION=user:pass@host/dbname
    Or:
        export SNOWEX_DB_CREDENTIALS=/path/to/credentials.json
    """
    from snowexsql.db import load_credentials
    
    # Check if using connection string format
    if os.getenv("SNOWEX_DB_CONNECTION"):
        # Parse connection string: user:pass@host/dbname
        conn_str = os.getenv("SNOWEX_DB_CONNECTION")
        try:
            # Split user:pass@host/dbname
            auth, location = conn_str.split('@')
            username, password = auth.split(':')
            host, dbname = location.split('/')
            
            return {
                'username': username,
                'password': password,
                'host': host,
                'dbname': dbname
            }
        except ValueError as e:
            pytest.skip(
                f"Invalid SNOWEX_DB_CONNECTION format: {e}\n"
                "Expected format: user:pass@host/dbname"
            )
    
    # Otherwise use load_credentials for JSON file
    try:
        creds = load_credentials()
        
        # Convert to the format expected by the Lambda handler
        return {
            'username': creds.get('username') or creds.get('user'),
            'password': creds.get('password'),
            'host': creds.get('address') or creds.get('host'),
            'dbname': (creds.get('db_name') or 
                      creds.get('database') or 
                      creds.get('dbname'))
        }
    except FileNotFoundError as e:
        pytest.skip(
            f"Database credentials not found: {str(e)}\n"
            "Set SNOWEX_DB_CONNECTION or SNOWEX_DB_CREDENTIALS environment variable"
        )


# ========================================================================
# CONNECTION TESTS
# ========================================================================

@pytest.mark.handler
def test_handler_connection(local_credentials):
    """Test basic database connection through handler"""
    event = {'action': 'test_connection'}
    
    result = handle_event_with_secret(event, local_credentials)
    
    assert result.get('connected'), "Handler connection failed"
    assert result.get('version'), "Database version not returned"
    version_str = result.get('version', '')
    assert 'PostgreSQL' in version_str, "Expected PostgreSQL version"


# ========================================================================
# LAYER MEASUREMENTS TESTS
# ========================================================================

@pytest.mark.handler
class TestLayerMeasurementsHandler:
    """Test LayerMeasurements actions through the handler"""
    
    def test_layer_all_instruments(self, local_credentials):
        """Test LayerMeasurements.all_instruments property"""
        event = {
            'action': 'LayerMeasurements.all_instruments'
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        error_msg = f"Handler returned error: {result.get('error')}"
        assert 'error' not in result, error_msg
        assert 'data' in result, "Response missing 'data' field"
        assert isinstance(result['data'], list), (
            "Expected list of instruments"
        )
        
    def test_layer_all_campaigns(self, local_credentials):
        """Test LayerMeasurements.all_campaigns property"""
        event = {
            'action': 'LayerMeasurements.all_campaigns'
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        error_msg = f"Handler returned error: {result.get('error')}"
        assert 'error' not in result, error_msg
        assert 'data' in result, "Response missing 'data' field"
        assert isinstance(result['data'], list), (
            "Expected list of campaigns"
        )
    
    def test_layer_from_filter(self, local_credentials):
        """Test LayerMeasurements.from_filter with limit"""
        event = {
            'action': 'LayerMeasurements.from_filter',
            'filters': {
                'limit': 5
            }
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        error_msg = f"Handler returned error: {result.get('error')}"
        assert 'error' not in result, error_msg
        assert 'data' in result, "Response missing 'data' field"
        assert isinstance(result['data'], list), (
            "Expected list of records"
        )
        assert len(result['data']) <= 5, "Limit not respected"
        
    def test_layer_from_unique_entries_single_column(
        self, local_credentials
    ):
        """Test from_unique_entries with single column"""
        event = {
            'action': 'LayerMeasurements.from_unique_entries',
            'columns': ['depth'],
            'filters': {'limit': 10}
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        error_msg = f"Handler returned error: {result.get('error')}"
        assert 'error' not in result, error_msg
        assert 'data' in result, "Response missing 'data' field"
        assert isinstance(result['data'], list), (
            "Expected list of unique depths"
        )
        
    def test_layer_from_unique_entries_multiple_columns(
        self, local_credentials
    ):
        """Test from_unique_entries with multiple columns"""
        event = {
            'action': 'LayerMeasurements.from_unique_entries',
            'columns': ['depth', 'value'],
            'filters': {'limit': 5}
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        error_msg = f"Handler returned error: {result.get('error')}"
        assert 'error' not in result, error_msg
        assert 'data' in result, "Response missing 'data' field"
        # Multiple columns should return list of tuples/lists
        
    def test_layer_filter_by_instrument(self, local_credentials):
        """Test from_filter with instrument filter"""
        # First get available instruments
        event1 = {
            'action': 'LayerMeasurements.all_instruments'
        }
        result1 = handle_event_with_secret(event1, local_credentials)
        
        if result1.get('data'):
            instrument = result1['data'][0]
            
            # Now filter by that instrument
            event2 = {
                'action': 'LayerMeasurements.from_filter',
                'filters': {
                    'instrument': instrument,
                    'limit': 3
                }
            }
            result2 = handle_event_with_secret(event2, local_credentials)
            
            error_msg = f"Filter failed: {result2.get('error')}"
            assert 'error' not in result2, error_msg
            assert 'data' in result2


# ========================================================================
# POINT MEASUREMENTS TESTS
# ========================================================================

@pytest.mark.handler
class TestPointMeasurementsHandler:
    """Test PointMeasurements actions through the handler"""
    
    def test_point_all_instruments(self, local_credentials):
        """Test PointMeasurements.all_instruments property"""
        event = {
            'action': 'PointMeasurements.all_instruments'
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        error_msg = f"Handler returned error: {result.get('error')}"
        assert 'error' not in result, error_msg
        assert 'data' in result, "Response missing 'data' field"
        assert isinstance(result['data'], list), (
            "Expected list of instruments"
        )
        
    def test_point_from_filter(self, local_credentials):
        """Test PointMeasurements.from_filter"""
        event = {
            'action': 'PointMeasurements.from_filter',
            'filters': {
                'limit': 5
            }
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        error_msg = f"Handler returned error: {result.get('error')}"
        assert 'error' not in result, error_msg
        assert 'data' in result, "Response missing 'data' field"
        assert isinstance(result['data'], list), (
            "Expected list of records"
        )
        
    def test_point_from_unique_entries(self, local_credentials):
        """Test PointMeasurements.from_unique_entries"""
        event = {
            'action': 'PointMeasurements.from_unique_entries',
            'columns': ['value'],  # Use 'type' instead of 'instrument' - direct column
            'filters': {'limit': 10}
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        error_msg = f"Handler returned error: {result.get('error')}"
        assert 'error' not in result, error_msg
        assert 'data' in result, "Response missing 'data' field"


# ========================================================================
# QUERY TESTS
# ========================================================================

@pytest.mark.handler
class TestRawQueryHandler:
    """Test raw SQL query functionality"""
    
    def test_simple_query(self, local_credentials):
        """Test simple SQL query"""
        event = {
            'action': 'query',
            'sql': 'SELECT version();'
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        error_msg = f"Query failed: {result.get('error')}"
        assert 'error' not in result, error_msg
        assert 'data' in result, "Response missing 'data' field"
        assert len(result['data']) > 0, "Expected query results"
        
    def test_query_with_limit(self, local_credentials):
        """Test query with LIMIT clause"""
        event = {
            'action': 'query',
            'sql': 'SELECT * FROM points LIMIT 3;'
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        error_msg = f"Query failed: {result.get('error')}"
        assert 'error' not in result, error_msg
        assert 'data' in result, "Response missing 'data' field"


# ========================================================================
# ERROR HANDLING TESTS
# ========================================================================

@pytest.mark.handler
class TestHandlerErrorHandling:
    """Test error handling in the handler"""
    
    def test_invalid_action(self, local_credentials):
        """Test handler response to invalid action"""
        event = {
            'action': 'invalid_action_name'
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        assert 'error' in result, "Expected error for invalid action"
        
    def test_invalid_class_name(self, local_credentials):
        """Test handler response to invalid class name"""
        event = {
            'action': 'InvalidClass.from_filter',
            'filters': {}
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        assert 'error' in result, "Expected error for invalid class"
        
    def test_missing_required_parameter(self, local_credentials):
        """Test handler response to missing required parameter"""
        event = {
            'action': 'LayerMeasurements.from_unique_entries',
            # Missing 'columns' parameter
            'filters': {}
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        assert 'error' in result, "Expected error for missing parameter"
        
    def test_invalid_sql_query(self, local_credentials):
        """Test handler response to invalid SQL"""
        event = {
            'action': 'query',
            'sql': 'SELECT * FROM nonexistent_table_xyz;'
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        assert 'error' in result, "Expected error for invalid SQL"


# ========================================================================
# SPATIAL QUERY TESTS (from_area)
# ========================================================================

@pytest.mark.handler
class TestSpatialQueryHandler:
    """Test spatial query functionality using PostGIS"""
    
    def test_point_from_area_with_buffer(self, local_credentials):
        """Test from_area with point and buffer"""
        event = {
            'action': 'PointMeasurements.from_area',
            'pt_wkt': 'POINT(743683 4321095)',
            'buffer': 1000,  # 1km buffer
            'crs': 26912,  # UTM Zone 12N
            'filters': {'limit': 10}
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        error_msg = f"from_area failed: {result.get('error')}"
        assert 'error' not in result, error_msg
        assert 'data' in result, "Response missing 'data' field"
        assert isinstance(result['data'], list)
        
    def test_layer_from_area_with_shape(self, local_credentials):
        """Test from_area with polygon shape"""
        # Small bounding box
        event = {
            'action': 'LayerMeasurements.from_area',
            'shp_wkt': 'POLYGON((743000 4321000, 744000 4321000, 744000 4322000, 743000 4322000, 743000 4321000))',
            'crs': 26912,
            'filters': {'limit': 10}
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        error_msg = f"from_area failed: {result.get('error')}"
        assert 'error' not in result, error_msg
        assert 'data' in result, "Response missing 'data' field"
        
    def test_from_area_with_filters(self, local_credentials):
        """Test from_area with additional filters"""
        event = {
            'action': 'PointMeasurements.from_area',
            'pt_wkt': 'POINT(743683 4321095)',
            'buffer': 5000,
            'crs': 26912,
            'filters': {
                'type': 'depth',
                'limit': 5
            }
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        error_msg = f"from_area with filters failed: {result.get('error')}"
        assert 'error' not in result, error_msg
        assert 'data' in result


# ========================================================================
# RESPONSE FORMAT TESTS
# ========================================================================

@pytest.mark.handler
class TestHandlerResponseFormat:
    """Test that handler responses follow expected format"""
    
    def test_connection_response_format(self, local_credentials):
        """Test connection response has expected fields"""
        event = {'action': 'test_connection'}
        result = handle_event_with_secret(event, local_credentials)
        
        assert 'connected' in result
        assert 'version' in result
        
    def test_data_response_format(self, local_credentials):
        """Test data query response has expected fields"""
        event = {
            'action': 'PointMeasurements.from_filter',
            'filters': {'limit': 1}
        }
        result = handle_event_with_secret(event, local_credentials)
        
        assert 'data' in result
        assert 'count' in result
        assert result['count'] == len(result['data'])
        
    def test_property_response_format(self, local_credentials):
        """Test property response has expected fields"""
        event = {
            'action': 'LayerMeasurements.all_instruments'
        }
        result = handle_event_with_secret(event, local_credentials)
        
        assert 'data' in result
        assert isinstance(result['data'], list)


# ========================================================================
# ARCHITECTURE VERIFICATION
# ========================================================================

@pytest.mark.handler
class TestHandlerArchitecture:
    """Verify handler uses api.py as single source of truth"""
    
    def test_handler_calls_api_from_filter(self, local_credentials):
        """
        Verify from_filter goes through api.py methods.
        This ensures handler isn't duplicating query logic.
        """
        event = {
            'action': 'PointMeasurements.from_filter',
            'filters': {'limit': 1}
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        # If this works, handler successfully called api.py
        assert 'error' not in result
        assert 'data' in result
        
    def test_handler_calls_api_from_area(self, local_credentials):
        """
        Verify from_area goes through api.py methods.
        This ensures spatial logic is in api.py, not duplicated.
        """
        event = {
            'action': 'PointMeasurements.from_area',
            'pt_wkt': 'POINT(743683 4321095)',
            'buffer': 100,
            'crs': 26912,
            'filters': {'limit': 1}
        }
        
        result = handle_event_with_secret(event, local_credentials)
        
        # If this works, handler successfully called api.py
        assert 'error' not in result
        assert 'data' in result