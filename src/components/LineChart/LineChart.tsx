import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { ChartProps } from '@/types/dashboard';
import { format, zonedTimeToUtc } from 'date-fns-tz';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
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
    tooltip: {
      callbacks: {
        label: function(context: any) {
          return `$${context.parsed.y.toLocaleString()}`;
        }
      }
    }
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
        callback: function(value: any) {
          return `$${value.toLocaleString()}`;
        }
      },
    },
  },
  elements: {
    line: {
      tension: 0.4,
    },
  },
};

const LineChart: React.FC<ChartProps> = ({ data, className = '' }) => {
  const chartData = {
    labels: data.map(item => {
      const date = new Date(item.timestamp + 'T00:00:00');
      return format(date, 'dd MMM');
    }),
    datasets: [
      {
        data: data.map(item => item.value),
        borderColor: 'rgba(54, 162, 235, 1)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        fill: true,
      },
    ],
  };

  return (
    <div className={`h-[300px] ${className}`}>
      <Line options={options} data={chartData} />
    </div>
  );
};

export default LineChart; 
