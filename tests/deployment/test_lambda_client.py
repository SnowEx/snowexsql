"""
Test the Lambda CLIENT (lambda_client.py) functionality.

Tests the SnowExLambdaClient class that makes requests to the deployed 
Lambda function. This tests:
- Client-side logic and API interface
- Full round-trip: client → Lambda → database → client
- GeoDataFrame conversion on client-side

These are END-TO-END tests requiring a deployed Lambda function.
Mark with @pytest.mark.integration to run separately.
"""

import pytest
import pandas as pd
from snowexsql.lambda_client import SnowExLambdaClient

# Check if geopandas is available for testing
try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False


@pytest.fixture(scope="module")
def lambda_client():
    """Fixture to provide a SnowExLambdaClient instance for all tests"""
    return SnowExLambdaClient()


# ========================================================================
# CONNECTION TESTS
# ========================================================================

@pytest.mark.integration
class TestClientConnection:
    """Test client connection and basic functionality"""
    
    def test_lambda_connection(self, lambda_client):
        """Test the deployed Lambda function connection"""
        result = lambda_client.test_connection()
        assert result.get('connected'), "Lambda connection failed"
        assert result.get('version'), "Database version not returned"
        assert 'PostgreSQL' in result.get('version', '')
        
    def test_raw_query(self, lambda_client):
        """Test raw SQL query through client"""
        result = lambda_client.query("SELECT 1 as test_value;")
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0


# ========================================================================
# MEASUREMENT CLASS INTERFACE TESTS
# ========================================================================

@pytest.mark.integration
class TestPointMeasurementsClient:
    """Test PointMeasurements through client"""
    
    def test_point_all_instruments(self, lambda_client):
        """Test accessing all_instruments property"""
        instruments = lambda_client.point_measurements.all_instruments
        assert isinstance(instruments, list)
        assert len(instruments) > 0
        
    def test_point_all_campaigns(self, lambda_client):
        """Test accessing all_campaigns property"""
        campaigns = lambda_client.point_measurements.all_campaigns
        assert isinstance(campaigns, list)
        assert len(campaigns) > 0
        
    def test_point_from_filter(self, lambda_client):
        """Test from_filter method"""
        df = lambda_client.point_measurements.from_filter(limit=5)
        assert isinstance(df, (pd.DataFrame, gpd.GeoDataFrame))
        assert len(df) <= 5
        
    def test_point_from_filter_with_filters(self, lambda_client):
        """Test from_filter with multiple filters"""
        instruments = lambda_client.point_measurements.all_instruments
        if instruments:
            df = lambda_client.point_measurements.from_filter(
                instrument=instruments[0],
                limit=3
            )
            assert isinstance(df, (pd.DataFrame, gpd.GeoDataFrame))
            assert len(df) <= 3


@pytest.mark.integration
class TestLayerMeasurementsClient:
    """Test LayerMeasurements through client"""
    
    def test_layer_all_instruments(self, lambda_client):
        """Test accessing all_instruments property"""
        instruments = lambda_client.layer_measurements.all_instruments
        assert isinstance(instruments, list)
        
    def test_layer_from_filter(self, lambda_client):
        """Test from_filter method"""
        df = lambda_client.layer_measurements.from_filter(limit=5)
        assert isinstance(df, (pd.DataFrame, gpd.GeoDataFrame))
        assert len(df) <= 5
        
    def test_layer_from_unique_entries(self, lambda_client):
        """Test from_unique_entries method"""
        result = lambda_client.layer_measurements.from_unique_entries(
            columns=['depth'],
            limit=10
        )
        assert isinstance(result, list)


# ========================================================================
# SPATIAL QUERY TESTS
# ========================================================================

