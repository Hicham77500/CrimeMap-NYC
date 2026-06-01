from __future__ import annotations

from sqlalchemy import Column, String, Float, Integer
from database import Base


class NypdCrime(Base):
    __tablename__ = "nypd_crimes"

    id        = Column(Integer, primary_key=True)
    date      = Column(String,  nullable=False)
    offense   = Column(String)
    borough   = Column(String(50))
    latitude  = Column(Float)
    longitude = Column(Float)
    category  = Column(String(20))
    precinct  = Column(String(10))


class Hotspot(Base):
    __tablename__ = "hotspots"

    cluster_id  = Column(Integer, primary_key=True)
    latitude    = Column(Float, nullable=False)
    longitude   = Column(Float, nullable=False)
    crime_count = Column(Integer, nullable=False)
