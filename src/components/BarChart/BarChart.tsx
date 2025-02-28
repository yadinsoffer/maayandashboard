import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { ChartProps } from '@/types/dashboard';
import { format, zonedTimeToUtc } from 'date-fns-tz';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    title: {
      display: false,
    },
  },
  scales: {
    x: {
      grid: {
        display: false,
      },
      ticks: {
        color: '#fff',
      },
    },
    y: {
      grid: {
        color: 'rgba(255, 255, 255, 0.1)',
      },
      ticks: {
        color: '#fff',
      },
    },
  },
};

const BarChart: React.FC<ChartProps> = ({ data, className = '' }) => {
  const chartData = {
    labels: data.map(item => {
      const date = new Date(item.timestamp + 'T00:00:00');
      return format(date, 'dd MMM');
    }),
    datasets: [
      {
        data: data.map(item => item.value),
        backgroundColor: 'rgba(54, 162, 235, 0.8)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className={`h-[300px] ${className}`}>
      <Bar options={options} data={chartData} />
    </div>
  );
};

export default BarChart; 