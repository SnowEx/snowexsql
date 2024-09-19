from sqlalchemy import Column, Float, Integer, String, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, \
    column_property
from typing import List

from .base import Base, SingleLocationData
from .doi import HasOneDOI
from .measurement_type import HasMeasurement
from .observers import Observer
from .instrument import HasInstrument
from .site import Site


class LayerObservers(Base):
    """
    Link table
    """
    __tablename__ = 'layer_observers'

    layer_id = Column(Integer, ForeignKey('public.layers.id'))
    observer_id = Column(Integer, ForeignKey("public.observers.id"))


class LayerData(
    SingleLocationData, HasMeasurement, HasInstrument, Base, HasOneDOI
):
    """
    Class representing the layers table. This table holds all layers or
    profile data. Here a single data entry is a single value at depth in the
    snowpack and a single coordinate pair.  e.g. SMP profiles, Hand hardness,
    temperature etc...
    """
    __tablename__ = 'layers'

    depth = Column(Float)
    pit_id = Column(String(50))
    bottom_depth = Column(Float)
    comments = Column(String(1000))
    sample_a = Column(String(20))
    sample_b = Column(String(20))
    sample_c = Column(String(20))
    value = Column(String(50))
    flags = Column(String(20))

    # Link the site id with a foreign key
    site_id = Column(
        Integer, ForeignKey('public.sites.id'), index=True
    )
    # Link the Site class
    site = relationship('Site', lazy='joined')

    # id is a mapped column for many-to-many with observers
    id: Mapped[int] = mapped_column(primary_key=True)
    observers: Mapped[List[Observer]] = relationship(
        secondary=LayerObservers.__table__
    )

    # # Rendered columns
    # # Use column_property to reference Site's date column
    # # This makes querying easier
    # # date = column_property(
    # #     select(Site.date).where(Site.id == site_id).scalar_subquery()
    # # )
    # date = column_property(
    #     select(Site.date).where(Site.id == site_id).correlate(Site).scalar_subquery()
    # )
