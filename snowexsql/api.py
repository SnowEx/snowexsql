"""
SnowEx API for querying measurement data.

LAMBDA INTEGRATION CONVENTIONS:
===============================
If you're adding a new measurement class that should be available
via the Lambda API, follow these naming conventions:

1. Class name MUST end with 'Measurements'
   (e.g., WeatherMeasurements)
2. Class MUST have a 'MODEL' attribute pointing to the SQLAlchemy
   model
3. Class MUST inherit from BaseDataset

Example:
    class WeatherMeasurements(BaseDataset):
        MODEL = WeatherData  # Required for Lambda auto-discovery!
        
        # Your implementation here...

The Lambda handler will automatically discover and expose your
class as:
    client.weather_measurements.from_filter()
    client.weather_measurements.all_instruments
    etc.

See snowexsql.lambda_handler._get_measurement_classes() for
implementation details.
"""
import logging
import os
from contextlib import contextmanager

from sqlalchemy.sql import func
from sqlalchemy import cast, Numeric, exists, literal, select

# Initialize logger first
LOG = logging.getLogger(__name__)

# Import pandas - always available
import pandas as pd
from sqlalchemy.dialects import postgresql

def query_to_geopandas(query, engine, **kwargs):
    """
    Convert SQLAlchemy query to GeoDataFrame (if geopandas available)
    or DataFrame.
    
    Execution context:
    - Local power users: Returns GeoDataFrame with proper geometry objects
    - Lambda environment: Returns pandas DataFrame (no geopandas dependency)
      - DataFrame is serialized to JSON by lambda_handler
      - lambda_client receives JSON and converts to GeoDataFrame client-side
    
    Args:
        query: SQLAlchemy Query object
        engine: SQLAlchemy engine
        **kwargs: Additional arguments passed to read_postgis or read_sql
        
    Returns:
        geopandas.GeoDataFrame if geopandas available,
        otherwise pandas.DataFrame
    """
    sql = query.statement.compile(dialect=postgresql.dialect())
    
    try:
        import geopandas as gpd
        return gpd.read_postgis(sql, engine.connect(), **kwargs)
    except ImportError:
        # Geopandas not available (e.g., Lambda environment)
        # Returns pandas DataFrame with geometry as WKB/WKT
        # lambda_client will convert to GeoDataFrame client-side
        return pd.read_sql(sql, engine, **kwargs)

def raster_to_rasterio(rasters):
    """Raster functionality requires rasterio"""
    raise ImportError(
        "Raster functionality not available in Lambda environment. "
        "Use local API for raster operations."
    )
from snowexsql.db import get_db
from snowexsql.tables import (
    Campaign, CampaignObservation, DOI, ImageData, ImageObservation, Instrument,
    LayerData, MeasurementType, Observer, PointData, PointObservation, Site
)
from snowexsql.db import db_session_with_credentials

# TODO:
#   * Possible enums
#   * implement 'like' or 'contains' method


class LargeQueryCheckException(RuntimeError):
    pass

def get_points():
    # Lets grab a single row from the points table
    with db_session_with_credentials() as (_engine, session):
        qry = session.query(PointData).limit(1)
        # Execute that query!
        result = qry.all()


