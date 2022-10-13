from contextlib import contextmanager
from sqlalchemy.sql import func
import geopandas as gpd
from shapely.geometry import box
from geoalchemy2.shape import from_shape
import geoalchemy2.functions as gfunc

from snowexsql.db import get_db
from snowexsql.data import SiteData, PointData, LayerData, ImageData
from snowexsql.conversions import query_to_geopandas


DB_NAME = 'snow:hackweek@db.snowexdata.org/snowex'


@contextmanager
def db_session():
    engine, session = get_db(DB_NAME)
    yield session, engine
    session.close()


def get_points():
    # Lets grab a single row from the points table
    with db_session() as session:
        qry = session.query(PointData).limit(1)
        # Execute that query!
        result = qry.all()


class BaseDataset:
    MODEL = None

    ALLOWED_QRY_KWRAGS = [
        "site_name", "site_id", "date", "instrument", "observers", "type"
    ]
    SPECIAL_KWARGS = ["limit"]

    @staticmethod
    def build_box(xmin, ymin, xmax, ymax, crs):
        # build a geopandas box
        return gpd.GeoDataFrame(
            geometry=[box(xmin, ymin, xmax, ymax)]
        ).set_crs(crs)

    @classmethod
    def extend_qry(cls, qry, **kwargs):
        for k, v in kwargs.items():
            if k in cls.SPECIAL_KWARGS:
                if k == "limit":
                    qry = qry.limit(v)
            elif k in cls.ALLOWED_QRY_KWRAGS:
                filter_col = getattr(cls.MODEL, k)
                if isinstance(v, list):
                    qry = qry.filter(filter_col.in_([v]))
                    #TODO: LOG.debug
                else:
                    qry = qry.filter(filter_col == v)
            else:
                raise ValueError(f"{k} is not an allowed filter")
        return qry

    @property
    def all_types(self):
        with db_session() as (session, engine):
            qry = session.query(self.MODEL.type).distinct()
            result = qry.all()
        return result

    @property
    def all_dates(self):
        with db_session() as (session, engine):
            qry = session.query(self.MODEL.date).distinct()
            result = qry.all()
        return result

    @property
    def all_observers(self):
        with db_session() as (session, engine):
            qry = session.query(self.MODEL.observers).distinct()
            result = qry.all()
        return result

    @property
    def all_instruments(self):
        with db_session() as (session, engine):
            qry = session.query(self.MODEL.instrument).distinct()
            result = qry.all()
        return result


class PointMeasurements(BaseDataset):
    MODEL = PointData

    @classmethod
    def from_filter(cls, **kwargs):
        with db_session() as (session, engine):
            try:
                qry = session.query(cls.MODEL)
                qry = cls.extend_qry(qry, **kwargs)
                df = query_to_geopandas(qry, engine)
            except Exception as e:
                session.close()
                raise e

        return df

    @classmethod
    def from_area(cls, shp=None, pt=None, buffer=None, crs=26912, **kwargs):
        """
        Args:
            shp:
        """
        if shp is None and pt is None:
            raise ValueError("We need a shape description or a point and buffer")
        if (pt is not None and buffer is None) or (buffer is not None and pt is None):
            raise ValueError("pt and buffer must be given together")
        with db_session() as (session, engine):
            try:
                if shp:
                    qry = session.query(cls.MODEL)
                    qry = qry.filter(func.ST_Within(PointData.geom, shp))
                    qry = cls.extend_qry(qry, **kwargs)
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
                    qry = qry.filter(func.ST_Within(PointData.geom, buffered_pt))
                    qry = cls.extend_qry(qry, **kwargs)
                    df = query_to_geopandas(qry, engine)
            except Exception as e:
                session.close()
                raise e

        return df


class LayerMeasurements(BaseDataset):
    MODEL = LayerData


class RasterMeasurements(BaseDataset):
    MODEL = ImageData

    # @classmethod
    # def from_area(cls):
    #     # Building a buffer which will give us a buffer object around our point
    #     buffer = session.query(
    #         gfunc.ST_SetSRID(gfunc.ST_Buffer(from_shape(geom), buffer_dist),
    #                          crs)).all()[0][0]
    #
    #     # Convert to a shapely shapefile object
    #     circle = to_shape(buffer)
    #
    #     # Convert to a geopandas dataframe
    #     df_circle = gpd.GeoSeries(circle)
    #
    #     # Grab the rasters, union them and convert them as tiff when done
    #     q = session.query(
    #         func.ST_AsTiff(func.ST_Union(ImageData.raster, type_=Raster)))
    #
    #     # Only grab rasters that are the bare earth DEM from USGS
    #     q = q.filter(ImageData.type == 'depth').filter(
    #         ImageData.observers == 'ASO Inc.')
    #     q = q.filter(ImageData.date == dt)
    #
    #     # And grab rasters touching the circle
    #     q = q.filter(gfunc.ST_Intersects(ImageData.raster, buffer))
    #
    #     # Execute the query
    #     rasters = q.all()
    #
    #     # Get the rasterio object of the raster
    #     dataset = raster_to_rasterio(session, rasters)[0]
