from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class CrimeOut(BaseModel):
    id: int
    date: str
    offense: Optional[str] = None
    borough: Optional[str] = None
    latitude: float
    longitude: float
    category: Optional[str] = None
    precinct: Optional[str] = None

    model_config = {"from_attributes": True}


class HotspotOut(BaseModel):
    cluster_id: int
    latitude: float
    longitude: float
    crime_count: int

    model_config = {"from_attributes": True}


class PaginatedCrimes(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[CrimeOut]


class BoroughStat(BaseModel):
    borough: str
    crime_count: int


class OffenseStat(BaseModel):
    offense: str
    crime_count: int


class CategoryStat(BaseModel):
    category: str
    crime_count: int


class MonthStat(BaseModel):
    month: str
    crime_count: int


class DashboardStats(BaseModel):
    total: int
    by_borough: list[BoroughStat]
    by_offense: list[OffenseStat]
    by_category: list[CategoryStat]
    by_month: list[MonthStat]
