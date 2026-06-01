from __future__ import annotations

import sqlite3
from math import radians
from pathlib import Path

import pandas as pd

LIMIT = 100_000  # Augmenter à 500_000 pour le jeu complet

URL = (
    "https://data.cityofnewyork.us/resource/qgea-i56i.csv"
    f"?$limit={LIMIT}"
    "&$select=cmplnt_fr_dt,ofns_desc,boro_nm,latitude,longitude,law_cat_cd,addr_pct_cd"
)

DB_PATH = Path(__file__).parent.parent / "data" / "nypd_crimes.db"


def download_and_clean() -> pd.DataFrame:
    print(f"Téléchargement NYC Open Data ({LIMIT:,} lignes)...")
    print("  Connexion à l'API... (peut prendre 30-60s)", flush=True)
    df = pd.read_csv(URL)
    print(f"  ✓ {len(df):,} lignes reçues", flush=True)

    df = df.rename(columns={
        "cmplnt_fr_dt": "date",
        "ofns_desc":    "offense",
        "boro_nm":      "borough",
        "law_cat_cd":   "category",
        "addr_pct_cd":  "precinct",
    })

    df["date"]      = pd.to_datetime(df["date"],     errors="coerce")
    df["latitude"]  = pd.to_numeric(df["latitude"],  errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    df = df.dropna(subset=["date", "latitude", "longitude"])
    df = df[df["latitude"].between(40.4, 41.0) & df["longitude"].between(-74.3, -73.7)]

    for col in ["offense", "borough", "category"]:
        df[col] = df[col].astype(str).str.strip().str.upper()
        df[col] = df[col].replace({"NAN": None, "": None})

    df["precinct"] = df["precinct"].astype(str).str.strip().replace({"nan": None, "": None})
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    print(f"  Après nettoyage : {len(df):,} lignes")
    return df.reset_index(drop=True)


def compute_hotspots(df: pd.DataFrame, eps_km: float = 0.5, min_samples: int = 10) -> pd.DataFrame:
    try:
        from sklearn.cluster import DBSCAN
    except ImportError:
        print("  scikit-learn absent — hotspots ignorés")
        return pd.DataFrame(columns=["cluster_id", "latitude", "longitude", "crime_count"])

    print("  Calcul DBSCAN hotspots...")
    coords = df.dropna(subset=["latitude", "longitude"])
    coords_rad = [
        [radians(lat), radians(lon)]
        for lat, lon in zip(coords["latitude"], coords["longitude"])
    ]
    labels = DBSCAN(eps=eps_km / 6371.0, min_samples=min_samples, metric="haversine").fit_predict(coords_rad)
    tmp = coords.assign(cluster_id=labels)
    hotspots = (
        tmp[tmp["cluster_id"] != -1]
        .groupby("cluster_id", as_index=False)
        .agg(
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean"),
            crime_count=("cluster_id", "size"),
        )
        .sort_values("crime_count", ascending=False)
    )
    print(f"  {len(hotspots)} hotspots détectés")
    return hotspots


def save_to_sqlite(df: pd.DataFrame, hotspots: pd.DataFrame) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    print("  Insertion nypd_crimes...")
    df.to_sql("nypd_crimes", conn, if_exists="replace", index=True, index_label="id")

    print("  Création des index...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_date     ON nypd_crimes(date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_borough  ON nypd_crimes(borough)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_offense  ON nypd_crimes(offense)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON nypd_crimes(category)")

    if not hotspots.empty:
        hotspots.to_sql("hotspots", conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()
    print(f"  Base SQLite : {DB_PATH}")


if __name__ == "__main__":
    df = download_and_clean()
    hotspots = compute_hotspots(df)
    save_to_sqlite(df, hotspots)

    print(f"\nRésumé :")
    print(f"  Lignes insérées  : {len(df):,}")
    print(f"  Période          : {df['date'].min()} → {df['date'].max()}")
    print(f"  Boroughs         : {sorted(df['borough'].dropna().unique().tolist())}")
    print(f"  Hotspots         : {len(hotspots)}")
    print(f"\n  Lance maintenant : npm start")