class BaseDataset:
    MODEL = None

    ALLOWED_QRY_KWARGS = [
        "campaign", "date", "instrument", "type",
        "utm_zone", "date_greater_equal", "date_less_equal",
        "value_greater_equal", 'value_less_equal', "doi",
        "observer"
    ]
    SPECIAL_KWARGS = ["limit"]
    # Default max record count
    MAX_RECORD_COUNT = 1000

    @staticmethod
    def retrieve_single_value_result(result):
        """
        When we only request a single thing we still get a list of
        lists this function filters it out. This usually looks like a
        list of tuples.
        """
        final = []
        if len(result) != 0:
            final = [r[0] for r in result]
        return final
    
    @classmethod
    def _build_select_clause(cls, verbose=False):
        """
        Build the SELECT clause for queries.
        Override in subclasses to customize columns returned based on verbose
        mode.
        
        Args:
            verbose: If True, return denormalized data with related table 
            columns
            
        Returns:
            List of SQLAlchemy column expressions for session.query()
        """
        # Default: just return the model (all its direct columns)
        return [cls.MODEL]
    
    @classmethod
    def _check_size(cls, qry, kwargs):
        # Safeguard against accidental giant requests
        count = qry.count()
        if count > cls.MAX_RECORD_COUNT and "limit" not in kwargs:
            raise LargeQueryCheckException(
                f"Query will return {count} number of records,"
                f" but we have a default max of {cls.MAX_RECORD_COUNT}."
                f" If you want to proceed, set the 'limit' filter"
                f" to the desired number of records."
            )

    @classmethod
    def _filter_campaign(cls, qry, v):
        qry = qry.filter(
            Site.campaign.has(Campaign.name == v)
        )
        return qry

    @classmethod
    def _filter_observers(cls, qry, v):
        qry = qry.join(
            cls.MODEL.observers
        ).filter(Observer.name == v)
        return qry

    @classmethod
    def _filter_instrument(cls, qry, value):
        return qry.filter(
            cls.MODEL.instrument.has(name=value)
        )

    @classmethod
    def _filter_measurement_type(cls, qry, value):
        return qry.join(
            cls.MODEL.measurement_type
        ).filter(MeasurementType.name == value)

    @classmethod
    def _filter_doi(cls, qry, value):
        return qry.join(cls.MODEL.doi).filter(DOI.doi == value)

    @classmethod
    def extend_qry(cls, qry, check_size=True, **kwargs):
        if cls.MODEL is None:
            raise ValueError("You must use a class with a MODEL.")

        # use the default kwargs
        for k, v in kwargs.items():
            # Handle special operations
            if k in cls.ALLOWED_QRY_KWARGS:

                qry_model = cls.MODEL
                # Logic for filtering on date with LayerData
                if "date" in k and cls.MODEL == LayerData:
                    qry = qry.join(LayerData.site)
                    qry_model = Site
                elif cls.MODEL == PointData:
                    qry = qry.join(PointData.observation)

                # standard filtering using qry.filter
                if isinstance(v, list):
                    filter_col = getattr(qry_model, k)
                    if k == "date":
                        raise ValueError(
                            "We cannot search for a list of dates"
                        )
                    elif "_equal" in k:
                        raise ValueError(
                            "We cannot compare greater_equal or "
                            "less_equal with a list"
                        )
                    elif k == "site":
                        # Skip list handling here, will be handled below
                        pass
                    else:
                        qry = qry.filter(filter_col.in_(v))
                        LOG.debug(
                            f"Filtering {k} to value {v}"
                        )
                else:
                    # Filter boundary
                    if "_greater_equal" in k:
                        key = k.split("_greater_equal")[0]
                        if key == "value":
                            qry = qry.filter(
                                cast(getattr(qry_model, key), Numeric) >= v
                            )
                        else:
                            qry = qry.filter(
                                getattr(qry_model, key) >= v
                            )
                    elif "_less_equal" in k:
                        key = k.split("_less_equal")[0]
                        if key == "value":
                            qry = qry.filter(
                                cast(getattr(qry_model, key), Numeric) <= v
                            )
                        else:
                            qry = qry.filter(
                                getattr(qry_model, key) <= v
                            )
                    # Filter linked columns
                    elif k == "instrument":
                        qry = cls._filter_instrument(qry, v)
                    elif k == "campaign":
                        qry = cls._filter_campaign(qry, v)
                    elif k == "site":
                        # Handle list of site names
                        if isinstance(v, list):
                            qry = qry.filter(
                                exists().where(
                                    qry_model.site_id == Site.id
                                ).where(
                                    Site.name.in_(v)
                                )
                            )
                        else:
                            qry = qry.filter(
                                qry_model.site.has(name=v)
                            )
                    elif k == "observer":
                        qry = cls._filter_observers(qry, v)
                    elif k == "doi":
                        qry = cls._filter_doi(qry, v)
                    elif k == "type":
                        qry = cls._filter_measurement_type(qry, v)
                    # Filter to exact value
                    else:
                        qry = qry.filter(
                            getattr(qry_model, k) == v
                        )
                    LOG.debug(
                        f"Filtering {k} to list {v}"
                    )

            # to avoid limit before filter
            elif k in cls.SPECIAL_KWARGS:
                if k == "limit":
                    qry = qry.limit(v)
            else:
                # Error out for not-allowed kwargs
                raise ValueError(f"{k} is not an allowed filter")

        if check_size:
            cls._check_size(qry, kwargs)

        return qry

    @classmethod
    def from_unique_entries(cls, columns_to_search, **kwargs):
        """
        Returns unique values from a column to help with filtering
        """
        columns = [
            getattr(cls.MODEL, column)
            for column in columns_to_search
        ]

        with db_session_with_credentials() as (_engine, session):
            try:
                qry = session.query(*columns)
                # Hardcode the limit to
                qry = cls.extend_qry(qry, check_size=False, **kwargs)
                results = qry.distinct().all()

            except Exception as e:
                session.close()
                LOG.error(
                    "Failed query finding options for filtering"
                )
                raise e

        if len(columns_to_search) == 1:
            results = cls.retrieve_single_value_result(results)

        return results

    @classmethod
    def from_filter(cls, verbose=False, **kwargs):
        """
        Get data for the class by filtering by allowed arguments. The allowed
        filters are cls.ALLOWED_QRY_KWARGS.
        
        Args:
            verbose: If True, return denormalized data with related table 
            columns
            **kwargs: Filter arguments from ALLOWED_QRY_KWARGS
        """
        with db_session_with_credentials() as (engine, session):
            try:
                select_clause = cls._build_select_clause(verbose)
                qry = session.query(*select_clause)
                
                # Add explicit joins for verbose mode to avoid cartesian 
                # products
                if verbose and hasattr(cls, '_add_verbose_joins'):
                    qry = cls._add_verbose_joins(qry)
                elif hasattr(cls, '_add_base_joins'):
                    # For verbose=False, still need basic joins (e.g., 
                    # Site for geom)
                    qry = cls._add_base_joins(qry)
                
                qry = cls.extend_qry(qry, **kwargs)

                # For debugging in the test suite and not
                # recommended in production
                # https://docs.sqlalchemy.org/en/20/faq/
                # sqlexpressions.html#rendering-postcompile-
                # parameters-as-bound-parameters
                if 'DEBUG_QUERY' in os.environ:
                    full_sql_query = qry.statement.compile(
                        compile_kwargs={"literal_binds": True}
                    )
                    print("\n ** SQL query **")
                    print(full_sql_query)

                df = query_to_geopandas(qry, engine)
            except Exception as e:
                session.close()
                LOG.error("Failed query for PointData")
                raise e

        return df

    @classmethod
    def from_area(
        cls, verbose=False, shp=None, pt=None, buffer=None, crs=26912, **kwargs
    ):
        """
        Get data for the class within a specific shapefile or
        within a point and a known buffer. Uses PostGIS functions via ORM
        for spatial operations, eliminating dependency on geoalchemy2/shapely.
        
        Args:
            verbose: If True, return denormalized data with related table 
            columns
            shp: shapely geometry in which to filter, or WKT string
            pt: shapely point that will have a buffer applied, or WKT string
            buffer: buffer distance in same units as point
                    (meters if using geography)
            crs: integer SRID/EPSG code (default 26912 = UTM Zone 12N)
            kwargs: for more filtering or limiting (cls.ALLOWED_QRY_KWARGS)
            
        Returns: 
            pandas DataFrame with results (includes geom column with WKT)
        """
        
        if shp is None and pt is None:
            raise ValueError(
                "Inputs must be a shape description or a point "
                "and buffer"
            )
        if ((pt is not None and buffer is None) or
                (buffer is not None and pt is None)):
            raise ValueError(
                "pt and buffer must be given together"
            )
        
        # Convert shapely objects to WKT if needed
        if shp is not None and hasattr(shp, 'wkt'):
            shp_wkt = shp.wkt
        elif isinstance(shp, str):
            shp_wkt = shp
        else:
            shp_wkt = None
            
        if pt is not None:
            if hasattr(pt, 'wkt'):
                pt_wkt = pt.wkt
            elif isinstance(pt, str):
                pt_wkt = pt
            elif isinstance(pt, (tuple, list)) and len(pt) == 2:
                # Handle (x, y) tuple format
                pt_wkt = f"POINT ({pt[0]} {pt[1]})"
            else:
                pt_wkt = None
        else:
            pt_wkt = None
        
        # Determine table structure
        table_name = cls.MODEL.__tablename__
        needs_site_join = (table_name == 'layers')
        
        with db_session_with_credentials() as (engine, session):
            try:
                # Detect database SRID to avoid transforming indexed column
                # Query first non-null geometry to determine database SRID
                if needs_site_join:
                    srid_qry = session.query(func.ST_SRID(Site.geom)).filter(
                        Site.geom.isnot(None)
                    ).limit(1)
                else:
                    srid_qry = session.query(func.ST_SRID(cls.MODEL.geom)).filter(
                        cls.MODEL.geom.isnot(None)
                    ).limit(1)        
                try:
                    db_srid_result = session.execute(srid_qry).first()
                    if not db_srid_result or db_srid_result[0] is None:
                        # No data in table yet - use input CRS as default
                        # This allows empty table queries to work 
                        # (will return empty)
                        LOG.warning(
                            f"No geometries found in {table_name}, "
                            f"using input CRS {crs} as default"
                        )
                        db_srid = crs
                    else:
                        db_srid = db_srid_result[0]
                        LOG.debug(f"Detected database SRID: \
                                 {db_srid} for table {table_name}")
                except Exception as srid_error:
                    # If SRID detection fails, fall back to input CRS
                    LOG.warning(
                        f"SRID detection failed for {table_name}: {srid_error}."
                        f"Using input CRS {crs} as default"
                    )
                    db_srid = crs
                
                # Build PostGIS search geometry
                # Transform search geometry to match database SRID for index 
                # usage
                if pt_wkt:
                    # Create point in input CRS, buffer it, then transform to 
                    # DB SRID
                    # Buffer before transform to ensure correct distance units
                    search_geom = func.ST_Transform(
                        func.ST_Buffer(
                            func.ST_GeomFromText(literal(pt_wkt), literal(crs)),
                            literal(buffer)
                        ),
                        literal(db_srid)
                    )
                elif shp_wkt:
                    # Transform shape from input CRS to database SRID
                    search_geom = func.ST_Transform(
                        func.ST_GeomFromText(literal(shp_wkt), literal(crs)),
                        literal(db_srid)
                    )
                else:
                    raise ValueError("Unable to parse geometry input")
                
            # Build select clause (handles verbose mode)
                select_clause = cls._build_select_clause(verbose) \
                                if hasattr(cls, '_build_select_clause') \
                                else [cls.MODEL]
                qry = session.query(*select_clause)
                
                # Add explicit joins for verbose mode to avoid 
                # cartesian products
                if verbose and hasattr(cls, '_add_verbose_joins'):
                    qry = cls._add_verbose_joins(qry)
                elif hasattr(cls, '_add_base_joins'):
                    # For verbose=False, still need basic joins
                    # (e.g., Site for geom)
                    qry = cls._add_base_joins(qry)
                
                # Add spatial filter
                if needs_site_join:
                    # For LayerData, join to Site for geometry
                    # SQLAlchemy handles duplicate joins from _add_*_joins above
                    qry = qry.join(cls.MODEL.site)
                    qry = qry.filter(func.ST_Intersects(Site.geom, search_geom))
                else:
                    # For PointData, use direct geometry column
                    qry = qry.filter(func.ST_Intersects(cls.MODEL.geom, 
                                                        search_geom))
                
                # Add standard filters using existing extend_qry
                # This handles type, instrument, campaign, date ranges, etc.
                qry = cls.extend_qry(qry, **kwargs)
                
                # Execute and convert to GeoDataFrame
                df = query_to_geopandas(qry, engine)
                
            except Exception as e:
                session.close()
                LOG.error(f"Failed query for {cls.__name__}")
                raise e
        
        return df

    @property
    def all_campaigns(self):
        """
        Return all campaign names
        """
        with db_session_with_credentials() as (_engine, session):
            qry = session.query(Campaign.name).distinct()
            result = qry.all()
        return self.retrieve_single_value_result(result)

    @property
    def all_types(self):
        """
        Return all types of the data
        """
        with db_session_with_credentials() as (_engine, session):
            qry = session.query(MeasurementType.name).distinct()
            result = qry.all()
        return self.retrieve_single_value_result(result)

    @property
    def all_dates(self):
        """
        Return all distinct dates in the data
        """
        with db_session_with_credentials() as (_engine, session):
            qry = session.query(self.MODEL.date).distinct()
            result = qry.all()
        return self.retrieve_single_value_result(result)

    @property
    def all_observers(self):
        """
        Return all distinct observers in the data
        """
        with db_session_with_credentials() as (_engine, session):
            qry = session.query(Observer.name).distinct()
            result = qry.all()
        return self.retrieve_single_value_result(result)

    @property
    def all_dois(self):
        """
        Return all distinct DOIs in the data
        """
        with db_session_with_credentials() as (_engine, session):
            qry = session.query(DOI.doi).distinct()
            result = qry.all()
        return self.retrieve_single_value_result(result)

    @property
    def all_units(self):
        """
        Return all distinct units in the data
        """
        with db_session_with_credentials() as (_engine, session):
            qry = session.query(self.MODEL.units).distinct()
            result = qry.all()
        return self.retrieve_single_value_result(result)

    @property
    def all_instruments(self):
        """
        Return all distinct instruments in the data
        """
        with db_session_with_credentials() as (_engine, session):
            # Use EXISTS for better performance on large datasets
            # (29GB+ tables)
            qry = session.query(Instrument.name).filter(
                exists().where(
                    self.MODEL.instrument_id == Instrument.id
                )
            )
            result = qry.all()
        return self.retrieve_single_value_result(result)


