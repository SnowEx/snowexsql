"""
Lambda-specific helper that exposes a function the container entrypoint
can call.

This module adapts the existing snowexsql db helpers to accept credentials
provided at runtime via a temporary credentials.json file written from
Secrets Manager. It also exposes the core API functionality from api.py
for serverless usage.

DEVELOPER NOTE: This module automatically discovers measurement classes
from api.py based on naming conventions. See _get_measurement_classes()
for detailed requirements.
"""
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, date
import pandas as pd
import numpy as np

from snowexsql import db as sled_db
from sqlalchemy import text

LOG = logging.getLogger(__name__)

LOG.info("Using standard API classes")

def deserialize_geometry(geom_dict):
    """Convert GeoJSON dict back to Shapely geometry"""
    try:
        from shapely.geometry import shape
        return shape(geom_dict)
    except ImportError:
        raise ImportError(
            "shapely is required for geometric operations. "
            "Install with: pip install shapely"
        )

def serialize_for_json(obj):
    """Convert pandas DataFrame records to JSON-serializable format"""
    if isinstance(obj, list):
        return [serialize_for_json(item) for item in obj]
    elif isinstance(obj, dict):
        return {
            key: serialize_for_json(value)
            for key, value in obj.items()
        }
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, (pd.Timestamp, pd.NaT.__class__)):
        return obj.isoformat() if pd.notna(obj) else None
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif pd.isna(obj):
        return None
    elif hasattr(obj, '__geo_interface__'):
        # Handle shapely geometries
        return obj.__geo_interface__
    elif str(type(obj)).endswith("WKBElement'>"):
        # Handle geoalchemy2 WKBElement objects
        try:
            # Convert to WKT (Well-Known Text) format for JSON
            return str(obj)
        except Exception:
            return None
    else:
        return obj


