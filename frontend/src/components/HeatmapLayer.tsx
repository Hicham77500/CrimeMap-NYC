import { useEffect, useRef } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
// leaflet.heat has no bundled types
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import "leaflet.heat/dist/leaflet-heat.js";

interface Props {
  points: [number, number][];
}

// leaflet.heat injecte L.heatLayer sur l'objet L global
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const lAny = L as any;

export default function HeatmapLayer({ points }: Props) {
  const map = useMap();
  const layerRef = useRef<L.Layer | null>(null);

  useEffect(() => {
    if (!lAny.heatLayer) return;
    if (layerRef.current) {
      map.removeLayer(layerRef.current);
    }
    if (points.length > 0) {
      const layer = lAny.heatLayer(points, {
        radius: 20,
        blur: 15,
        maxZoom: 14,
        gradient: { 0.2: "#ffffb2", 0.5: "#fd8d3c", 0.8: "#e31a1c", 1.0: "#800026" },
      });
      layer.addTo(map);
      layerRef.current = layer;
    }
    return () => {
      if (layerRef.current) {
        map.removeLayer(layerRef.current);
        layerRef.current = null;
      }
    };
  }, [map, points]);

  return null;
}
