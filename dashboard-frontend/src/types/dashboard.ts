export interface MetricValue {
  value: number;
  label: string;
  prefix?: string;
  suffix?: string;
}

export interface Metrics {
  totalMarketingSpend: MetricValue;
  influencerSpend: MetricValue;
  paidAdsSpend: MetricValue;
  netRevenue: MetricValue;
  revenueSpentOnAds: MetricValue;
  customerLifetimeValue: MetricValue;
  customerAcquisitionCost: MetricValue;
  tickets: MetricValue;
  revenue: MetricValue;
}

export interface ChartDataPoint {
  date: string;
  value: number;
}

export interface DashboardData {
  metrics: Metrics;
  charts: {
    barChart: ChartDataPoint[];
    lineChart: ChartDataPoint[];
  };
}

export interface DailyMetric {
  date: string;
  grossRevenue: number;
  netRevenue: number;
  dailyGuests: number;
  accumulatedGuests: number;
}

export interface MetricCardProps {
  data: MetricValue;
  className?: string;
}

export interface ChartProps {
  data: ChartDataPoint[];
  className?: string;
} 