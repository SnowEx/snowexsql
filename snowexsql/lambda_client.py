"""
SnowEx Lambda API Client

Lightweight client for accessing SnowEx database via AWS Lambda
function. Provides serverless access to snow data without requiring
heavy geospatial dependencies.
"""

import boto3
import json
import pandas as pd
from typing import Dict, Any
from datetime import datetime, date


class SnowExLambdaClient:
    """
    Client for accessing SnowEx data via AWS Lambda
    
    This client provides serverless access to the SnowEx database through
    a deployed Lambda function, eliminating the need for direct database
    connections or heavy geospatial dependencies.
    
    The client mirrors the api.py class structure, providing access to:
    - PointMeasurements: Point data measurements  
    - LayerMeasurements: Layer/profile data measurements
    - RasterMeasurements: Raster/image data
    - System functions: DOI queries, connection testing
    
    Example:
        >>> client = SnowExLambdaClient()
        >>> client.test_connection()
        {'connected': True, 'version': 'PostgreSQL 17.6...'}
        
        >>> # Use class-based approach (mirrors api.py)
        >>> data = client.layer_measurements.from_filter(
        ...     instrument='reflectance', limit=10
        ... )
        >>> instruments = client.point_measurements.all_instruments
    """
    
    def __init__(
        self,
        region: str = 'us-west-2',
        function_name: str = 'lambda-snowex-sql'
    ):
        """
        Initialize the Lambda client
        
        Args:
            region: AWS region where the Lambda function is deployed
            function_name: Name of the deployed Lambda function
        """
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.function_name = function_name
        
        # Dynamically create class-based accessors from available
        # measurement classes
        self._create_measurement_clients()
    
    def query(self, sql_query: str) -> pd.DataFrame:
        """
        Execute a raw SQL query against the database via Lambda.
        
        Args:
            sql_query: Raw SQL query string to execute
            
        Returns:
            pd.DataFrame: Query results as a DataFrame
        """
        payload = {
            'action': 'query',
            'sql': sql_query
        }
        
        response = self.lambda_client.invoke(
            FunctionName=self.function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        result = json.loads(response['Payload'].read())
        
        if result.get('statusCode') != 200:
            raise Exception(f"Lambda query failed: {result.get('body')}")
        
        body = json.loads(result['body'])
        return pd.DataFrame(body.get('data', []))
    
    def _create_measurement_clients(self):
        """
        Dynamically create measurement client attributes based on
        available measurement classes.
        
        This method discovers measurement classes using the same
        convention as the Lambda handler:
        - Classes ending in 'Measurements' 
        - Available in the snowexsql.api module
        - Creates snake_case attributes
          (e.g., PointMeasurements -> point_measurements)
        """
        try:
            # Import here to avoid circular imports
            from snowexsql import api
            
            # Get all measurement classes using the same discovery
            # logic as lambda_handler
            measurement_classes = [
                name for name in dir(api) 
                if name.endswith('Measurements') and hasattr(api, name)
            ]
            
            # Create client attributes dynamically
            for class_name in measurement_classes:
                # Convert CamelCase to snake_case for attribute name
                attr_name = ''.join([
                    '_' + c.lower() if c.isupper() else c
                    for c in class_name
                ]).lstrip('_')
                
                # Create the client accessor
                setattr(
                    self,
                    attr_name,
                    _LambdaDatasetClient(self, class_name)
                )
                
        except ImportError as e:
            # If local discovery fails
            raise ImportError(
                f"Could not auto-discover measurement classes from "
                f"snowexsql.api: {e}. "
                "This usually indicates a packaging or import issue. "
                "Check that the snowexsql package is properly installed."
            )
    
    def get_measurement_classes(self):
        """
        Get all measurement client objects as a dictionary for easy unpacking.
        
        This method dynamically discovers all available measurement classes
        and returns them with their original CamelCase names, making it easy
        to use as drop-in replacements for direct API imports.
        
        Returns:
            Dict mapping class names (str) to client objects
            
        Example:
            >>> from snowexsql.lambda_client import SnowExLambdaClient
            >>> client = SnowExLambdaClient()
            >>> 
            >>> # Get all measurement classes
            >>> classes = client.get_measurement_classes()
            >>> PointMeasurements = classes['PointMeasurements']
            >>> LayerMeasurements = classes['LayerMeasurements']
            >>> 
            >>> # Use exactly like the direct API
            >>> df = PointMeasurements.from_filter(type='depth', limit=10)
            >>> df.plot(column='value', cmap='jet')
        """
        try:
            from snowexsql import api
            
            # Get all measurement classes
            measurement_classes = [
                name for name in dir(api) 
                if name.endswith('Measurements') and hasattr(api, name)
            ]
            
            # Build dictionary mapping class names to client objects
            result = {}
            for class_name in measurement_classes:
                # Convert CamelCase to snake_case to get the attribute name
                attr_name = ''.join([
                    '_' + c.lower() if c.isupper() else c
                    for c in class_name
                ]).lstrip('_')
                
                # Get the client object and map it to the original class name
                if hasattr(self, attr_name):
                    result[class_name] = getattr(self, attr_name)
            
            return result
            
        except ImportError as e:
            raise ImportError(
                f"Could not discover measurement classes: {e}"
            )
    
    def _serialize_payload(self, obj):
        """
        Recursively serialize payload objects to JSON-compatible format.
        
        Handles datetime objects and Shapely geometry objects by converting
        them to JSON-serializable formats.
        
        Args:
            obj: Object to serialize
            
        Returns:
            JSON-serializable version of the object
        """
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif hasattr(obj, '__geo_interface__'):
            # Handle Shapely geometry objects (Point, Polygon, etc.)
            return obj.__geo_interface__
        elif isinstance(obj, dict):
            return {key: self._serialize_payload(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._serialize_payload(item) for item in obj]
        else:
            return obj
    
    def _invoke_lambda(self, action: str, **kwargs) -> dict:
        """
        Internal method to invoke Lambda function
        
        Args:
            action: The action to perform
                (e.g., 'test_connection', 'get_layer_measurements')
            **kwargs: Additional parameters to pass to the Lambda
                function
            
        Returns:
            Dict containing the Lambda function response
            
        Raises:
            Exception: If Lambda invocation fails or returns an error
        """
        payload = {'action': action, **kwargs}
        
        # Serialize datetime objects and other non-JSON-serializable types
        payload = self._serialize_payload(payload)
        
        try:
            response = self.lambda_client.invoke(
                FunctionName=self.function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            result = json.loads(response['Payload'].read().decode('utf-8'))
            
            # Check if result has the expected structure
            if 'body' not in result:
                raise Exception(f"Unexpected Lambda response format: {result}")
            
            body = json.loads(result['body'])
            
            # Check for errors in the response
            if 'error' in body:
                raise Exception(f"Lambda returned error: {body['error']}")
            
            return body
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse Lambda response: {str(e)}")
        except Exception as e:
            raise Exception(f"Lambda invocation failed: {str(e)}")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test database connection through Lambda
        
        Returns:
            Dict with connection status and database version info
        """
        return self._invoke_lambda('test_connection')
    
class _LambdaDatasetClient:
    """
    Dynamic proxy client that automatically mirrors api.py
    BaseDataset classes
    
    This class uses Python's __getattr__ magic method to dynamically
    handle any method or property call, eliminating the need to
    manually synchronize with changes in the underlying API classes.
    
    Supported patterns:
    - Properties starting with 'all_': all_instruments,
      all_campaigns, etc.
    - Known methods: from_filter, from_unique_entries, from_area
    - Class-specific properties: all_sites (LayerMeasurements only)
    """
    
    # Known methods that return DataFrames
    _DATAFRAME_METHODS = {'from_filter', 'from_area', 'get_sites'}
    
    # Known methods that take special parameters
    _KNOWN_METHODS = {
        'from_filter': ['filters'],
        'from_unique_entries': ['columns', 'filters'], 
        'from_area': ['shp', 'pt', 'buffer', 'crs'],
        'get_sites': ['site_names']
    }
    
    def __init__(
        self,
        parent_client: SnowExLambdaClient,
        class_name: str
    ):
        self._client = parent_client
        self._class_name = class_name
    
    def __getattr__(self, name: str):
        """
        Dynamic attribute access - handles any property or method call
        
        This magic method is called when an attribute is accessed that
        doesn't exist on the object. It routes the call to the
        appropriate handler based on naming patterns.
        """
        
        # Pattern 1: Properties starting with 'all_'
        if name.startswith('all_'):
            return self._get_property(name)
        
        # Pattern 2: Known methods from BaseDataset
        elif name in self._KNOWN_METHODS:
            return self._create_method_proxy(name)
        
        # Pattern 3: Other potential methods (extensible)
        elif name.startswith('get_') or name.startswith('find_'):
            return self._create_method_proxy(name)
        
        # Pattern 4: Handle unknown attributes with helpful error
        else:
            methods_list = list(self._KNOWN_METHODS.keys())
            raise AttributeError(
                f"'{self._class_name}' has no attribute '{name}'. "
                f"Available patterns: all_* (properties), "
                f"{methods_list} (methods)"
            )
    
    def _create_method_proxy(self, method_name: str):
        """
        Create a proxy function for a method that will invoke Lambda
        
        Returns a callable that matches the signature of the original
        method
        """
        def method_proxy(*args, as_geodataframe=True, **kwargs):
            # Convert positional args to kwargs based on known method
            # signatures
            if args and method_name in self._KNOWN_METHODS:
                param_names = self._KNOWN_METHODS[method_name]
                for i, arg in enumerate(args):
                    if i < len(param_names):
                        kwargs[param_names[i]] = arg
            
            # Shape the payload to match what the Lambda handler
            # expects from_filter: expects a single 'filters' dict
            if method_name == 'from_filter':
                provided_filters = {}
                # If user provided an explicit filters dict, start
                # with it
                if 'filters' in kwargs and isinstance(
                    kwargs['filters'], dict
                ):
                    provided_filters.update(kwargs['filters'])
                    kwargs.pop('filters', None)
                # Move any remaining kwargs into filters
                for k in list(kwargs.keys()):
                    provided_filters[k] = kwargs.pop(k)
                # Now set the shaped kwargs
                kwargs = {'filters': provided_filters}

            # from_unique_entries: expects 'columns' list and
            # optional 'filters' dict
            elif method_name == 'from_unique_entries':
                columns = kwargs.get('columns')
                if columns is None and 'filters' in kwargs:
                    # In case user passed columns positionally earlier,
                    # it's already mapped
                    pass
                # Start filters from explicit dict if present
                provided_filters = {}
                if 'filters' in kwargs and isinstance(
                    kwargs['filters'], dict
                ):
                    provided_filters.update(kwargs['filters'])
                # Pull out recognized key 'columns'
                shaped = {}
                if columns is not None:
                    shaped['columns'] = columns
                # Move any unrecognized keys (besides
                # 'columns'/'filters') into filters
                for k in list(kwargs.keys()):
                    if k in ('columns', 'filters'):
                        continue
                    provided_filters[k] = kwargs[k]
                if provided_filters:
                    shaped['filters'] = provided_filters
                kwargs = shaped if shaped else kwargs

            # from_area: Handle server-side spatial filtering using PostGIS
            # Lambda uses PostGIS for efficient database-side spatial queries
            elif method_name == 'from_area':
                return self._handle_from_area_server_side(kwargs, as_geodataframe)

            # Invoke Lambda with the method call
            action = f'{self._class_name}.{method_name}'
            result = self._client._invoke_lambda(action, **kwargs)
            
            if 'error' in result:
                raise Exception(
                    f"Method call failed: {result['error']}"
                )
            
            # Smart return type handling based on method
            if method_name in self._DATAFRAME_METHODS:
                df = pd.DataFrame(result['data'])
                
                # Convert to GeoDataFrame if requested and possible
                if as_geodataframe and self._can_convert_to_geodataframe(df):
                    return self._to_geodataframe(df)
                
                return df
            else:
                return result['data']
        
        # Add helpful docstring to the proxy function
        method_proxy.__doc__ = (
            f"Proxy for {self._class_name}.{method_name}() - "
            f"calls Lambda backend\n\n"
            f"Args:\n"
            f"    as_geodataframe (bool): If True (default), return GeoDataFrame "
            f"when geometry data is available.\n"
            f"                           If False, return regular DataFrame.\n"
            f"                           Requires geopandas to be installed."
        )
        method_proxy.__name__ = method_name
        
        return method_proxy
    
    def _handle_from_area_server_side(self, kwargs: dict, as_geodataframe: bool):
        """
        Handle from_area() with server-side PostGIS spatial filtering
        
        Lambda uses PostGIS for efficient database-side spatial queries:
        1. Convert geometry to WKT (Well-Known Text) format
        2. Send to Lambda with other filters
        3. Lambda constructs PostGIS spatial query
        4. Database performs spatial filtering efficiently
        5. Return filtered results
        
        Args:
            kwargs: Parameters including pt/shp, buffer, crs, and other filters
            as_geodataframe: Whether to return as GeoDataFrame
            
        Returns:
            Filtered GeoDataFrame or DataFrame
        """
        try:
            from shapely.geometry import Point
        except ImportError:
            raise ImportError(
                "shapely is required for from_area(). "
                "Install with: pip install shapely"
            )
        
        # Extract spatial parameters
        pt = kwargs.pop('pt', None)
        shp = kwargs.pop('shp', None)
        buffer_dist = kwargs.pop('buffer', None)
        crs = kwargs.pop('crs', 4326)  # Default to WGS84
        
        # Validate parameters
        if pt is None and shp is None:
            raise ValueError("Either 'pt' or 'shp' parameter is required for from_area")
        
        if pt is not None and buffer_dist is None:
            raise ValueError("'buffer' parameter is required when using 'pt'")
        
        # Convert geometry to WKT for transmission to Lambda
        if pt is not None:
            # Convert point to WKT
            if isinstance(pt, Point):
                pt_wkt = pt.wkt
            elif isinstance(pt, (tuple, list)) and len(pt) == 2:
                pt_wkt = Point(pt[0], pt[1]).wkt
            else:
                raise ValueError("pt must be a shapely Point or (x, y) tuple")
            
            kwargs['pt_wkt'] = pt_wkt
            kwargs['buffer'] = buffer_dist
        else:
            # Convert shape to WKT
            if hasattr(shp, 'wkt'):
                kwargs['shp_wkt'] = shp.wkt
            else:
                raise ValueError("shp must be a shapely geometry object")
        
        kwargs['crs'] = crs
        
        # Remaining kwargs are filters
        filters = {}
        for k, v in list(kwargs.items()):
            if k not in ['pt_wkt', 'shp_wkt', 'buffer', 'crs']:
                filters[k] = kwargs.pop(k)
        
        if filters:
            kwargs['filters'] = filters
        
        # Invoke Lambda with PostGIS spatial query
        action = f'{self._class_name}.from_area'
        result = self._client._invoke_lambda(action, **kwargs)
        
        # Convert result to DataFrame
        df = pd.DataFrame(result.get('data', []))
        
        if df.empty:
            return df
        
        # Convert to GeoDataFrame if requested
        if as_geodataframe:
            df = self._to_geodataframe(df)
        
        return df
    
    def _can_convert_to_geodataframe(self, df: pd.DataFrame) -> bool:
        """
        Check if DataFrame can be converted to GeoDataFrame
        
        Args:
            df: DataFrame to check
            
        Returns:
            bool: True if conversion is possible
        """
        # Check for PostGIS geometry columns
        has_geometry = 'geometry' in df.columns
        has_geom = 'geom' in df.columns  # PostGIS column name
        
        return has_geometry or has_geom
    
    def _to_geodataframe(self, df: pd.DataFrame):
        """
        Convert pandas DataFrame to GeoDataFrame
        
        Handles PostGIS geometry columns returned from Lambda:
        - geom column from PostGIS databases (WKB hex, WKT, or GeoJSON dict)
        - geometry column already present
        
        Args:
            df: DataFrame to convert
            
        Returns:
            GeoDataFrame if conversion successful, otherwise original DataFrame
        """
        try:
            import geopandas as gpd
            from shapely import wkb, wkt
            from shapely.geometry import shape
            
            # Case 1: DataFrame has 'geom' column (PostGIS standard)
            if 'geom' in df.columns:
                if df['geom'].dtype == 'object':
                    # Try to parse as WKB hex string (most common from PostGIS)
                    try:
                        df['geometry'] = df['geom'].apply(
                            lambda x: wkb.loads(x, hex=True) if x else None
                        )
                        return gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
                    except Exception:
                        # Try as WKT string
                        try:
                            df['geometry'] = df['geom'].apply(lambda x: wkt.loads(x) if x else None)
                            return gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
                        except Exception:
                            # Try as GeoJSON __geo_interface__ dict
                            try:
                                df['geometry'] = df['geom'].apply(lambda x: shape(x) if x else None)
                                return gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
                            except:
                                pass  # Fall through to return original df
            
            # Case 2: DataFrame already has geometry column
            elif 'geometry' in df.columns:
                # Try to parse as WKT if it's a string
                if df['geometry'].dtype == 'object':
                    try:
                        df['geometry'] = df['geometry'].apply(lambda x: wkt.loads(x) if x else None)
                    except:
                        pass  # Already valid geometry or will fail below
                
                return gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
            
            # Case 3: No spatial data available
            return df
            
        except ImportError:
            # If geopandas not available, return regular DataFrame
            import warnings
            warnings.warn(
                "geopandas not installed. Returning pandas DataFrame. "
                "Install geopandas for spatial plotting: pip install geopandas",
                UserWarning
            )
            return df
        except Exception as e:
            # If conversion fails for any other reason
            import warnings
            warnings.warn(
                f"Could not convert to GeoDataFrame: {e}. "
                f"Returning pandas DataFrame.",
                UserWarning
            )
            return df
    
    def _get_property(self, property_name: str):
        """Handle property access via Lambda"""
        action = f'{self._class_name}.{property_name}'
        result = self._client._invoke_lambda(action)
        if 'error' in result:
            raise Exception(
                f"Property access failed: {result['error']}"
            )
        return result['data']
    
    def __repr__(self):
        """Helpful representation for debugging"""
        return f"<{self._class_name}Client via Lambda>"


# Convenience function for quick client creation
def create_client(
    region: str = 'us-west-2',
    function_name: str = 'lambda-snowex-sql'
) -> SnowExLambdaClient:
    """
    Create a SnowExLambdaClient instance
    
    Args:
        region: AWS region where the Lambda function is deployed
        function_name: Name of the deployed Lambda function
        
    Returns:
        SnowExLambdaClient instance
    """
    return SnowExLambdaClient(region=region, function_name=function_name)