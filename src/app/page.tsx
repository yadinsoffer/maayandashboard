import { Suspense } from 'react';
import LineChart from '@/components/LineChart/LineChart';
import BarChart from '@/components/BarChart/BarChart';
import MetricCard from '@/components/MetricCard/MetricCard';
import { Metrics } from '@/types/dashboard';

async function getData(): Promise<Metrics> {
  const res = await fetch('http://localhost:3000/api/metrics', { cache: 'no-store' });
  if (!res.ok) {
    throw new Error('Failed to fetch data');
  }
  return res.json();
}

export default async function Home() {
  const data = await getData();

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 bg-gray-900 text-white">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-8">Maayan Dashboard</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <MetricCard
            title="Total Marketing Spend"
            value={data.totalMarketingSpend}
            prefix="$"
          />
          <MetricCard
            title="Total Revenue"
            value={data.totalRevenue}
            prefix="$"
          />
          <MetricCard
            title="Total Guests"
            value={data.totalGuests}
          />
          <MetricCard
            title="CAC"
            value={data.cac}
            prefix="$"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Accumulated Net Revenue</h2>
            <LineChart data={data.dailyMetrics} />
          </div>
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Daily Net Revenue</h2>
            <BarChart data={data.dailyMetrics} />
          </div>
        </div>
      </div>
    </main>
  );
} 
