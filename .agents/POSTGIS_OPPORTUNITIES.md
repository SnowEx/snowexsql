# PostGIS Optimization Opportunities

## Overview
By leveraging PostGIS on the server side and sending WKT strings from the client, we can avoid heavy geospatial dependencies in Lambda while maintaining full spatial functionality.

## Current Implementation Status

### ✅ Implemented
- **from_area() for Point/Layer Measurements**: Uses PostGIS `ST_Intersects`, `ST_Buffer`, `ST_Transform` for spatial filtering

## 🎯 High Priority Opportunities

### 1. **Raster Operations (RasterMeasurements.from_area)**
**Current Issue**: Requires shapely's `from_shape()` in Lambda
**Solution**: Accept WKT from client, use PostGIS functions

```python
# Lambda Handler
def _handle_raster_from_area_postgis(event, session):
    wkt = event.get('shp_wkt') or event.get('pt_wkt')
    crs = event.get('crs', 26912)
    buffer_dist = event.get('buffer')
    
    if pt_wkt and buffer_dist:
        geom_sql = f"ST_Buffer(ST_Transform(ST_GeomFromText('{wkt}', {crs}), 4326)::geography, {buffer_dist})::geometry"
    else:
        geom_sql = f"ST_Transform(ST_GeomFromText('{wkt}', {crs}), 4326)"
    
    query = text(f"""
        SELECT ST_AsTiff(
            ST_Clip(
                ST_Union(raster),
                ({geom_sql}),
                TRUE
            )
        )
        FROM image_data
        WHERE ST_Intersects(raster, ({geom_sql}))
    """)
    # ... execute and return
```

**Benefits**:
- Raster clipping works in Lambda
- No shapely/rasterio needed in Lambda
- Fast server-side processing

### 2. **Distance-Based Queries**
**New Feature**: Find measurements within X meters of a point

```python
# Client API
df = PointMeasurements.find_within_distance(
    pt=Point(x, y),
    distance=1000,  # meters
    crs=26912,
    type='depth'
)

# Lambda uses PostGIS ST_DWithin
query = text(f"""
    SELECT *
    FROM point_data
    WHERE ST_DWithin(
        geom::geography,
        ST_Transform(ST_GeomFromText('{pt_wkt}', {crs}), 4326)::geography,
        {distance}
    )
""")
```

**Benefits**:
- Uses PostGIS spatial index (extremely fast)
- No need to buffer geometries
- Geography type handles meters correctly

### 3. **Bounding Box Queries**
**New Feature**: Query by bounding box (xmin, ymin, xmax, ymax)

```python
# Client API
df = PointMeasurements.from_bbox(
    bbox=(xmin, ymin, xmax, ymax),
    crs=26912,
    type='depth'
)

# Lambda uses PostGIS ST_MakeEnvelope
query = text(f"""
    SELECT *
    FROM point_data
    WHERE ST_Intersects(
        geom,
        ST_Transform(ST_MakeEnvelope({xmin}, {ymin}, {xmax}, {ymax}, {crs}), 4326)
    )
""")
```

**Benefits**:
- Common use case for map viewers
- Very efficient with spatial indexes
- No client-side geometry construction needed

## 🔄 Medium Priority

### 4. **Nearest Neighbor Queries**
**New Feature**: Find N nearest measurements to a point

```python
df = PointMeasurements.find_nearest(
    pt=Point(x, y),
    n=10,
    crs=26912,
    type='depth'
)

# Uses PostGIS <-> operator and ORDER BY distance
query = text(f"""
    SELECT *, ST_Distance(geom::geography, point::geography) as distance
    FROM point_data
    CROSS JOIN (
        SELECT ST_Transform(ST_GeomFromText('{pt_wkt}', {crs}), 4326)::geography as point
    ) pt
    WHERE type_id = (SELECT id FROM measurement_type WHERE name = :type)
    ORDER BY geom::geography <-> pt.point
    LIMIT :n
""")
```

### 5. **Spatial Aggregations**
**New Feature**: Group measurements by proximity

```python
# Find average depth within grid cells
df = PointMeasurements.aggregate_by_grid(
    bbox=(xmin, ymin, xmax, ymax),
    cell_size=100,  # meters
    type='depth',
    agg='mean'
)

# Uses PostGIS ST_SnapToGrid
```

## 🚀 Advanced Opportunities

### 6. **Line-of-Sight / Path Queries**
Query measurements along a path (e.g., flight line, transect)

```python
df = PointMeasurements.along_path(
    path=LineString([...]),
    buffer=50,
    type='depth'
)
```

### 7. **Temporal-Spatial Queries**
Combine spatial and temporal proximity

```python
# Find measurements near location X within 1 day of date Y
df = PointMeasurements.find_nearby_in_time(
    pt=Point(x, y),
    date=datetime(2020, 2, 1),
    spatial_buffer=500,
    temporal_window=timedelta(days=1)
)
```

### 8. **Spatial Joins**
Join different measurement types by proximity

```python
# Find all SMP profiles within 10m of pits
df = LayerMeasurements.join_nearby(
    reference_type='density',  # pits
    join_type='smp',
    max_distance=10
)
```

## Implementation Pattern

For all PostGIS operations, follow this pattern:

1. **Client Side** (lambda_client.py):
   - Convert Shapely geometries to WKT
   - Send WKT + parameters to Lambda

2. **Lambda Handler** (lambda_handler.py):
   - Construct PostGIS SQL query
   - Use WKT with `ST_GeomFromText`
   - Let database do spatial operations

3. **Benefits**:
   - ✅ No heavy dependencies in Lambda
   - ✅ Fast database-side processing
   - ✅ Scales to millions of geometries
   - ✅ Uses PostGIS spatial indexes

## Performance Notes

PostGIS spatial indexes (`GIST`) make these operations extremely fast:
- `ST_Intersects`: Uses index, very fast
- `ST_DWithin`: Uses index, very fast  
- `ST_Distance` with ORDER BY: Uses index with KNN operator `<->`
- Without spatial index: Linear scan, slow

Ensure all geometry columns have spatial indexes:
```sql
CREATE INDEX idx_point_data_geom ON point_data USING GIST(geom);
CREATE INDEX idx_layer_data_site_geom ON site USING GIST(geom);
```

## Summary

By systematically moving spatial operations to PostGIS:
1. Lambda stays lightweight and fast
2. Database does what it's optimized for
3. Spatial queries scale efficiently
4. No dependency hell in serverless environment

**Next Steps**:
1. Implement raster WKT support
2. Add distance-based queries
3. Add bounding box queries
4. Consider advanced features based on user needs
