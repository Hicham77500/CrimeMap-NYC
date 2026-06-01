import axios from "axios";
import type { Filters, PaginatedCrimes, DashboardStats, Hotspot } from "./types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const api = axios.create({ baseURL: BASE_URL });

function toParams(filters: Filters & Record<string, unknown>) {
  const params: Record<string, string> = {};
  for (const [k, v] of Object.entries(filters)) {
    if (v !== undefined && v !== "" && v !== null) {
      params[k] = String(v);
    }
  }
  return params;
}

export async function fetchCrimes(
  filters: Filters,
  page = 1,
  pageSize = 50
): Promise<PaginatedCrimes> {
  const { data } = await api.get<PaginatedCrimes>("/crimes", {
    params: { ...toParams(filters as Record<string, unknown>), page, page_size: pageSize },
  });
  return data;
}

export async function searchCrimes(
  q: string,
  filters: Filters,
  page = 1,
  pageSize = 50
): Promise<PaginatedCrimes> {
  const { data } = await api.get<PaginatedCrimes>("/crimes/search", {
    params: { q, ...toParams(filters as Record<string, unknown>), page, page_size: pageSize },
  });
  return data;
}

export async function fetchStats(filters: Filters): Promise<DashboardStats> {
  const { data } = await api.get<DashboardStats>("/stats", {
    params: toParams(filters as Record<string, unknown>),
  });
  return data;
}

export async function fetchHeatmap(
  filters: Filters,
  limit = 5000
): Promise<[number, number][]> {
  const { data } = await api.get<{ points: [number, number][] }>("/heatmap", {
    params: { ...toParams(filters as Record<string, unknown>), limit },
  });
  return data.points;
}

export async function fetchHotspots(): Promise<Hotspot[]> {
  const { data } = await api.get<Hotspot[]>("/hotspots");
  return data;
}

export async function fetchBoroughs(): Promise<string[]> {
  const { data } = await api.get<{ boroughs: string[] }>("/boroughs");
  return data.boroughs;
}

export async function fetchOffenses(): Promise<string[]> {
  const { data } = await api.get<{ offenses: string[] }>("/offenses");
  return data.offenses;
}

export async function fetchCategories(): Promise<string[]> {
  const { data } = await api.get<{ categories: string[] }>("/categories");
  return data.categories;
}
