from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from .base import Base


class Observer(Base):
    __tablename__ = 'observers'
    # id is mapped column for many-to-many
    id: Mapped[int] = mapped_column(primary_key=True)
    # Name of the observer
    name = Column(String(), nullable=False)


class HasObserver:
    """
    Class to inherit when adding a observer relationship to a table
    """

    observers_id: Mapped[int] = mapped_column(
        ForeignKey("public.observers.id"), index=True, nullable=False
    )

    @declared_attr
    def observer(self) -> Mapped[Observer]:
        return relationship('Observer')
