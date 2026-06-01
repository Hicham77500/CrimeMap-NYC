import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import type { Hotspot, Crime, Filters } from "../types";
import HeatmapLayer from "./HeatmapLayer";
import "leaflet/dist/leaflet.css";

interface Props {
  heatmapPoints: [number, number][];
  hotspots: Hotspot[];
  crimes: Crime[];
  showHeatmap: boolean;
  showHotspots: boolean;
  showCrimes: boolean;
  filters: Filters;
}

export default function CrimeMap({
  heatmapPoints,
  hotspots,
  crimes,
  showHeatmap,
  showHotspots,
  showCrimes,
}: Props) {
  return (
    <MapContainer
      center={[40.73, -73.95]}
      zoom={11}
      style={{ height: "100%", width: "100%" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {showHeatmap && <HeatmapLayer points={heatmapPoints} />}

      {showHotspots &&
        hotspots.map((h) => (
          <CircleMarker
            key={h.cluster_id}
            center={[h.latitude, h.longitude]}
            radius={Math.min(6 + Math.sqrt(h.crime_count), 30)}
            pathOptions={{ color: "#c0392b", fillColor: "#e74c3c", fillOpacity: 0.7 }}
          >
            <Popup>
              <strong>Hotspot #{h.cluster_id}</strong>
              <br />
              {h.crime_count} crimes
            </Popup>
          </CircleMarker>
        ))}

      {showCrimes &&
        crimes.slice(0, 300).map((c) => (
          <CircleMarker
            key={c.id}
            center={[c.latitude, c.longitude]}
            radius={4}
            pathOptions={{ color: "#2980b9", fillColor: "#3498db", fillOpacity: 0.6 }}
          >
            <Popup>
              <strong>{c.offense}</strong>
              <br />
              {c.borough} — {c.date}
            </Popup>
          </CircleMarker>
        ))}
    </MapContainer>
  );
}
