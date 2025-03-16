export interface GeckoboardMetrics {
  timestamp: string;
  customer_acquisition_cost: number;  // in cents
  customer_lifetime_value: number;    // in cents
  revenue_spent_on_ads: number;       // decimal (0-1)
  revenue_after_stripe: number;       // in cents
  accumulated_tickets: number;
  total_marketing_spend: number;      // in cents
  influencer_spend: number;           // in cents
  paid_ads_spend: number;            // in cents
  historical_spend: number;          // in cents
  net_revenue: number;               // in cents
  operational_expenses: number;      // in dollars
}

export interface DailyRevenue {
  date: string;
  gross_revenue: number;            // in cents
  net_revenue: number;              // in cents
  daily_guests: number;
  accumulated_guests: number;
  accumulated_net: number;          // in cents
}

// Frontend display types
export interface MetricData {
  value: number;
  label: string;
  prefix?: string;
  suffix?: string;
}

export interface TimeseriesData {
  timestamp: string;
  value: number;
}

export interface DashboardData {
  metrics: {
    totalMarketingSpend: MetricData;
    influencerSpend: MetricData;
    paidAdsSpend: MetricData;
    netRevenue: MetricData;
    revenueSpentOnAds: MetricData;
    customerLifetimeValue: MetricData;
    customerAcquisitionCost: MetricData;
    tickets: MetricData;
    revenue: MetricData;
    operationalExpenses: MetricData;
  };
  charts: {
    barChart: TimeseriesData[];
    lineChart: TimeseriesData[];
  };
}

export interface MetricCardProps {
  data: MetricData;
  className?: string;
}

export interface ChartProps {
  data: DailyMetrics[];
  className?: string;
}

export interface DailyMetrics {
  timestamp: string;
  value: number;
}

export interface Metrics {
  dailyMetrics: DailyMetrics[];
  totalMarketingSpend: number;
  totalRevenue: number;
  totalGuests: number;
  cac: number;
  netRevenue: number;
}

// Utility function to convert cents to dollars
export function centsToDollars(cents: number): number {
  return cents / 100;
}

// Transform Geckoboard data to frontend format
export function transformGeckoboardData(data: GeckoboardMetrics): Partial<DashboardData['metrics']> {
  return {
    totalMarketingSpend: { 
      value: centsToDollars(data.total_marketing_spend), 
      label: 'Total Marketing Spend', 
      prefix: '$' 
    },
    influencerSpend: { 
      value: centsToDollars(data.influencer_spend), 
      label: 'Influencer Spend', 
      prefix: '$' 
    },
    paidAdsSpend: { 
      value: centsToDollars(data.paid_ads_spend), 
      label: 'Paid Ads Spend', 
      prefix: '$' 
    },
    netRevenue: { 
      value: centsToDollars(data.net_revenue), 
      label: 'Net Revenue', 
      prefix: '$' 
    },
    revenueSpentOnAds: { 
      value: data.revenue_spent_on_ads * 100, 
      label: 'Revenue Spent on Ads', 
      suffix: '%' 
    },
    customerLifetimeValue: { 
      value: centsToDollars(data.customer_lifetime_value), 
      label: 'Customer Lifetime Value', 
      prefix: '$' 
    },
    customerAcquisitionCost: { 
      value: centsToDollars(data.customer_acquisition_cost), 
      label: 'Customer Acquisition Cost', 
      prefix: '$' 
    },
    tickets: { 
      value: data.accumulated_tickets, 
      label: 'Tickets' 
    },
    revenue: { 
      value: centsToDollars(data.revenue_after_stripe), 
      label: 'Revenue', 
      prefix: '$' 
    },
    operationalExpenses: { 
      value: data.operational_expenses, // Direct value since it's already in dollars
      label: 'Operational Expenses', 
      prefix: '$' 
    }
  };
}

export interface BackendMetrics {
  totalSpend: number;
  totalRevenue: number;
  totalGuests: number;
  spendToRevenueRatio: number;
  revenueSpentOnAds: number;
  customerAcquisitionCost: number;
  accumulatedNetRevenue: number;
  influencerSpend: number;
  facebookSpend: number;
  paidAdsSpend: number;
  historicalSpend: number;
  averageLtv: number;
}

export interface DailyMetric {
  date: string;
  grossRevenue: number;
  netRevenue: number;
  accumulatedNet: number;
  dailyGuests: number;
  accumulatedGuests: number;
}

export interface BackendData {
  timestamp: string;
  metrics: BackendMetrics;
  dailyMetrics: DailyMetric[];
} 