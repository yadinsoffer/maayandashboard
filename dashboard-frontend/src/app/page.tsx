'use client';

import { useEffect, useState, useCallback } from 'react';
import MetricCard from '../components/MetricCard/MetricCard';
import BarChart from '../components/BarChart/BarChart';
import LineChart from '../components/LineChart/LineChart';
import KeyInputForm from '../components/KeyInputForm/KeyInputForm';
import { triggerDashboardUpdate } from '../components/utils/ec2-api';
import type { DashboardData } from '../types/dashboard';

const REFRESH_INTERVAL = 30000; // Refresh every 30 seconds

export default function Home() {
  const [dashboardData, setDashboardData] = useState<DashboardData>({
    metrics: {
      totalMarketingSpend: { value: 0, label: 'Total Marketing Spend', prefix: '$' },
      influencerSpend: { value: 0, label: 'Influencer Spend', prefix: '$' },
      paidAdsSpend: { value: 0, label: 'Paid Ads Spend', prefix: '$' },
      netRevenue: { value: 0, label: 'Net Revenue', prefix: '$' },
      revenueSpentOnAds: { value: 0, label: 'Revenue Spent on Ads', suffix: '%' },
      customerLifetimeValue: { value: 0, label: 'Customer Lifetime Value', prefix: '$' },
      customerAcquisitionCost: { value: 0, label: 'Customer Acquisition Cost', prefix: '$' },
      tickets: { value: 0, label: 'Tickets' },
      revenue: { value: 0, label: 'Revenue', prefix: '$' }
    },
    charts: {
      barChart: [],
      lineChart: []
    }
  });
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showKeyForm, setShowKeyForm] = useState(false);

  const fetchDashboardData = useCallback(async () => {
    try {
      const response = await fetch('/api/metrics');
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data');
      }
      const data = await response.json();
      setDashboardData(data);
      setLoading(false);
      setError(null);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to load dashboard data');
      setLoading(false);
    }
  }, []);

  const updateDashboard = useCallback(async () => {
    setLoading(true);
    setError(null);
    setShowKeyForm(false);
    
    try {
      console.log('Triggering dashboard update...');
      // Trigger the update process on the EC2 server
      const updateResult = await triggerDashboardUpdate();
      console.log('Update result:', updateResult);
      
      if (updateResult.success) {
        // If update was successful, fetch the latest data
        console.log('Update successful, fetching dashboard data...');
        await fetchDashboardData();
      } else if (updateResult.error === 'KEY_ERROR') {
        // If update failed due to key error, show the key input form
        console.log('KEY_ERROR detected, showing key input form');
        setShowKeyForm(true);
        setError('Dashboard update failed: Invalid or expired key');
        setLoading(false);
      } else {
        // If update failed for other reasons
        console.log('Update failed for other reasons:', updateResult.error);
        setError(updateResult.message || 'Failed to update dashboard');
        setLoading(false);
      }
    } catch (error) {
      console.error('Error updating dashboard:', error);
      setError('Failed to connect to the update server');
      setLoading(false);
    }
  }, [fetchDashboardData]);

  const handleKeySuccess = async () => {
    // After successful key submission, try updating the dashboard again
    await updateDashboard();
  };

  useEffect(() => {
    // Initial update when the page loads
    updateDashboard();

    // Set up periodic refresh
    const intervalId = setInterval(fetchDashboardData, REFRESH_INTERVAL);

    // Cleanup on unmount
    return () => clearInterval(intervalId);
  }, [updateDashboard, fetchDashboardData]);

  // If we need to show the key input form
  if (showKeyForm) {
    return <KeyInputForm onSuccess={handleKeySuccess} errorMessage={error || undefined} />;
  }

  // Show loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" role="status">
            <span className="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">Loading...</span>
          </div>
          <p className="mt-2 text-gray-600">Updating dashboard...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen p-4">
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg max-w-md">
          <h2 className="text-lg font-semibold mb-2">Error</h2>
          <p className="mb-4">{error}</p>
          <button 
            onClick={updateDashboard}
            className="bg-red-600 text-white py-2 px-4 rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Render the dashboard
  return (
    <main className="p-4 md:p-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {Object.entries(dashboardData.metrics).map(([key, metric]) => (
          <MetricCard 
            key={key}
            data={metric}
          />
        ))}
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {dashboardData.charts.barChart.length > 0 && (
          <div className="bg-white p-4 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Monthly Performance</h2>
            <BarChart data={dashboardData.charts.barChart} />
          </div>
        )}
        
        {dashboardData.charts.lineChart.length > 0 && (
          <div className="bg-white p-4 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Trend Analysis</h2>
            <LineChart data={dashboardData.charts.lineChart} />
          </div>
        )}
      </div>
    </main>
  );
}
