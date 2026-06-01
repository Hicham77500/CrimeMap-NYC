import type { Filters } from "../types";

interface Props {
  filters: Filters;
  boroughs: string[];
  offenses: string[];
  onFilterChange: (f: Filters) => void;
  onSearch: (q: string) => void;
  searchQuery: string;
}

export default function FilterBar({
  filters,
  boroughs,
  offenses,
  onFilterChange,
  onSearch,
  searchQuery,
}: Props) {
  const years = [2023, 2024, 2025, 2026];

  return (
    <aside className="filter-bar">
      <h2>Filtres</h2>

      {/* Recherche */}
      <div className="filter-group">
        <label>Recherche</label>
        <input
          type="text"
          placeholder="Ex: robbery, assault…"
          value={searchQuery}
          onChange={(e) => onSearch(e.target.value)}
        />
      </div>

      {/* Borough */}
      <div className="filter-group">
        <label>Borough</label>
        <select
          value={filters.borough ?? ""}
          onChange={(e) =>
            onFilterChange({ ...filters, borough: e.target.value || undefined })
          }
        >
          <option value="">Tous</option>
          {boroughs.map((b) => (
            <option key={b} value={b}>
              {b}
            </option>
          ))}
        </select>
      </div>

      {/* Année */}
      <div className="filter-group">
        <label>Année</label>
        <select
          value={filters.year ?? ""}
          onChange={(e) =>
            onFilterChange({
              ...filters,
              year: e.target.value ? Number(e.target.value) : undefined,
            })
          }
        >
          <option value="">Toutes</option>
          {years.map((y) => (
            <option key={y} value={y}>
              {y}
            </option>
          ))}
        </select>
      </div>

      {/* Infraction */}
      <div className="filter-group">
        <label>Infraction</label>
        <select
          value={filters.offense ?? ""}
          onChange={(e) =>
            onFilterChange({ ...filters, offense: e.target.value || undefined })
          }
        >
          <option value="">Toutes</option>
          {offenses.slice(0, 60).map((t) => (
            <option key={t} value={t}>
              {t.length > 30 ? t.slice(0, 28) + "…" : t}
            </option>
          ))}
        </select>
      </div>

      {/* Date from */}
      <div className="filter-group">
        <label>Du</label>
        <input
          type="date"
          value={filters.date_from ?? ""}
          onChange={(e) =>
            onFilterChange({ ...filters, date_from: e.target.value || undefined })
          }
        />
      </div>

      {/* Date to */}
      <div className="filter-group">
        <label>Au</label>
        <input
          type="date"
          value={filters.date_to ?? ""}
          onChange={(e) =>
            onFilterChange({ ...filters, date_to: e.target.value || undefined })
          }
        />
      </div>

      {/* Reset */}
      <button
        className="btn-reset"
        onClick={() => {
          onFilterChange({});
          onSearch("");
        }}
      >
        Réinitialiser
      </button>
    </aside>
  );
}