class PointMeasurements(BaseDataset):
    """
    API class for access to PointData
    """
    MODEL = PointData

    @classmethod
    def _build_select_clause(cls, verbose=False):
        """
        Build SELECT clause for PointMeasurements queries.
        
        Args:
            verbose: If False, return only core point columns.
                    If True, return denormalized data with observation, 
                    instrument, and measurement type info.
        """
        if verbose:
            # Return denormalized data with meaningful column names
            # Note: Must also join these tables explicitly in the query
            return [
                cls.MODEL.value,
                cls.MODEL.datetime.label('date'),
                cls.MODEL.elevation,
                cls.MODEL.geom,
                CampaignObservation.name.label('observation_name'),
                CampaignObservation.description.label('obs_description'),
                MeasurementType.name.label('type'),
                MeasurementType.units.label('units'),
                MeasurementType.derived.label('derived'),
                Instrument.name.label('instrument_name'),
                Instrument.model.label('instrument_model'),
                Instrument.specifications.label('instrument_specifications'),
                Campaign.name.label('campaign_name'),
                Observer.name.label('observer_name')
            ]
        else:
            # Return only columns from points table
            return [
                cls.MODEL.id,
                cls.MODEL.value,
                cls.MODEL.datetime,
                cls.MODEL.elevation,
                cls.MODEL.geom
            ]
    
    @classmethod
    def _add_verbose_joins(cls, qry):
        """
        Add explicit joins needed for verbose mode to avoid cartesian products.
        """
        qry = qry.join(cls.MODEL.observation)
        qry = qry.join(cls.MODEL.measurement_type)
        qry = qry.join(PointObservation.instrument)
        qry = qry.join(PointObservation.campaign)
        qry = qry.join(PointObservation.observer)
        return qry

    @classmethod
    def _filter_campaign(cls, qry, value):
        return qry.join(
            cls.MODEL.observation
        ).join(
            PointObservation.campaign
        ).filter(
            Campaign.name == value
        )

    @classmethod
    def _filter_instrument(cls, qry, value):
        return qry.join(
            cls.MODEL.observation
        ).join(
            PointObservation.instrument
        ).filter(
            Instrument.name == value
        )

    @classmethod
    def _filter_doi(cls, qry, value):
        return qry.join(
            cls.MODEL.observation
        ).join(
            PointObservation.doi
        ).filter(
            DOI.doi == value
        )

    @classmethod
    def _filter_observers(cls, qry, value):
        return qry.join(
            cls.MODEL.observation
        ).join(
            PointObservation.observer
        ).filter(
            Observer.name == value
        )

    @property
    def all_types(self):
        """
        Return all measurement types that have data in the points table
        """
        with db_session_with_credentials() as (_engine, session):
            # Use EXISTS for better performance on large points table
            qry = session.query(MeasurementType.name).filter(
                exists().where(
                    PointData.measurement_type_id == MeasurementType.id
                )
            )
            result = qry.all()
        return self.retrieve_single_value_result(result)
    
    @property
    def all_instruments(self):
        """
        Return all distinct instruments in the data
        """
        with db_session_with_credentials() as (_engine, session):
            result = session.query(Instrument.name).filter(
                Instrument.id.in_(
                    session.query(
                        PointObservation.instrument_id
                    ).distinct()
                )
            ).distinct().all()
        return self.retrieve_single_value_result(result)


