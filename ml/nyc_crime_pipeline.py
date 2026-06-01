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

    coordinates = data[["latitude", "longitude"]].apply(lambda row: [radians(row[0]), radians(row[1])], axis=1).to_list()
    labels = DBSCAN(eps=eps_km / 6371.0, min_samples=min_samples, metric="haversine").fit_predict(coordinates)
    data = data.assign(cluster_id=labels)
    return (
        data[data["cluster_id"] != -1]
        .groupby("cluster_id", as_index=False)
        .agg(latitude=("latitude", "mean"), longitude=("longitude", "mean"), crime_count=("cluster_id", "size"))
        .sort_values("crime_count", ascending=False)
    )


def save_outputs(cleaned: pd.DataFrame, hotspots: pd.DataFrame, paths: PipelinePaths) -> None:
    cleaned.to_csv(paths.clean_file, index=False)
    hotspots.to_csv(paths.hotspot_file, index=False)


def run_pipeline(source: str | Path = DATASET_URL, base_dir: Path | str = Path("data")) -> dict[str, pd.DataFrame]:
    paths = ensure_directories(base_dir)
    raw = load_source_data(source)
    raw.to_csv(paths.raw_file, index=False)
    cleaned = clean_crime_data(raw)
    hotspots = build_hotspots(cleaned) if not cleaned.empty else pd.DataFrame()
    save_outputs(cleaned, hotspots, paths)
    return {"raw": raw, "cleaned": cleaned, "hotspots": hotspots}