@pytest.mark.integration
class TestClientSpatialQueries:
    """Test spatial queries through client"""
    
    def test_from_area_with_point_buffer(self, lambda_client):
        """Test from_area with point and buffer"""
        # Use a point in Grand Mesa area
        df = lambda_client.point_measurements.from_area(
            pt=(743683, 4321095),
            buffer=1000,
            crs=26912,
            limit=10
        )
        assert isinstance(df, (pd.DataFrame, gpd.GeoDataFrame))
        
    def test_from_area_with_geodataframe_conversion(self, lambda_client):
        """Test that from_area returns GeoDataFrame when requested"""
        df = lambda_client.point_measurements.from_area(
            pt=(743683, 4321095),
            buffer=500,
            crs=26912,
            as_geodataframe=True,
            limit=5
        )
        
        if HAS_GEOPANDAS and len(df) > 0:
            # Should be GeoDataFrame with geometry column
            assert isinstance(df, gpd.GeoDataFrame)
            assert 'geometry' in df.columns or 'geom' in df.columns
            
    def test_from_area_as_dataframe(self, lambda_client):
        """Test that from_area can return plain DataFrame"""
        df = lambda_client.point_measurements.from_area(
            pt=(743683, 4321095),
            buffer=500,
            crs=26912,
            as_geodataframe=False,
            limit=5
        )
        
        # Should be plain DataFrame (not GeoDataFrame)
        assert isinstance(df, pd.DataFrame)


# ========================================================================
# CLIENT-SIDE CONVERSION TESTS
# ========================================================================

@pytest.mark.integration
@pytest.mark.skipif(not HAS_GEOPANDAS, reason="geopandas required")
class TestClientGeoConversion:
    """Test client-side GeoDataFrame conversion"""
    
    def test_geodataframe_conversion(self, lambda_client):
        """Test that client converts to GeoDataFrame properly"""
        df = lambda_client.point_measurements.from_filter(
            limit=3,
            as_geodataframe=True
        )
        
        if len(df) > 0:
            assert isinstance(df, gpd.GeoDataFrame)
            # Should have geometry column
            assert hasattr(df, 'geometry')
            
    def test_geometry_column_parsing(self, lambda_client):
        """Test that geometry is properly parsed from WKT/WKB"""
        df = lambda_client.point_measurements.from_filter(
            limit=1,
            as_geodataframe=True
        )
        
        if len(df) > 0 and isinstance(df, gpd.GeoDataFrame):
            # Geometry should be Shapely objects, not strings
            geom = df.iloc[0].geometry
            assert hasattr(geom, 'geom_type')
            assert geom.geom_type in ['Point', 'Polygon', 'LineString']


# ========================================================================
# ERROR HANDLING TESTS
# ========================================================================

@pytest.mark.integration
class TestClientErrorHandling:
    """Test client error handling"""
    
    def test_invalid_method(self, lambda_client):
        """Test client handles invalid method gracefully"""
        with pytest.raises(Exception):
            lambda_client.point_measurements.nonexistent_method()
            
    def test_invalid_filter_parameter(self, lambda_client):
        """Test client handles invalid filter parameters"""
        # This should still work but might return empty results
        df = lambda_client.point_measurements.from_filter(
            instrument='definitely_not_a_real_instrument_name',
            limit=1
        )
        assert isinstance(df, (pd.DataFrame, gpd.GeoDataFrame))


# ========================================================================
# RESPONSE FORMAT TESTS
# ========================================================================

@pytest.mark.integration
class TestClientResponseFormats:
    """Test that client properly formats responses"""
    
    def test_property_returns_list(self, lambda_client):
        """Test that property accessors return lists"""
        result = lambda_client.point_measurements.all_instruments
        assert isinstance(result, list)
        
    def test_from_filter_returns_dataframe(self, lambda_client):
        """Test that from_filter returns DataFrame"""
        result = lambda_client.point_measurements.from_filter(limit=1)
        assert isinstance(result, (pd.DataFrame, gpd.GeoDataFrame))
        
    def test_from_unique_entries_returns_list(self, lambda_client):
        """Test that from_unique_entries returns list"""
        result = lambda_client.point_measurements.from_unique_entries(
            columns=['instrument'],
            limit=5
        )
        assert isinstance(result, list)
