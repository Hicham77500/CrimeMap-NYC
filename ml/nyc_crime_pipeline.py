from __future__ import annotations

from dataclasses import dataclass
from math import radians
from pathlib import Path

import pandas as pd

try:
    from sklearn.cluster import DBSCAN
except Exception:  # pragma: no cover - optional during bootstrap
    DBSCAN = None


# NYPD Complaint Data Current (Year To Date) — ~133K lignes, mise à jour trimestrielle
DATASET_URL_YTD = "https://data.cityofnewyork.us/resource/5uac-w243.csv?$limit=150000"

# NYPD Complaint Data Historic — 10.1M lignes, 2006 → fin de l'année passée
DATASET_URL_HISTORIC = "https://data.cityofnewyork.us/resource/qgea-i56i.csv?$limit=100000"

# Source par défaut : API YTD (pas besoin de télécharger quoi que ce soit)
DATASET_URL = DATASET_URL_YTD

# Chemins locaux optionnels — si présents, le pipeline les utilise à la place de l'API
LOCAL_YTD = Path("data/processed/5uac-w243.csv")
LOCAL_HISTORIC = Path("data/processed/qgea-i56i.csv")

CANONICAL_COLUMNS = ["id", "date", "borough", "crime_type", "latitude", "longitude"]

BOROUGH_NORMALIZATION = {
    "BRONX": "Bronx",
    "BROOKLYN": "Brooklyn",
    "MANHATTAN": "Manhattan",
    "QUEENS": "Queens",
    "STATEN ISLAND": "Staten Island",
}


@dataclass(frozen=True)
class PipelinePaths:
    raw_dir: Path
    processed_dir: Path

    @property
    def raw_file(self) -> Path:
        return self.raw_dir / "nyc_crime_raw.csv"

    @property
    def clean_file(self) -> Path:
        return self.processed_dir / "nyc_crime_clean.csv"

    @property
    def hotspot_file(self) -> Path:
        return self.processed_dir / "nyc_crime_hotspots.csv"


def ensure_directories(base_dir: Path | str = Path("data")) -> PipelinePaths:
    base_dir = Path(base_dir)
    raw_dir = base_dir / "raw"
    processed_dir = base_dir / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    return PipelinePaths(raw_dir=raw_dir, processed_dir=processed_dir)


def load_source_data(source: str | Path = DATASET_URL) -> pd.DataFrame:
    source_path = Path(str(source))
    if source_path.exists():
        return pd.read_csv(source_path)
    return pd.read_csv(str(source))


def _normalize_borough(value: object) -> str | None:
    if pd.isna(value):
        return None
    normalized = str(value).strip().upper()
    if not normalized:
        return None
    return BOROUGH_NORMALIZATION.get(normalized, normalized.title())