def _test_connection(engine):
    """Test database connectivity and return version info."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        ver = result.fetchone()[0]
    return {'connected': True, 'version': ver}

def _create_response(action: str, data, **kwargs):
    """
    Create a standardized response format for successful operations.
    """
    response = {
        'action': action,
        'data': data
    }
    
    # Add count if data is a list
    if isinstance(data, list):
        response['count'] = len(data)
    
    # Add any additional metadata
    response.update(kwargs)
    
    return response

def _create_error_response(action: str, error: Exception):
    """Create a standardized error response format."""
    return {'error': f'{action} failed: {str(error)}'}

def _get_measurement_classes():
    """
    Dynamically discover measurement classes from the api module.
    
    To make a new measurement class available via Lambda,
    it must follow these conventions:
    
    1. Class name MUST end with 'Measurements'
       (e.g., WeatherMeasurements)
    2. Class MUST have a 'MODEL' attribute pointing to the
       SQLAlchemy model
    3. Class MUST inherit from BaseDataset (directly or indirectly)
    
    Example:
        class WeatherMeasurements(BaseDataset):
            MODEL = WeatherData  # Required!
            # ... your implementation ...
    
    The class will then be automatically available as:
        client.weather_measurements.from_filter()
        client.weather_measurements.all_instruments
        etc.
    
    Returns:
        dict: Mapping of class names to class objects
    """
    import snowexsql.api as api_module
    
    measurement_classes = {}
    discovered_classes = []
    
    for name in dir(api_module):
        if name.endswith('Measurements'):
            cls = getattr(api_module, name)
            # Verify it's a proper measurement class
            if hasattr(cls, 'MODEL') and callable(cls):
                measurement_classes[name] = cls
                discovered_classes.append(name)
    
    # Log what was discovered for debugging
    LOG.info(
        f"Auto-discovered measurement classes: {discovered_classes}"
    )
    
    if not measurement_classes:
        LOG.warning(
            "No measurement classes found! Check naming conventions "
            "in api.py"
        )
    
    return measurement_classes


def validate_measurement_class(cls, class_name: str) -> bool:
    """
    Validate that a class follows the measurement class conventions.
    
    This is a helper for developers to check if their new classes
    will work. You can call this manually in tests or during
    development.
    """
    issues = []
    
    if not class_name.endswith('Measurements'):
        issues.append(
            f"Class name '{class_name}' should end with 'Measurements'"
        )
    
    if not hasattr(cls, 'MODEL'):
        issues.append(
            f"Class '{class_name}' missing required MODEL attribute"
        )
    
    if not callable(cls):
        issues.append(
            f"'{class_name}' is not callable (not a class?)"
        )
    
    # Check if it has expected BaseDataset methods
    expected_methods = ['from_filter', 'from_unique_entries']
    for method in expected_methods:
        if not hasattr(cls, method):
            issues.append(
                f"Class '{class_name}' missing expected method "
                f"'{method}'"
            )
    
    if issues:
        LOG.warning(
            f"Class '{class_name}' validation issues: {issues}"
        )
        return False
    
    LOG.info(f"Class '{class_name}' passes validation ✓")
    return True

def _handle_class_action(
    class_name: str,
    method_name: str,
    event: dict,
    tmp_cred_path: str
):
    """Handle class-based actions that mirror the api.py structure."""
    try:
        # Dynamically discover available measurement classes
        allowed_classes = _get_measurement_classes()
        
        if class_name not in allowed_classes:
            available = list(allowed_classes.keys())
            raise ValueError(
                f'Unknown class: {class_name}. Available: {available}'
            )
        
        api_class = allowed_classes[class_name]
        
        # Handle different method types
        if method_name == 'from_filter':
            filters = event.get('filters', {})
            # Extract verbose parameter before passing to from_filter
            verbose = filters.pop('verbose', False)
            records = _get_measurements_by_class(api_class, filters, verbose=verbose)
            action = f'{class_name}.{method_name}'
            return _create_response(action, records, filters=filters)
            
        elif method_name == 'from_area':
            # Call api.py from_area method directly (it now uses PostGIS SQL)
            pt_wkt = event.get('pt_wkt')
            shp_wkt = event.get('shp_wkt')
            buffer_dist = event.get('buffer')
            crs = event.get('crs', 26912)
            filters = event.get('filters', {})
            # Extract verbose parameter before passing to from_area
            verbose = filters.pop('verbose', False)
            
            # Set credentials for api.py to use
            os.environ['SNOWEX_DB_CREDENTIALS_FILE'] = tmp_cred_path
            
            try:
                df = api_class.from_area(
                    shp=shp_wkt,
                    pt=pt_wkt,
                    buffer=buffer_dist,
                    crs=crs,
                    verbose=verbose,
                    **filters
                )
                records = df.to_dict('records')
                action = f'{api_class.__name__}.from_area'
                return _create_response(action, serialize_for_json(records), count=len(records))
            except Exception as e:
                raise Exception(f"from_area query failed: {str(e)}")
            
        elif method_name == 'from_unique_entries':
            columns = event.get('columns', [])
            filters = event.get('filters', {})
            if not columns:
                raise ValueError('columns parameter is required')
            result = api_class.from_unique_entries(columns, **filters)
            action = f'{class_name}.{method_name}'
            return _create_response(
                action,
                serialize_for_json(result),
                columns=columns
            )
            
        elif method_name.startswith('all_'):
            # Handle property-like methods
            # (all_instruments, all_campaigns, etc.)
            api_instance = api_class()
            if hasattr(api_instance, method_name):
                result = getattr(api_instance, method_name)
                action = f'{class_name}.{method_name}'
                return _create_response(action, result)
            else:
                raise ValueError(
                    f'Property {method_name} not found on {class_name}'
                )
                
        else:
            raise ValueError(f'Unsupported method: {method_name}')
            
    except Exception as e:
        return _create_error_response(
            f'{class_name}.{method_name}',
            e
        )

def _get_measurements_by_class(api_class, filters: dict, verbose: bool = False):
    """
    Get measurements by calling api.py methods directly.
    Single source of truth for query logic.
    """
    df = api_class.from_filter(verbose=verbose, **filters)
    records = df.to_dict('records') if hasattr(df, 'to_dict') else []
    return serialize_for_json(records)

def _write_temp_credentials(creds: Dict[str, Any], dest: Path):
    """
    Write credentials in flat format expected by snowexsql.db.load_credentials.
    
    AWS Secrets Manager secret should contain:
    - username (or user or db_user)
    - password
    - host (or address)
    - dbname (or database or db_name)
    """
    cred_entry = {
        'username': (creds.get('username') or
                    creds.get('user') or
                    creds.get('db_user')),
        'password': creds.get('password'),
        'address': creds.get('host') or creds.get('address'),
        'db_name': (creds.get('dbname') or
                   creds.get('database') or
                   creds.get('db_name'))
    }
    
    # Validate all required fields are present
    missing = [k for k, v in cred_entry.items() if not v]
    if missing:
        LOG.error(f"Missing credential fields: {missing}")
        LOG.error(f"Available secret keys: {list(creds.keys())}")
        raise ValueError(f"Missing required credential fields: {missing}")
    
    # Write flat structure (NOT nested with production/tests keys)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, 'w') as fh:
        json.dump(cred_entry, fh, indent=2)
    
    LOG.info(f"Wrote credentials to {dest}")

def handle_event_with_secret(event: Dict[str, Any], secret_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle an event with credentials from AWS Secrets Manager.
    
    Args:
        event: Lambda event containing action and parameters
        secret_dict: Credentials from Secrets Manager
        
    Returns:
        Response dictionary with results or error
    """
    tmp_creds = Path('/tmp/credentials.json')
    
    try:
        # Write credentials in flat format expected by snowexsql.db
        _write_temp_credentials(secret_dict, tmp_creds)
        
        # Verify credentials file was written and is readable
        if not tmp_creds.exists():
            raise FileNotFoundError(f"Failed to write credentials to {tmp_creds}")
        
        # Log for debugging (without exposing password)
        with open(tmp_creds) as f:
            creds_check = json.load(f)
            LOG.info(f"Credentials file keys: {list(creds_check.keys())}")
        
        # Set environment variable so API classes can find credentials
        # This is critical because api.py classes call db_session_with_credentials()
        # without passing credentials_path parameter
        os.environ['SNOWEX_DB_CREDENTIALS'] = str(tmp_creds)
        
        # Get database connection with explicit credentials path
        engine, session = sled_db.get_db(credentials_path=str(tmp_creds))
        
        # Test connection
        if event.get('action') == 'test_connection':
            result = _test_connection(engine)
            session.close()
            return result
        
        # Handle class-based actions (e.g., PointMeasurements.from_filter)
        action = event.get('action', '')
        if '.' in action:
            class_name, method_name = action.split('.', 1)
            result = _handle_class_action(
                class_name,
                method_name,
                event,
                str(tmp_creds)
            )
            session.close()
            return result
        
        # Handle raw SQL queries
        if action == 'query':
            sql = event.get('sql')
            if not sql:
                raise ValueError('SQL query not provided')
            
            result = session.execute(text(sql))
            rows = [dict(row._mapping) for row in result]
            session.close()
            return _create_response('query', serialize_for_json(rows))
        
        session.close()
        raise ValueError(f'Unknown action: {action}')
        
    except Exception as e:
        LOG.error(f"Error in handle_event_with_secret: {str(e)}", exc_info=True)
        if 'session' in locals():
            session.close()
        return {
            'error': str(e),
            'action': event.get('action', 'unknown')
        }