class TooManyRastersException(Exception):
    """
    Exception to report to users that their query will produce too
    many rasters
    """
    pass


class LayerMeasurements(BaseDataset):
    """
    API class for access to LayerData
    """
    MODEL = LayerData
    ALLOWED_QRY_KWARGS = [
        "campaign", "site", "date", "instrument", "observer", "type",
        "utm_zone", "date_greater_equal", "date_less_equal",
        "doi", "value_greater_equal", 'value_less_equal'
    ]

    @classmethod
    def _filter_campaign(cls, qry, v):
        return qry.join(
            cls.MODEL.site
        ).join(
            Site.campaign
        ).filter(
            Campaign.name == v
        )
        
    @classmethod
    def _filter_observers(cls, qry, v):
        return qry.join(
            cls.MODEL.site
        ).join(
            Site.observers
        ).filter(
            Observer.name == v
        )
    
    @classmethod
    def _filter_doi(cls, qry, value):
        return qry.join(
            cls.MODEL.site
        ).join(
            Site.doi
        ).filter(
            DOI.doi == value
        )
    
    @classmethod
    def _build_select_clause(cls, verbose=False):
        """
        Build SELECT clause for LayerMeasurements queries.
        
        Args:
            verbose: If False, return only core layer columns (no joins).
                    If True, return denormalized data with site, instrument, 
                    and measurement type info.
        """
        if verbose:
            # Return denormalized data with meaningful column names
            # Note: Must also join these tables explicitly in the query
            return [
                cls.MODEL.depth,
                cls.MODEL.bottom_depth,
                cls.MODEL.value,
                Site.name.label('site_name'),
                Site.description.label('site_description'),
                Site.slope_angle.label('slope_angle'),
                Site.aspect.label('aspect'),
                Site.air_temp.label('air_temp'),
                Site.total_depth.label('total_depth'),
                Site.weather_description.label('weather_description'),
                Site.precip.label('precip'),
                Site.sky_cover.label('sky_cover'),  
                Site.wind.label('wind'),
                Site.ground_condition.label('ground_condition'),
                Site.ground_roughness.label('ground_roughness'),
                Site.ground_vegetation.label('ground_vegetation'),
                Site.vegetation_height.label('vegetation_height'),
                Site.tree_canopy.label('tree_canopy'),
                Site.comments.label('site_comments'),
                Site.datetime.label('date'),
                Site.geom,  
                MeasurementType.name.label('type'),
                MeasurementType.units.label('units'),
                MeasurementType.derived.label('type_derived'),
                Instrument.name.label('instrument_name'),
                Instrument.model.label('instrument_model'),
                Instrument.specifications.label('instrument_specifications'),
                func.ST_AsText(Site.geom).label('geom_wkt')
            ]
        else:
            # Return only core columns from layers table plus geom for geopandas
            return [
                cls.MODEL.id,
                cls.MODEL.depth,
                cls.MODEL.bottom_depth,
                cls.MODEL.value,
                Site.geom  # Required for GeoDataFrame
            ]
    
    @classmethod
    def _add_base_joins(cls, qry):
        """
        Add minimal joins needed for non-verbose mode (just Site for geom).
        """
        qry = qry.join(cls.MODEL.site)
        return qry
    
    @classmethod
    def _add_verbose_joins(cls, qry):
        """
        Add explicit joins needed for verbose mode to avoid cartesian products.
        """
        qry = qry.join(cls.MODEL.site)
        qry = qry.join(cls.MODEL.measurement_type)
        qry = qry.join(cls.MODEL.instrument)
        return qry
    
    @property
    def all_types(self):
        """
        Return all measurement types that have data in the layers table
        """
        with db_session_with_credentials() as (_engine, session):
            # Use EXISTS for better performance on 208M row table
            qry = session.query(MeasurementType.name).filter(
                exists().where(
                    LayerData.measurement_type_id == MeasurementType.id
                )
            )
            result = qry.all()
        return self.retrieve_single_value_result(result)
    
    @property
    def all_sites(self):
        """
        Return all specific site names
        """
        with db_session_with_credentials() as (_engine, session):
            result = session.query(
                Site.name
            ).distinct().all()
        return self.retrieve_single_value_result(result)

    @property
    def all_dates(self):
        """
        Return all distinct dates in the data
        """
        with db_session_with_credentials() as (_engine, session):
            result = session.query(
                Site.date
            ).distinct().all()
        return self.retrieve_single_value_result(result)

    @property
    def all_units(self):
        """
        Return all distinct units in the data
        """
        with db_session_with_credentials() as (_engine, session):
            result = session.query(
                MeasurementType.units
            ).distinct().all()
        return self.retrieve_single_value_result(result)
    
    @classmethod
    def get_sites(cls, site_names=None, **kwargs):
        """
        Get site information including geometries.
        
        Args:
            site_names: List of site names or single site name
            **kwargs: Additional filters (campaign, date, etc.)
            
        Returns:
            GeoDataFrame with site information
        """
        with db_session_with_credentials() as (engine, session):
            qry = session.query(Site.name, 
                                Site.geom,
                                Site.description,
                                Site.datetime).distinct() 
                                # others can be added
            
            if site_names:
                if isinstance(site_names, list):
                    qry = qry.filter(Site.name.in_(site_names))
                else:
                    qry = qry.filter(Site.name == site_names)
            
            df = query_to_geopandas(qry, engine)
        
        return df

