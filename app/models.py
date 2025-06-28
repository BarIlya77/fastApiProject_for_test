from typing import List, Optional

from sqlalchemy import ForeignKey, String, Float, Integer, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


organization_activity = Table(
    "organization_activity",
    Base.metadata,
    Column("organization_id", ForeignKey("organizations.id"), primary_key=True),
    Column("activity_id", ForeignKey("activities.id"), primary_key=True)
)


class Phone(Base):
    __tablename__ = "phones"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(20))
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    organization: Mapped["Organization"] = relationship(back_populates="phones")


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("activities.id"))

    children: Mapped[List["Activity"]] = relationship(
        back_populates="parent",
        remote_side=[parent_id]
    )
    parent: Mapped[Optional["Activity"]] = relationship(
        back_populates="children",
        remote_side=[id]
    )

    organizations: Mapped[List["Organization"]] = relationship(
        secondary="organization_activity",
        back_populates="activities"
    )


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(String(200))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    organizations: Mapped[List["Organization"]] = relationship(back_populates="building")


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"))

    building: Mapped["Building"] = relationship()
    phones: Mapped[List["Phone"]] = relationship(back_populates="organization")
    activities: Mapped[List["Activity"]] = relationship(secondary="organization_activity")
