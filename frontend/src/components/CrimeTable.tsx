import type { Crime, PaginatedCrimes } from "../types";

interface Props {
  result: PaginatedCrimes | null;
  page: number;
  onPageChange: (p: number) => void;
  loading: boolean;
}

export default function CrimeTable({ result, page, onPageChange, loading }: Props) {
  if (loading) return <div className="loading">Chargement…</div>;
  if (!result || result.items.length === 0)
    return <div className="no-data">Aucun résultat</div>;

  const totalPages = Math.ceil(result.total / result.page_size);

  return (
    <div className="crime-table-wrapper">
      <div className="table-meta">
        {result.total.toLocaleString()} résultats — page {page}/{totalPages}
      </div>
      <table className="crime-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Borough</th>
            <th>Infraction</th>
            <th>Lat</th>
            <th>Lng</th>
          </tr>
        </thead>
        <tbody>
          {result.items.map((c: Crime) => (
            <tr key={c.id}>
              <td>{c.date}</td>
              <td>{c.borough}</td>
              <td title={c.offense ?? ""}>
                {(c.offense ?? "").length > 28 ? (c.offense ?? "").slice(0, 26) + "…" : (c.offense ?? "-")}
              </td>
              <td>{Number(c.latitude).toFixed(4)}</td>
              <td>{Number(c.longitude).toFixed(4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="pagination">
        <button disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
          ‹ Préc.
        </button>
        <span>
          {page} / {totalPages}
        </span>
        <button disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>
          Suiv. ›
        </button>
      </div>
    </div>
  );
}