class RasterMeasurements(BaseDataset):
    MODEL = ImageData
    ALLOWED_QRY_KWARGS = (
        BaseDataset.ALLOWED_QRY_KWARGS + ['description']
    )

    @property
    def all_types(self):
        """
        Return all measurement types that have data in the images table
        """
        with db_session_with_credentials() as (_engine, session):
            result = session.query(
                MeasurementType.name
            ).join(
                ImageData, ImageData.observation_id == ImageObservation.id
            ).join(
                ImageObservation.measurement_type
            ).distinct().all()
        return self.retrieve_single_value_result(result)
    
    @property
    def all_descriptions(self):
        with db_session_with_credentials() as (_engine, session):
            qry = session.query(self.MODEL.description).distinct()
            result = qry.all()
        return self.retrieve_single_value_result(result)

    @classmethod
    def check_for_single_dataset(cls, **kwargs):
        """
        At the moment there is not a clear path to how to deal with
        multiple rasters so check that the user only requested one
        dataset
        """
        LOG.info(
            "Checking raster query for single raster dataset..."
        )
        multi_raster_indicators = [
            'instrument', 'date', 'observers', 'doi', 'type',
            'description'
        ]
        with db_session_with_credentials() as (_engine, session):
            try:
                # Form query and check if the query spans
                # multiple rasters
                for column in multi_raster_indicators:
                    values = cls.from_unique_entries(
                        [column], **kwargs
                    )
                    if len(values) > 1:
                        options = [f"'{v}'" for v in values]
                        raise TooManyRastersException(
                            f"More than one `{column}` suggests "
                            f"there are multiple raster datasets. "
                            f"Try filter {column} to one of the "
                            f"following values {', '.join(options)}."
                        )

            except Exception as e:
                session.close()
                LOG.error("Failed query for Raster Data")
                raise e

    @classmethod
    def from_filter(cls, **kwargs):
        """
        Get data for the class by filtering by allowed arguments.
        The allowed filters are cls.ALLOWED_QRY_KWARGS.
        """

        cls.check_for_single_dataset(**kwargs)

        with db_session_with_credentials() as (_engine, session):
            try:
                # Rebuild the query and form the raster
                base_query = cls.MODEL.raster

                qry = session.query(
                    func.ST_AsTiff(
                        func.ST_Union(base_query, type_=Raster)
                    )
                )
                qry = cls.extend_qry(qry, **kwargs)
                rasters = qry.all()

                # Get the rasterio object of the raster
                datasets = raster_to_rasterio(rasters)

            except Exception as e:
                LOG.error("Failed query for Raster Data")
                raise e

        return datasets

    @classmethod
    def from_area(
        cls, shp=None, pt=None, buffer=None, crs=26912, **kwargs
    ):
        if shp is None and pt is None:
            raise ValueError(
                "We need a shape description or a point and buffer"
            )
        if ((pt is not None and buffer is None) or
                (buffer is not None and pt is None)):
            raise ValueError(
                "pt and buffer must be given together"
            )
        
        # Check if geometric operations are available
        if not HAS_CORE_GIS:
            raise ImportError(
                "geoalchemy2 and shapely are required for "
                "geometric filtering. Install with: "
                "pip install geoalchemy2 shapely"
            )

        with db_session_with_credentials() as (_engine, session):

            try:
                # Get shape ready for cropping with rasters
                if shp:
                    db_shp = from_shape(shp, srid=crs)
                else:
                    qry_pt = from_shape(pt)
                    qry = session.query(
                        gfunc.ST_SetSRID(
                            func.ST_Buffer(qry_pt, buffer), crs
                        )
                    )
                    db_shp = qry.all()[0][0]

                # Grab the rasters, union and clip them
                base_query = func.ST_AsTiff(
                    func.ST_Clip(
                        func.ST_Union(ImageData.raster, type_=Raster),
                        db_shp,
                        True
                    )
                )
                q = session.query(base_query)
                # Find all the tiles that
                q = q.filter(
                    gfunc.ST_Intersects(ImageData.raster, db_shp)
                )


                limit = kwargs.get("limit")
                if limit:
                    kwargs.pop("limit")
                q = cls.extend_qry(q, check_size=False, **kwargs)
                rasters = q.all()

                # Get the rasterio object of the raster
                datasets = raster_to_rasterio(rasters)
                if len(datasets) > 0:
                    dataset = datasets[0]
                else:
                    dataset = datasets
                return dataset

            except Exception as e:
                LOG.error("Failed query for Raster Data")
                raise e
