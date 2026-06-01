import { useState, useEffect, useCallback, useRef } from "react";
import type { Filters, DashboardStats, Hotspot, PaginatedCrimes } from "./types";
import {
  fetchStats,
  fetchHeatmap,
  fetchHotspots,
  fetchCrimes,
  searchCrimes,
  fetchBoroughs,
  fetchOffenses,
} from "./api";
import CrimeMap from "./components/CrimeMap";
import Dashboard from "./components/Dashboard";
import FilterBar from "./components/FilterBar";
import CrimeTable from "./components/CrimeTable";
import "./App.css";

type Tab = "map" | "dashboard" | "table";

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>("map");
  const [filters, setFilters] = useState<Filters>({});
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(1);

  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showHotspots, setShowHotspots] = useState(true);
  const [showCrimes, setShowCrimes] = useState(false);

  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [heatmapPoints, setHeatmapPoints] = useState<[number, number][]>([]);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [crimesResult, setCrimesResult] = useState<PaginatedCrimes | null>(null);
  const [boroughs, setBoroughs] = useState<string[]>([]);
  const [offenses, setOffenses] = useState<string[]>([]);

  const [loadingStats, setLoadingStats] = useState(false);
  const [loadingMap, setLoadingMap] = useState(false);
  const [loadingTable, setLoadingTable] = useState(false);

  const searchTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    fetchBoroughs().then(setBoroughs).catch(() => {});
    fetchOffenses().then(setOffenses).catch(() => {});
    fetchHotspots().then(setHotspots).catch(() => {});
  }, []);

  useEffect(() => {
    setLoadingStats(true);
    fetchStats(filters)
      .then(setStats)
      .catch(() => setStats(null))
      .finally(() => setLoadingStats(false));

    setLoadingMap(true);
    fetchHeatmap(filters)
      .then(setHeatmapPoints)
      .catch(() => setHeatmapPoints([]))
      .finally(() => setLoadingMap(false));
  }, [filters]);

  const loadTable = useCallback(() => {
    setLoadingTable(true);
    const req = searchQuery.trim()
      ? searchCrimes(searchQuery, filters, page)
      : fetchCrimes(filters, page);
    req
      .then(setCrimesResult)
      .catch(() => setCrimesResult(null))
      .finally(() => setLoadingTable(false));
  }, [filters, page, searchQuery]);

  useEffect(() => {
    loadTable();
  }, [loadTable]);

  const handleSearch = (q: string) => {
    setSearchQuery(q);
    setPage(1);
    if (searchTimer.current) clearTimeout(searchTimer.current);
    searchTimer.current = setTimeout(loadTable, 400);
  };

  const handleFilterChange = (f: Filters) => {
    setFilters(f);
    setPage(1);
  };

  return (
    <div className="app">
      <header className="app-header">
        <span className="logo">🗽 CrimeMap NYC</span>
        <nav className="tabs">
          {(["map", "dashboard", "table"] as Tab[]).map((t) => (
            <button
              key={t}
              className={`tab ${activeTab === t ? "active" : ""}`}
              onClick={() => setActiveTab(t)}
            >
              {t === "map" ? "🗺 Carte" : t === "dashboard" ? "📊 Dashboard" : "📋 Données"}
            </button>
          ))}
        </nav>
      </header>

      <div className="main-layout">
        <FilterBar
          filters={filters}
          boroughs={boroughs}
          offenses={offenses}
          onFilterChange={handleFilterChange}
          onSearch={handleSearch}
          searchQuery={searchQuery}
        />

        <main className="content">
          {activeTab === "map" && (
            <>
              <div className="map-controls">
                <label>
                  <input type="checkbox" checked={showHeatmap} onChange={(e) => setShowHeatmap(e.target.checked)} />
                  Heatmap
                </label>
                <label>
                  <input type="checkbox" checked={showHotspots} onChange={(e) => setShowHotspots(e.target.checked)} />
                  Hotspots DBSCAN
                </label>
                <label>
                  <input type="checkbox" checked={showCrimes} onChange={(e) => setShowCrimes(e.target.checked)} />
                  Points individuels
                </label>
                {loadingMap && <span className="badge">Chargement…</span>}
              </div>
              <div className="map-container">
                <CrimeMap
                  heatmapPoints={heatmapPoints}
                  hotspots={hotspots}
                  crimes={crimesResult?.items ?? []}
                  showHeatmap={showHeatmap}
                  showHotspots={showHotspots}
                  showCrimes={showCrimes}
                  filters={filters}
                />
              </div>
            </>
          )}
          {activeTab === "dashboard" && <Dashboard stats={stats} loading={loadingStats} />}
          {activeTab === "table" && (
            <CrimeTable result={crimesResult} page={page} onPageChange={setPage} loading={loadingTable} />
          )}
        </main>
      </div>
    </div>
  );
}