def _get_secret(
    secret_name: str,
    region_name: str = None
) -> Dict[str, Any]:
    """
    Retrieve a secret from AWS Secrets Manager and return it as a dict.

    This duplicates the minimal logic previously in the lambda-api
    wrapper so the package can be used as the Lambda entrypoint directly.
    """
    import boto3
    import json
    import base64
    from botocore.exceptions import ClientError

    client_kwargs = {}
    if region_name:
        client_kwargs['region_name'] = region_name
    client = boto3.client('secretsmanager', **client_kwargs)
    try:
        resp = client.get_secret_value(SecretId=secret_name)
    except ClientError:
        LOG.exception('Error fetching secret %s', secret_name)
        raise

    if 'SecretString' in resp and resp['SecretString']:
        try:
            return json.loads(resp['SecretString'])
        except json.JSONDecodeError:
            return {'raw': resp['SecretString']}
    else:
        decoded = base64.b64decode(resp['SecretBinary']).decode('utf-8')
        return json.loads(decoded)


def lambda_handler(event: Dict[str, Any], context: Any):
    """
    AWS Lambda entrypoint: fetch DB secret and delegate to
    handle_event_with_secret.

    This is the function the Lambda runtime will call when we set the
    handler to `snowexsql.lambda_handler.lambda_handler` in the
    container CMD.
    """
    secret_name = os.environ.get('DB_SECRET_NAME')
    region = os.environ.get('DB_AWS_REGION')

    if not secret_name:
        LOG.error('DB_SECRET_NAME not set in environment')
        error_body = json.dumps('DB_SECRET_NAME not set')
        return {'statusCode': 500, 'body': error_body}

    try:
        secret = _get_secret(secret_name, region)
    except Exception as e:
        error_body = json.dumps({'error': str(e)})
        return {'statusCode': 500, 'body': error_body}

    try:
        result = handle_event_with_secret(event, secret)
        return {'statusCode': 200, 'body': json.dumps(result)}
    except Exception as e:
        LOG.exception('Handler failed')
        error_body = json.dumps({'error': str(e)})
        return {'statusCode': 500, 'body': error_body}
    