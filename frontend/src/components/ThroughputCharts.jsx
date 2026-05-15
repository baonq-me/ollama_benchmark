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
  { primary: '#0891b2', secondary: '#d97706' }, // Bench 1: cyan/orange
  { primary: '#7c3aed', secondary: '#dc2626' }, // Bench 2: purple/red
  { primary: '#f59e0b', secondary: '#10b981' }, // Bench 3: amber/emerald
  { primary: '#ef4444', secondary: '#3b82f6' }, // Bench 4: red/blue
  { primary: '#10b981', secondary: '#f472b6' }, // Bench 5: emerald/pink
  { primary: '#3b82f6', secondary: '#a855f7' }, // Bench 6: blue/purple
  { primary: '#f472b6', secondary: '#14b8a6' }, // Bench 7: pink/teal
  { primary: '#a855f7', secondary: '#f97316' }, // Bench 8: purple/orange
];

function prepareChartData(benchmarks) {
  const dataMap = new Map();

  benchmarks.forEach((bench, idx) => {
    const color = colors[idx] || colors[idx % colors.length];
    (bench.results || []).forEach((entry) => {
      const promptSize = entry.prompt_size;
      if (!dataMap.has(promptSize)) {
        dataMap.set(promptSize, { promptSize });
      }
      const item = dataMap.get(promptSize);
      item[`input_tps_${idx}`] = entry.stats.input_tps.median;
      item[`input_tps_${idx}_p95`] = entry.stats.input_tps.p95;
      item[`input_tps_${idx}_p99`] = entry.stats.input_tps.p99;
      item[`output_tps_${idx}`] = entry.stats.output_tps.median;
      item[`output_tps_${idx}_p95`] = entry.stats.output_tps.p95;
      item[`output_tps_${idx}_p99`] = entry.stats.output_tps.p99;
    });
  });

  return Array.from(dataMap.values()).sort((a, b) => a.promptSize - b.promptSize);
}

function InputThroughputChart({ benchmarks, chartData }) {
  if (benchmarks.length === 0) return null;

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Input throughput (prefill)</h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="promptSize"
            stroke="#6b7280"
            tick={{ fontSize: 12 }}
            label={{ value: 'prompt size (tokens)', position: 'insideBottom', offset: -5, fill: '#6b7280' }}
          />
          <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} unit=" token/s" />
          <Tooltip
            contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
            labelStyle={{ color: '#374151' }}
          />
          <Legend />
          {benchmarks.map((bench, idx) => {
            const color = colors[idx] || colors[idx % colors.length];
            return (
              <React.Fragment key={`input-${bench.index}`}>
                <Line
                  type="monotone"
                  dataKey={`input_tps_${idx}`}
                  stroke={color.primary}
                  strokeWidth={2}
                  dot={{ fill: color.primary, r: 4 }}
                  name={`benchmark ${idx + 1} (median)`}
                />
                <Line
                  type="monotone"
                  dataKey={`input_tps_${idx}_p95`}
                  stroke={color.primary}
                  strokeWidth={1}
                  strokeDasharray="5 5"
                  dot={false}
                  opacity={0.5}
                  name={`benchmark ${idx + 1} (p95)`}
                />
                <Line
                  type="monotone"
                  dataKey={`input_tps_${idx}_p99`}
                  stroke={color.primary}
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

function OutputThroughputChart({ benchmarks, chartData }) {
  if (benchmarks.length === 0) return null;

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Output throughput (decode)</h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="promptSize"
            stroke="#6b7280"
            tick={{ fontSize: 12 }}
            label={{ value: 'prompt size (tokens)', position: 'insideBottom', offset: -5, fill: '#6b7280' }}
          />
          <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} unit=" token/s" />
          <Tooltip
            contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
            labelStyle={{ color: '#374151' }}
          />
          <Legend />
          {benchmarks.map((bench, idx) => {
            const color = colors[idx] || colors[idx % colors.length];
            return (
              <React.Fragment key={`output-${bench.index}`}>
                <Line
                  type="monotone"
                  dataKey={`output_tps_${idx}`}
                  stroke={color.secondary}
                  strokeWidth={2}
                  dot={{ fill: color.secondary, r: 4 }}
                  name={`benchmark ${idx + 1} (median)`}
                />
                <Line
                  type="monotone"
                  dataKey={`output_tps_${idx}_p95`}
                  stroke={color.secondary}
                  strokeWidth={1}
                  strokeDasharray="5 5"
                  dot={false}
                  opacity={0.5}
                  name={`benchmark ${idx + 1} (p95)`}
                />
                <Line
                  type="monotone"
                  dataKey={`output_tps_${idx}_p99`}
                  stroke={color.secondary}
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

export default function ThroughputCharts({ benchmarks }) {
  if (!benchmarks || benchmarks.length === 0) return null;

  const chartData = prepareChartData(benchmarks);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <InputThroughputChart benchmarks={benchmarks} chartData={chartData} />
      <OutputThroughputChart benchmarks={benchmarks} chartData={chartData} />
    </div>
  );
}

import React from 'react';