def clean_crime_data(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    # Normalise toutes les colonnes en minuscule pour gérer API (lowercase) et CSV brut
    data.columns = [col.lower() for col in data.columns]

    if "cmplnt_fr_dt" in data.columns:
        data["date"] = pd.to_datetime(data["cmplnt_fr_dt"], errors="coerce").dt.strftime("%Y-%m-%d")
    elif "date" not in data.columns:
        data["date"] = None

    if "boro_nm" in data.columns:
        data["borough"] = data["boro_nm"].map(_normalize_borough)
    elif "borough" not in data.columns:
        data["borough"] = None

    if "ofns_desc" in data.columns:
        data["crime_type"] = data["ofns_desc"].fillna("Unknown").astype(str).str.strip()
    elif "crime_type" not in data.columns:
        data["crime_type"] = "Unknown"

    data["latitude"] = pd.to_numeric(data.get("latitude"), errors="coerce")
    data["longitude"] = pd.to_numeric(data.get("longitude"), errors="coerce")

    if "cmplnt_num" in data.columns:
        data["id"] = data["cmplnt_num"]
    elif "id" not in data.columns:
        data.insert(0, "id", range(1, len(data) + 1))

    cleaned = data.loc[:, [column for column in CANONICAL_COLUMNS if column in data.columns]].copy()
    cleaned = cleaned.dropna(subset=["date", "borough", "crime_type", "latitude", "longitude"])
    cleaned = cleaned.drop_duplicates(subset=["id"])
    cleaned = cleaned[
        cleaned["latitude"].between(40.4, 41.2) & cleaned["longitude"].between(-74.5, -73.5)
    ]
    return cleaned.reset_index(drop=True)


def build_time_stats(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    return (
        data.assign(month=data["date"].dt.to_period("M").astype(str))
        .groupby(["month", "borough"], dropna=False)
        .size()
        .reset_index(name="crime_count")
        .sort_values(["month", "crime_count"], ascending=[True, False])
    )


def build_hotspots(frame: pd.DataFrame, eps_km: float = 0.5, min_samples: int = 10) -> pd.DataFrame:
    if DBSCAN is None:
        raise RuntimeError("scikit-learn is required for hotspot clustering")

    data = frame.dropna(subset=["latitude", "longitude"]).copy()
    if data.empty:
        return pd.DataFrame(columns=["cluster_id", "latitude", "longitude", "crime_count"])

    coordinates = [[radians(lat), radians(lon)] for lat, lon in zip(data["latitude"], data["longitude"])]
    labels = DBSCAN(eps=eps_km / 6371.0, min_samples=min_samples, metric="haversine").fit_predict(coordinates)
    data = data.assign(cluster_id=labels)
    return (
        data[data["cluster_id"] != -1]
        .groupby("cluster_id", as_index=False)
        .agg(latitude=("latitude", "mean"), longitude=("longitude", "mean"), crime_count=("cluster_id", "size"))
        .sort_values("crime_count", ascending=False)
    )


def build_dashboard_stats(raw: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Génère toutes les agrégations nécessaires au dashboard depuis les données brutes."""
    data = raw.copy()
    data.columns = [col.lower() for col in data.columns]

    # Date + heure
    data["_date"] = pd.to_datetime(data.get("cmplnt_fr_dt"), errors="coerce")
    data["_month"] = data["_date"].dt.to_period("M").astype(str)
    data["_year"] = data["_date"].dt.year
    if "cmplnt_fr_tm" in data.columns:
        data["_hour"] = pd.to_numeric(
            data["cmplnt_fr_tm"].astype(str).str[:2], errors="coerce"
        )
    else:
        data["_hour"] = None

    borough_col = "boro_nm" if "boro_nm" in data.columns else "borough"
    crime_col = "ofns_desc" if "ofns_desc" in data.columns else "crime_type"
    law_col = "law_cat_cd" if "law_cat_cd" in data.columns else None

    by_borough = (
        data.groupby(borough_col, dropna=True)
        .size()
        .reset_index(name="crime_count")
        .rename(columns={borough_col: "borough"})
        .sort_values("crime_count", ascending=False)
    )

    by_crime_type = (
        data.groupby(crime_col, dropna=True)
        .size()
        .reset_index(name="crime_count")
        .rename(columns={crime_col: "crime_type"})
        .sort_values("crime_count", ascending=False)
        .head(20)
    )

    by_hour = (
        data.dropna(subset=["_hour"])
        .groupby("_hour")
        .size()
        .reset_index(name="crime_count")
        .rename(columns={"_hour": "hour"})
        .sort_values("hour")
    ) if "_hour" in data.columns else pd.DataFrame(columns=["hour", "crime_count"])

    by_law_category = (
        data.groupby(law_col, dropna=True)
        .size()
        .reset_index(name="crime_count")
        .rename(columns={law_col: "law_category"})
        .sort_values("crime_count", ascending=False)
    ) if law_col else pd.DataFrame(columns=["law_category", "crime_count"])

    by_month = (
        data.groupby("_month", dropna=True)
        .size()
        .reset_index(name="crime_count")
        .rename(columns={"_month": "month"})
        .sort_values("month")
    )

    return {
        "by_borough": by_borough,
        "by_crime_type": by_crime_type,
        "by_hour": by_hour,
        "by_law_category": by_law_category,
        "by_month": by_month,
    }


def save_outputs(
    cleaned: pd.DataFrame,
    hotspots: pd.DataFrame,
    paths: PipelinePaths,
    stats: dict[str, pd.DataFrame] | None = None,
) -> None:
    cleaned.to_csv(paths.clean_file, index=False)
    hotspots.to_csv(paths.hotspot_file, index=False)
    if stats:
        stats_dir = paths.processed_dir / "stats"
        stats_dir.mkdir(exist_ok=True)
        for name, frame in stats.items():
            frame.to_csv(stats_dir / f"{name}.csv", index=False)


def run_pipeline(source: str | Path = DATASET_URL, base_dir: Path | str = Path("data")) -> dict[str, pd.DataFrame]:
    paths = ensure_directories(base_dir)
    raw = load_source_data(source)
    raw.to_csv(paths.raw_file, index=False)
    cleaned = clean_crime_data(raw)
    hotspots = build_hotspots(cleaned) if not cleaned.empty else pd.DataFrame()
    stats = build_dashboard_stats(raw)
    save_outputs(cleaned, hotspots, paths, stats)
    return {"raw": raw, "cleaned": cleaned, "hotspots": hotspots, "stats": stats}
