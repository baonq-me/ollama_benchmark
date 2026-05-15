import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const colors = [
  { input: '#0891b2', output: '#7c3aed' }, // Bench 1: cyan/purple
  { input: '#d97706', output: '#ec4899' }, // Bench 2: orange/pink
  { input: '#10b981', output: '#f472b6' }, // Bench 3: emerald/pink
  { input: '#3b82f6', output: '#a855f7' }, // Bench 4: blue/purple
  { input: '#ef4444', output: '#14b8a6' }, // Bench 5: red/teal
  { input: '#f59e0b', output: '#3b82f6' }, // Bench 6: amber/blue
  { input: '#f472b6', output: '#f97316' }, // Bench 7: pink/orange
  { input: '#a855f7', output: '#10b981' }, // Bench 8: purple/emerald
];

function prepareConcurrentData(benchmarks) {
  const dataMap = new Map();

  benchmarks.forEach((bench, idx) => {
    if (bench.metadata && bench.metadata.concurrent > 1 && bench.results) {
      (bench.results || []).forEach((entry) => {
        const promptSize = entry.prompt_size;
        if (!dataMap.has(promptSize)) {
          dataMap.set(promptSize, { promptSize });
        }
        const item = dataMap.get(promptSize);
        item[`input_${idx}`] = entry.stats.input_tps.median;
        item[`output_${idx}`] = entry.stats.output_tps.median;
      });
    }
  });

  return Array.from(dataMap.values()).sort((a, b) => a.promptSize - b.promptSize);
}

export default function ConcurrentCharts({ benchmarks }) {
  // Filter benchmarks that have concurrent > 1
  const concurrentBenchmarks = benchmarks.filter(
    (bench) => bench.metadata && bench.metadata.concurrent > 1 && bench.results && bench.results.length > 0
  );

  if (concurrentBenchmarks.length === 0) return null;

  const chartData = prepareConcurrentData(benchmarks);

  // Build title
  let title = '⚡ concurrent performance';
  const concurrentValues = concurrentBenchmarks.map(b => b.metadata.concurrent);
  if (concurrentBenchmarks.length === 1) {
    title += ` (concurrency=${concurrentValues[0]})`;
  } else {
    title += ` (${concurrentBenchmarks.map((b, i) => `benchmark ${i + 1}: ${b.metadata.concurrent}`).join(', ')})`;
  }

  return (
    <div className="mb-8">
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
        <p className="text-gray-500 text-sm mb-4">
          throughput under simultaneous requests. higher is better.
        </p>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="promptSize"
              stroke="#6b7280"
              tick={{ fontSize: 12 }}
              label={{ value: 'prompt size (tokens)', position: 'insideBottom', offset: -5, fill: '#6b7280' }}
            />
            <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
              labelStyle={{ color: '#374151' }}
            />
            <Legend />
            {concurrentBenchmarks.map((bench, idx) => {
              const color = colors[idx] || colors[idx % colors.length];
              return (
                <React.Fragment key={`concurrent-${bench.index}`}>
                  <Bar dataKey={`input_${idx}`} fill={color.input} radius={[4, 4, 0, 0]} name={`benchmark ${idx + 1} input token/s`} />
                  <Bar dataKey={`output_${idx}`} fill={color.output} radius={[4, 4, 0, 0]} name={`benchmark ${idx + 1} output token/s`} />
                </React.Fragment>
              );
            })}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

import React from 'react';