import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const colors = [
  { ttft: '#d97706', latency: '#dc2626' }, // Bench 1: orange/red
  { ttft: '#059669', latency: '#7c3aed' }, // Bench 2: emerald/purple
  { ttft: '#f59e0b', latency: '#ef4444' }, // Bench 3: amber/red
  { ttft: '#3b82f6', latency: '#10b981' }, // Bench 4: blue/emerald
  { ttft: '#f472b6', latency: '#3b82f6' }, // Bench 5: pink/blue
  { ttft: '#a855f7', latency: '#f59e0b' }, // Bench 6: purple/amber
  { ttft: '#14b8a6', latency: '#f472b6' }, // Bench 7: teal/pink
  { ttft: '#f97316', latency: '#a855f7' }, // Bench 8: orange/purple
];

function prepareChartData(benchmarks) {
  const dataMap = new Map();

  benchmarks.forEach((bench, idx) => {
    (bench.results || []).forEach((entry) => {
      const promptSize = entry.prompt_size;
      if (!dataMap.has(promptSize)) {
        dataMap.set(promptSize, { promptSize });
      }
      const item = dataMap.get(promptSize);
      item[`ttft_${idx}`] = entry.stats.ttft_ms.median;
      item[`ttft_${idx}_p95`] = entry.stats.ttft_ms.p95;
      item[`ttft_${idx}_p99`] = entry.stats.ttft_ms.p99;
      item[`latency_${idx}`] = entry.stats.total_latency_ms.median;
      item[`latency_${idx}_p95`] = entry.stats.total_latency_ms.p95;
      item[`latency_${idx}_p99`] = entry.stats.total_latency_ms.p99;
    });
  });

  return Array.from(dataMap.values()).sort((a, b) => a.promptSize - b.promptSize);
}

function TTftChart({ benchmarks, chartData }) {
  if (benchmarks.length === 0) return null;

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Time to first token (ttft)</h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="promptSize"
            stroke="#6b7280"
            tick={{ fontSize: 12 }}
            label={{ value: 'prompt size (tokens)', position: 'insideBottom', offset: -5, fill: '#6b7280' }}
          />
          <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} unit=" ms" />
          <Tooltip
            contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
            labelStyle={{ color: '#374151' }}
          />
          <Legend />
          {benchmarks.map((bench, idx) => {
            const color = colors[idx] || colors[idx % colors.length];
            return (
              <React.Fragment key={`ttft-${bench.index}`}>
                <Line
                  type="monotone"
                  dataKey={`ttft_${idx}`}
                  stroke={color.ttft}
                  strokeWidth={2}
                  dot={{ fill: color.ttft, r: 4 }}
                  name={`benchmark ${idx + 1} (median)`}
                />
                <Line
                  type="monotone"
                  dataKey={`ttft_${idx}_p95`}
                  stroke={color.ttft}
                  strokeWidth={1}
                  strokeDasharray="5 5"
                  dot={false}
                  opacity={0.5}
                  name={`benchmark ${idx + 1} (p95)`}
                />
                <Line
                  type="monotone"
                  dataKey={`ttft_${idx}_p99`}
                  stroke={color.ttft}
                  strokeWidth={1}
                  strokeDasharray="2 2"
                  dot={false}
                  opacity={0.3}
                  name={`benchmark ${idx + 1} (p99)`}
                />
              </React.Fragment>
            );
          })}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function TotalLatencyChart({ benchmarks, chartData }) {
  if (benchmarks.length === 0) return null;

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Latency</h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="promptSize"
            stroke="#6b7280"
            tick={{ fontSize: 12 }}
            label={{ value: 'prompt size (tokens)', position: 'insideBottom', offset: -5, fill: '#6b7280' }}
          />
          <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} unit=" ms" />
          <Tooltip
            contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
            labelStyle={{ color: '#374151' }}
          />
          <Legend />
          {benchmarks.map((bench, idx) => {
            const color = colors[idx] || colors[idx % colors.length];
            return (
              <React.Fragment key={`latency-${bench.index}`}>
                <Line
                  type="monotone"
                  dataKey={`latency_${idx}`}
                  stroke={color.latency}
                  strokeWidth={2}
                  dot={{ fill: color.latency, r: 4 }}
                  name={`benchmark ${idx + 1} (median)`}
                />
                <Line
                  type="monotone"
                  dataKey={`latency_${idx}_p95`}
                  stroke={color.latency}
                  strokeWidth={1}
                  strokeDasharray="5 5"
                  dot={false}
                  opacity={0.5}
                  name={`benchmark ${idx + 1} (p95)`}
                />
                <Line
                  type="monotone"
                  dataKey={`latency_${idx}_p99`}
                  stroke={color.latency}
                  strokeWidth={1}
                  strokeDasharray="2 2"
                  dot={false}
                  opacity={0.3}
                  name={`benchmark ${idx + 1} (p99)`}
                />
              </React.Fragment>
            );
          })}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function LatencyCharts({ benchmarks }) {
  if (!benchmarks || benchmarks.length === 0) return null;

  const chartData = prepareChartData(benchmarks);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <TTftChart benchmarks={benchmarks} chartData={chartData} />
      <TotalLatencyChart benchmarks={benchmarks} chartData={chartData} />
    </div>
  );
}

import React from 'react';