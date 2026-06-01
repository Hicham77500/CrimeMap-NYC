from pathlib import Path

from nyc_crime_pipeline import run_pipeline


if __name__ == "__main__":
    results = run_pipeline(base_dir=Path("data"))
    print(f"Raw rows: {len(results['raw'])}")
    print(f"Clean rows: {len(results['cleaned'])}")
    print(f"Hotspots: {len(results['hotspots'])}")
