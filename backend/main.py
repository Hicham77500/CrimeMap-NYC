from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import NypdCrime, Hotspot
from schemas import (
    CrimeOut,
    HotspotOut,
    PaginatedCrimes,
    DashboardStats,
    BoroughStat,
    OffenseStat,
    CategoryStat,
    MonthStat,
)

app = FastAPI(
    title="CrimeMap NYC API",
    description="API REST pour la visualisation de la criminalité à New York",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _apply_filters(query, borough, offense, date_from, date_to, year, category=None):
    if borough:
        query = query.filter(func.upper(NypdCrime.borough) == borough.upper())
    if offense:
        query = query.filter(func.upper(NypdCrime.offense).contains(offense.upper()))
    if category:
        query = query.filter(func.upper(NypdCrime.category) == category.upper())
    if date_from:
        query = query.filter(NypdCrime.date >= str(date_from))
    if date_to:
        query = query.filter(NypdCrime.date <= str(date_to))
    if year:
        query = query.filter(func.strftime("%Y", NypdCrime.date) == str(year))
    return query


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "CrimeMap NYC API"}


@app.get("/crimes", response_model=PaginatedCrimes, tags=["Crimes"])
def get_crimes(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    borough: Optional[str] = None,
    offense: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Liste paginée des crimes avec filtres optionnels."""
    query = db.query(NypdCrime)
    query = _apply_filters(query, borough, offense, date_from, date_to, year, category)
    total = query.count()
    items = query.order_by(NypdCrime.date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedCrimes(total=total, page=page, page_size=page_size, items=items)


@app.get("/crimes/search", response_model=PaginatedCrimes, tags=["Crimes"])
def search_crimes(
    q: Optional[str] = Query(None, description="Texte libre sur l'infraction"),
    borough: Optional[str] = None,
    offense: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    year: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Recherche combinée par texte libre + filtres."""
    query = db.query(NypdCrime)
    if q:
        query = query.filter(func.upper(NypdCrime.offense).contains(q.upper()))
    query = _apply_filters(query, borough, offense, date_from, date_to, year, category)
    total = query.count()
    items = query.order_by(NypdCrime.date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedCrimes(total=total, page=page, page_size=page_size, items=items)


@app.get("/crimes/{crime_id}", response_model=CrimeOut, tags=["Crimes"])
def get_crime(crime_id: int, db: Session = Depends(get_db)):
    crime = db.query(NypdCrime).filter(NypdCrime.id == crime_id).first()
    if not crime:
        raise HTTPException(status_code=404, detail="Crime not found")
    return crime


@app.get("/stats", response_model=DashboardStats, tags=["Stats"])
def get_stats(
    borough: Optional[str] = None,
    offense: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Agrégations dashboard : total, par borough, par infraction, par catégorie, par mois."""
    base = db.query(NypdCrime)
    base = _apply_filters(base, borough, offense, date_from, date_to, year, category)

    total = base.count()

    by_borough = (
        base.with_entities(NypdCrime.borough, func.count().label("crime_count"))
        .filter(NypdCrime.borough.isnot(None))
        .group_by(NypdCrime.borough)
        .order_by(func.count().desc())
        .all()
    )

    by_offense = (
        base.with_entities(NypdCrime.offense, func.count().label("crime_count"))
        .filter(NypdCrime.offense.isnot(None))
        .group_by(NypdCrime.offense)
        .order_by(func.count().desc())
        .limit(20)
        .all()
    )

    by_category = (
        base.with_entities(NypdCrime.category, func.count().label("crime_count"))
        .filter(NypdCrime.category.isnot(None))
        .group_by(NypdCrime.category)
        .order_by(func.count().desc())
        .all()
    )

    by_month = (
        base.with_entities(
            func.strftime("%Y-%m", NypdCrime.date).label("month"),
            func.count().label("crime_count"),
        )
        .filter(NypdCrime.date.isnot(None))
        .group_by("month")
        .order_by("month")
        .all()
    )

    return DashboardStats(
        total=total,
        by_borough=[BoroughStat(borough=r.borough, crime_count=r.crime_count) for r in by_borough if r.borough],
        by_offense=[OffenseStat(offense=r.offense, crime_count=r.crime_count) for r in by_offense if r.offense],
        by_category=[CategoryStat(category=r.category, crime_count=r.crime_count) for r in by_category if r.category],
        by_month=[MonthStat(month=r.month, crime_count=r.crime_count) for r in by_month if r.month],
    )


@app.get("/heatmap", tags=["Map"])
def get_heatmap(
    borough: Optional[str] = None,
    offense: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    year: Optional[int] = None,
    limit: int = Query(5000, ge=1, le=20000),
    db: Session = Depends(get_db),
):
    """Points lat/lng pour la heatmap Leaflet."""
    query = db.query(NypdCrime.latitude, NypdCrime.longitude)
    query = _apply_filters(query, borough, offense, date_from, date_to, year, category)
    rows = query.filter(
        NypdCrime.latitude.isnot(None), NypdCrime.longitude.isnot(None)
    ).limit(limit).all()
    return {"points": [[float(r.latitude), float(r.longitude)] for r in rows]}


@app.get("/hotspots", response_model=list[HotspotOut], tags=["Map"])
def get_hotspots(db: Session = Depends(get_db)):
    """Clusters DBSCAN calculés par le pipeline ML."""
    return db.query(Hotspot).order_by(Hotspot.crime_count.desc()).all()


@app.get("/boroughs", tags=["Filters"])
def get_boroughs(db: Session = Depends(get_db)):
    rows = (
        db.query(NypdCrime.borough)
        .filter(NypdCrime.borough.isnot(None))
        .distinct()
        .order_by(NypdCrime.borough)
        .all()
    )
    return {"boroughs": [r.borough for r in rows]}


@app.get("/offenses", tags=["Filters"])
def get_offenses(db: Session = Depends(get_db)):
    rows = (
        db.query(NypdCrime.offense)
        .filter(NypdCrime.offense.isnot(None))
        .distinct()
        .order_by(NypdCrime.offense)
        .all()
    )
    return {"offenses": [r.offense for r in rows]}


@app.get("/categories", tags=["Filters"])
def get_categories(db: Session = Depends(get_db)):
    rows = (
        db.query(NypdCrime.category)
        .filter(NypdCrime.category.isnot(None))
        .distinct()
        .order_by(NypdCrime.category)
        .all()
    )
    return {"categories": [r.category for r in rows]}


@app.get("/prediction", tags=["AI"])
def get_prediction(db: Session = Depends(get_db)):
    top_boroughs = (
        db.query(NypdCrime.borough, func.count().label("crime_count"))
        .filter(NypdCrime.borough.isnot(None))
        .group_by(NypdCrime.borough)
        .order_by(func.count().desc())
        .limit(5)
        .all()
    )
    top_offenses = (
        db.query(NypdCrime.offense, func.count().label("crime_count"))
        .filter(NypdCrime.offense.isnot(None))
        .group_by(NypdCrime.offense)
        .order_by(func.count().desc())
        .limit(5)
        .all()
    )
    return {
        "top_risk_boroughs": [{"borough": r.borough, "crime_count": r.crime_count} for r in top_boroughs],
        "top_offenses": [{"offense": r.offense, "crime_count": r.crime_count} for r in top_offenses],
    }
