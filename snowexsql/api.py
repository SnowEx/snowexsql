import logging
from contextlib import contextmanager
from sqlalchemy.sql import func
import geopandas as gpd
from shapely.geometry import box
from geoalchemy2.shape import from_shape, to_shape
import geoalchemy2.functions as gfunc
from geoalchemy2.types import Raster

from snowexsql.db import get_db
from snowexsql.data import SiteData, PointData, LayerData, ImageData
from snowexsql.conversions import query_to_geopandas, raster_to_rasterio


LOG = logging.getLogger(__name__)
DB_NAME = 'snow:hackweek@db.snowexdata.org/snowex'

# TODO:
#   * Possible enums
#   * filtering based on dates
#   * implement 'like' or 'contains' method


class LargeQueryCheckException(RuntimeError):
    pass


@contextmanager
def db_session(db_name):
    # use default_name
    db_name = db_name or DB_NAME
    engine, session = get_db(db_name)
    yield session, engine
    session.close()


def get_points():
    # Lets grab a single row from the points table
    with db_session(DB_NAME) as session:
        qry = session.query(PointData).limit(1)
        # Execute that query!
        result = qry.all()


class BaseDataset:
    MODEL = None
    # Use this database name
    DB_NAME = DB_NAME

    ALLOWED_QRY_KWARGS = [
        "site_name", "site_id", "date", "instrument", "observers", "type",
        "utm_zone", "date_greater_equal", "date_less_equal"
    ]
    SPECIAL_KWARGS = ["limit"]
    # Default max record count
    MAX_RECORD_COUNT = 1000

    @staticmethod
    def build_box(xmin, ymin, xmax, ymax, crs):
        # build a geopandas box
        return gpd.GeoDataFrame(
            geometry=[box(xmin, ymin, xmax, ymax)]
        ).set_crs(crs)

    @classmethod
    def _check_size(cls, qry, kwargs):
        # Safe guard against accidental giant requests
        count = qry.count()
        if count > cls.MAX_RECORD_COUNT and "limit" not in kwargs:
            raise LargeQueryCheckException(
                f"Query will return {count} number of records,"
                f" but we have a default max of {cls.MAX_RECORD_COUNT}."
                f" If you want to proceed, set the 'limit' filter"
                f" to the desired number of records."
            )

    @classmethod
    def extend_qry(cls, qry, check_size=True, **kwargs):
        if cls.MODEL is None:
            raise ValueError("You must use a class with a MODEL.")

        # use the default kwargs
        for k, v in kwargs.items():
            # Handle special operations
            if k in cls.ALLOWED_QRY_KWARGS:
                # standard filtering using qry.filter
                if isinstance(v, list):
                    filter_col = getattr(cls.MODEL, k)
                    if k == "date":
                        raise ValueError(
                            "We cannot search for a list of dates"
                        )
                    elif "_equal" in k:
                        raise ValueError(
                            "We cannot compare greater_equal or less_equal"
                            " with a list"
                        )
                    qry = qry.filter(filter_col.in_([v]))
                    LOG.debug(
                        f"Filtering {k} to value {v}"
                    )
                else:
                    # Filter boundary
                    if "_greater_equal" in k:
                        key = k.split("_greater_equal")[0]
                        filter_col = getattr(cls.MODEL, key)
                        qry = qry.filter(filter_col >= v)
                    elif "_less_equal" in k:
                        key = k.split("_less_equal")[0]
                        filter_col = getattr(cls.MODEL, key)
                        qry = qry.filter(filter_col <= v)
                    # Filter to exact value
                    else:
                        filter_col = getattr(cls.MODEL, k)
                        qry = qry.filter(filter_col == v)
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

    @property
    def all_site_names(self):
        """
        Return all types of the data
        """
        with db_session(self.DB_NAME) as (session, engine):
            qry = session.query(self.MODEL.site_name).distinct()
            result = qry.all()
        return result

    @property
    def all_types(self):
        """
        Return all types of the data
        """
        with db_session(self.DB_NAME) as (session, engine):
            qry = session.query(self.MODEL.type).distinct()
            result = qry.all()
        return result

    @property
    def all_dates(self):
        """
        Return all distinct dates in the data
        """
        with db_session(self.DB_NAME) as (session, engine):
            qry = session.query(self.MODEL.date).distinct()
            result = qry.all()
        return result

    @property
    def all_observers(self):
        """
        Return all distinct observers in the data
        """
        with db_session(self.DB_NAME) as (session, engine):
            qry = session.query(self.MODEL.observers).distinct()
            result = qry.all()
        return result

    @property
    def all_instruments(self):
        """
        Return all distinct instruments in the data
        """
        with db_session(self.DB_NAME) as (session, engine):
            qry = session.query(self.MODEL.instrument).distinct()
            result = qry.all()
        return result


