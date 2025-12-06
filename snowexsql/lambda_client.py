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
        
        try:
            response = self.lambda_client.invoke(
                FunctionName=self.function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            result = json.loads(response['Payload'].read().decode('utf-8'))
            return json.loads(result['body'])
            
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
    _DATAFRAME_METHODS = {'from_filter', 'from_area'}
    
    # Known methods that take special parameters
    _KNOWN_METHODS = {
        'from_filter': ['filters'],
        'from_unique_entries': ['columns', 'filters'], 
        'from_area': ['shp', 'pt', 'buffer', 'crs']
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
        def method_proxy(*args, **kwargs):
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

            # Invoke Lambda with the method call
            action = f'{self._class_name}.{method_name}'
            result = self._client._invoke_lambda(action, **kwargs)
            
            if 'error' in result:
                raise Exception(
                    f"Method call failed: {result['error']}"
                )
            
            # Smart return type handling based on method
            if method_name in self._DATAFRAME_METHODS:
                return pd.DataFrame(result['data'])
            else:
                return result['data']
        
        # Add helpful docstring to the proxy function
        method_proxy.__doc__ = (
            f"Proxy for {self._class_name}.{method_name}() - "
            f"calls Lambda backend"
        )
        method_proxy.__name__ = method_name
        
        return method_proxy
    
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