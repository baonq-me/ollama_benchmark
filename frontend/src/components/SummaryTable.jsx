export default function SummaryTable({ benchmarks }) {
  if (!benchmarks || benchmarks.length === 0) return null;

  const colors = [
    'text-cyan-600',
    'text-purple-600',
    'text-orange-600',
    'text-red-600',
    'text-green-600',
    'text-blue-600',
    'text-pink-600',
    'text-indigo-600',
  ];

  const formatNumber = (num) => {
    if (num === undefined || num === null) return '—';
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toFixed(1);
  };

  // Collect all unique prompt sizes across all benchmarks
  const allPromptSizes = Array.from(new Set(
    benchmarks.flatMap(b => (b.results || []).map(r => r.prompt_size))
  )).sort((a, b) => a - b);

  return (
    <div className="mb-8">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">📊 Summary Table (Median Values)</h2>
      <div className="overflow-x-auto rounded-xl border border-gray-200 shadow-sm">
        <table className="w-full text-sm text-left">
          <thead className="bg-gray-100 text-gray-500 text-xs tracking-wider">
            <tr>
              <th className="px-4 py-3" rowSpan="2">prompt size</th>
              {benchmarks.map((bench, idx) => (
                <th key={bench.index} className={`px-4 py-3 ${colors[idx]}`} colSpan="4">
                  Benchmark {bench.index + 1}
                </th>
              ))}
            </tr>
            <tr>
              {benchmarks.map((bench, idx) => (
                <React.Fragment key={bench.index}>
                  <th className={`px-4 py-3 ${colors[idx]}`}>TTFT (ms)</th>
                  <th className={`px-4 py-3 ${colors[idx]}`}>Input token/s</th>
                  <th className={`px-4 py-3 ${colors[idx]}`}>Output token/s</th>
                  <th className={`px-4 py-3 ${colors[idx]}`}>Latency (ms)</th>
                </React.Fragment>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {allPromptSizes.map((promptSize, i) => {
              const rowClassName = i % 2 === 0 ? 'bg-white' : 'bg-gray-50';
              return (
                <tr key={promptSize} className={rowClassName}>
                  <td className="px-4 py-3 font-mono text-gray-600 font-medium">{promptSize}</td>
                  {benchmarks.map((bench, idx) => {
                    const entry = (bench.results || []).find(r => r.prompt_size === promptSize);
                    return entry ? (
                      <React.Fragment key={bench.index}>
                        <td className={`px-4 py-3 ${colors[idx]}`}>{formatNumber(entry.stats.ttft_ms.median)}</td>
                        <td className={`px-4 py-3 ${colors[idx]}`}>{formatNumber(entry.stats.input_tps.median)}</td>
                        <td className={`px-4 py-3 ${colors[idx]}`}>{formatNumber(entry.stats.output_tps.median)}</td>
                        <td className={`px-4 py-3 ${colors[idx]}`}>{formatNumber(entry.stats.total_latency_ms.median)}</td>
                      </React.Fragment>
                    ) : (
                      <React.Fragment key={bench.index}>
                        <td colSpan="4" className={`px-4 py-3 ${colors[idx]} text-gray-400`}>— N/A —</td>
                      </React.Fragment>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

import React from 'react';
