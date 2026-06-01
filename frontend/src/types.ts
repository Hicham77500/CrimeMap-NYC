export interface Crime {
  id: number;
  date: string;
  offense: string;
  borough: string;
  latitude: number;
  longitude: number;
  category?: string;
  precinct?: string;
}

export interface Hotspot {
  cluster_id: number;
  latitude: number;
  longitude: number;
  crime_count: number;
}

export interface PaginatedCrimes {
  total: number;
  page: number;
  page_size: number;
  items: Crime[];
}

export interface BoroughStat {
  borough: string;
  crime_count: number;
}

export interface OffenseStat {
  offense: string;
  crime_count: number;
}

export interface CategoryStat {
  category: string;
  crime_count: number;
}

export interface MonthStat {
  month: string;
  crime_count: number;
}

export interface DashboardStats {
  total: number;
  by_borough: BoroughStat[];
  by_offense: OffenseStat[];
  by_category: CategoryStat[];
  by_month: MonthStat[];
}

export interface Filters {
  borough?: string;
  offense?: string;
  category?: string;
  year?: number;
  date_from?: string;
  date_to?: string;
}
