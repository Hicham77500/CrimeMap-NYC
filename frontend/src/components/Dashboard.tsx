import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import type { DashboardStats } from "../types";

const COLORS = ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#3498db", "#9b59b6", "#1abc9c", "#e91e63"];

interface Props {
  stats: DashboardStats | null;
  loading: boolean;
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="stat-card">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

export default function Dashboard({ stats, loading }: Props) {
  if (loading) return <div className="loading">Chargement des statistiques…</div>;
  if (!stats) return <div className="no-data">Aucune donnée disponible</div>;

  return (
    <div className="dashboard">
      {/* KPIs */}
      <div className="stat-cards">
        <StatCard label="Total crimes" value={stats.total.toLocaleString()} />
        <StatCard
          label="Borough le + touché"
          value={stats.by_borough[0]?.borough ?? "—"}
        />
        <StatCard
          label="Infraction la + fréquente"
          value={stats.by_offense[0]?.offense ?? "—"}
        />
      </div>

      {/* Crimes par borough */}
      <section className="chart-section">
        <h3>Crimes par borough</h3>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={stats.by_borough} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
            <XAxis dataKey="borough" tick={{ fill: "#ccc", fontSize: 12 }} />
            <YAxis tick={{ fill: "#ccc", fontSize: 12 }} />
            <Tooltip
              contentStyle={{ background: "#1e1e2e", border: "1px solid #444", color: "#fff" }}
            />
            <Bar dataKey="crime_count" fill="#e74c3c" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </section>

      {/* Tendance mensuelle */}
      <section className="chart-section">
        <h3>Tendance mensuelle</h3>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={stats.by_month} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
            <XAxis
              dataKey="month"
              tick={{ fill: "#ccc", fontSize: 10 }}
              interval="preserveStartEnd"
            />
            <YAxis tick={{ fill: "#ccc", fontSize: 12 }} />
            <Tooltip
              contentStyle={{ background: "#1e1e2e", border: "1px solid #444", color: "#fff" }}
            />
            <Line type="monotone" dataKey="crime_count" stroke="#3498db" dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </section>

      {/* Top 20 infractions */}
      <section className="chart-section">
        <h3>Top 20 infractions</h3>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart
            data={stats.by_offense.slice(0, 20)}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
            <XAxis type="number" tick={{ fill: "#ccc", fontSize: 11 }} />
            <YAxis
              type="category"
              dataKey="offense"
              tick={{ fill: "#ccc", fontSize: 10 }}
              width={115}
              tickFormatter={(v: string) => (v.length > 20 ? v.slice(0, 18) + "…" : v)}
            />
            <Tooltip
              contentStyle={{ background: "#1e1e2e", border: "1px solid #444", color: "#fff" }}
            />
            <Bar dataKey="crime_count" fill="#e67e22" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </section>

      {/* Distribution par catégorie (FELONY / MISDEMEANOR / VIOLATION) */}
      <section className="chart-section">
        <h3>Distribution par catégorie</h3>
        <ResponsiveContainer width="100%" height={240}>
          <PieChart>
            <Pie
              data={stats.by_category}
              dataKey="crime_count"
              nameKey="category"
              cx="50%"
              cy="50%"
              outerRadius={90}
              label={({ name, percent }: { name?: string; percent?: number }) =>
                name && percent != null
                  ? `${name} (${(percent * 100).toFixed(0)}%)`
                  : ""
              }
            >
              {stats.by_category.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Legend
              formatter={(v) => (
                <span style={{ color: "#ccc", fontSize: 12 }}>{v}</span>
              )}
            />
            <Tooltip
              contentStyle={{ background: "#1e1e2e", border: "1px solid #444", color: "#fff" }}
            />
          </PieChart>
        </ResponsiveContainer>
      </section>
    </div>
  );
}
