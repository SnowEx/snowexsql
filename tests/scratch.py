from metloom.pointdata import SnotelPointData
from os.path import join, dirname

import pytest
import geopandas as gpd
from datetime import date

from snowexsql.api import PointMeasurements


def test_stuff():
    sntl_point = SnotelPointData("622:CO:SNTL", "dummy name")
    geom = sntl_point.metadata
    geom = gpd.GeoSeries(geom).set_crs(4326).to_crs(26912).geometry.values[0]

    shp1 = gpd.GeoSeries(
        sntl_point.metadata
    ).set_crs(4326).buffer(.1).total_bounds
    bx = PointMeasurements.build_box(
        *list(shp1),
        4326
    )
    bx = bx.to_crs(26912)
    bx.explore().save("map.html")
    df = PointMeasurements.from_area(
        shp=bx.geometry.iloc[0], limit=30
    )

    df = PointMeasurements.from_area(
        pt=geom, buffer=10000, instrument="magnaprobe", limit=250
    )
    # df = PointMeasurements.from_filter(
    #     instrument="magnaprobe", limit=20
    # )
    print(df)
