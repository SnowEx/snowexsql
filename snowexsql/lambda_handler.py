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

def _setup_api_class(api_class, tmp_cred_path: str):
    """Configure the API class with the database credentials path."""
    api_class.DB_NAME = str(tmp_cred_path)
    return api_class

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
        _setup_api_class(api_class, tmp_cred_path)
        
        # Handle different method types
        if method_name == 'from_filter':
            filters = event.get('filters', {})
            records = _get_measurements_by_class(api_class, filters)
            action = f'{class_name}.{method_name}'
            return _create_response(action, records, filters=filters)
            
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

def _get_measurements_by_class(api_class, filters: dict):
    """Get measurements using a specific API class."""
    df = api_class.from_filter(**filters)
    records = df.to_dict('records') if hasattr(df, 'to_dict') else []
    return serialize_for_json(records)

def _write_temp_credentials(creds: Dict[str, Any], dest: Path):
    """
    Write the expected credentials.json structure used by
    snowexsql.db.load_credentials.

    The existing library expects a JSON file with top-level keys
    `production` and `tests`. We'll populate both entries from the
    secret (they can be the same).
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
    
    # Write both 'production' and 'tests' keys with the same
    # credentials. This ensures it works whether SNOWEXSQL_TESTS
    # env var is set or not
    payload = {
        'production': cred_entry,
        'tests': cred_entry
    }
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, 'w') as fh:
        json.dump(payload, fh)


def handle_event_with_secret(
    event: Dict[str, Any],
    secret: Dict[str, Any]
):
    """
    Main entry: write temporary credentials file and call into
    snowexsql API.

    Returns a JSON-serializable dict with the result.
    """
    tmp_cred_path = Path('/tmp/credentials.json')
    _write_temp_credentials(secret, tmp_cred_path)

    # The snowexsql.db functions accept a credentials_path parameter;
    # pass our temp file
    try:
        engine, session = sled_db.get_db(str(tmp_cred_path))
        
        # Get the action from the event, default to connectivity test
        action = event.get('action', 'test_connection')
        
        # Handle system-level actions
        if action == 'test_connection':
            return _test_connection(engine)
        
        # Handle raw SQL queries
        elif action == 'query':
            sql = event.get('sql')
            if not sql:
                return {'error': 'No SQL query provided'}
            
            try:
                result = session.execute(text(sql))
                # Convert result to list of dicts
                data = [dict(row._mapping) for row in result]
                serialized = serialize_for_json(data)
                return _create_response('query', serialized, sql=sql)
            except Exception as e:
                return _create_error_response('query', e)
    
        # Handle class-based actions (mirror api.py structure)
        elif '.' in action:
            # Parse class.method format
            # (e.g., 'PointMeasurements.from_filter')
            class_name, method_name = action.split('.', 1)
            return _handle_class_action(
                class_name,
                method_name,
                event,
                tmp_cred_path
            )
            
        else:
            return {'error': f'Unknown action: {action}'}
            
    finally:
        try:
            session.close() if 'session' in locals() else None
            tmp_cred_path.unlink()
        except Exception:
            pass

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
    