class PointMeasurements(BaseDataset):
    """
    API class for access to PointData
    """
    MODEL = PointData

    @classmethod
    def from_filter(cls, **kwargs):
        """
        Get data for the class by filtering by allowed arguments. The allowed
        filters are cls.ALLOWED_QRY_KWARGS.
        """
        with db_session(cls.DB_NAME) as (session, engine):
            try:
                qry = session.query(cls.MODEL)
                qry = cls.extend_qry(qry, **kwargs)
                df = query_to_geopandas(qry, engine)
            except Exception as e:
                session.close()
                LOG.error("Failed query for PointData")
                raise e

        return df

    @classmethod
    def from_area(cls, shp=None, pt=None, buffer=None, crs=26912, **kwargs):
        """
        Get data for the class within a specific shapefile or
        within a point and a known buffer
        Args:
            shp: shapely geometry in which to filter
            pt: shapely point that will have a buffer applied in order
                to find search area
            buffer: in same units as point
            crs: integer crs to use
            kwargs: for more filtering or limiting (cls.ALLOWED_QRY_KWARGS)
        Returns: Geopandas dataframe of results

        """
        if shp is None and pt is None:
            raise ValueError(
                "Inputs must be a shape description or a point and buffer"
            )
        if (pt is not None and buffer is None) or \
                (buffer is not None and pt is None):
            raise ValueError("pt and buffer must be given together")
        with db_session(cls.DB_NAME) as (session, engine):
            try:
                if shp is not None:
                    qry = session.query(cls.MODEL)
                    qry = qry.filter(
                        func.ST_Within(
                            cls.MODEL.geom, from_shape(shp, srid=crs)
                        )
                    )
                    qry = cls.extend_qry(qry, check_size=True, **kwargs)
                    df = query_to_geopandas(qry, engine)
                else:
                    qry_pt = from_shape(pt)
                    qry = session.query(
                        gfunc.ST_SetSRID(
                            func.ST_Buffer(qry_pt, buffer), crs
                        )
                    )

                    buffered_pt = qry.all()[0][0]
                    qry = session.query(cls.MODEL)
                    qry = qry.filter(func.ST_Within(cls.MODEL.geom, buffered_pt))
                    qry = cls.extend_qry(qry, check_size=True, **kwargs)
                    df = query_to_geopandas(qry, engine)
            except Exception as e:
                session.close()
                raise e

        return df


class LayerMeasurements(PointMeasurements):
    """
    API class for access to LayerData
    """
    MODEL = LayerData
    ALLOWED_QRY_KWARGS = [
        "site_name", "site_id", "date", "instrument", "observers", "type",
        "utm_zone", "pit_id", "date_greater_equal", "date_less_equal"
    ]
    # TODO: layer analysis methods?


class RasterMeasurements(BaseDataset):
    MODEL = ImageData

    @classmethod
    def from_area(cls, shp=None, pt=None, buffer=None, crs=26912, **kwargs):
        if shp is None and pt is None:
            raise ValueError(
                "We need a shape description or a point and buffer")
        if (pt is not None and buffer is None) or (
                buffer is not None and pt is None):
            raise ValueError("pt and buffer must be given together")
        with db_session(cls.DB_NAME) as (session, engine):
            try:
                # Grab the rasters, union them and convert them as tiff when done
                q = session.query(
                    func.ST_AsTiff(
                        func.ST_Union(ImageData.raster, type_=Raster)
                    )
                )
                # Query upfront except for the limit
                limit = kwargs.get("limit")
                if limit:
                    kwargs.pop("limit")
                q = cls.extend_qry(q, check_size=False, **kwargs)
                if shp:
                    q = q.filter(
                        gfunc.ST_Intersects(
                            ImageData.raster,
                            from_shape(shp, srid=crs)
                        )
                    )
                else:
                    qry_pt = from_shape(pt)
                    qry = session.query(
                        gfunc.ST_SetSRID(
                            func.ST_Buffer(qry_pt, buffer), crs
                        )
                    )
                    buffered_pt = qry.all()[0][0]
                    # And grab rasters touching the circle
                    q = q.filter(gfunc.ST_Intersects(ImageData.raster, buffered_pt))
                    # Execute the query
                # Check the query size or limit the query
                if limit:
                    q = cls.extend_qry(q, limit=limit)
                else:
                    cls._check_size(qry, kwargs)
                rasters = q.all()
                # Get the rasterio object of the raster
                dataset = raster_to_rasterio(session, rasters)[0]
                return dataset

            except Exception as e:
                session.close()
                raise e
