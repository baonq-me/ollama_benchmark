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

function prepareConcurrentData(results, suffix) {
  if (!results) return [];
  return results.map((entry) => ({
    promptSize: entry.prompt_size,
    ['Input t/s' + suffix]: entry.stats.input_tps.median,
    ['Output t/s' + suffix]: entry.stats.output_tps.median,
  }));
}

export default function ConcurrentCharts({ metadata1, results1, metadata2, results2 }) {
  const hasConcurrent1 = metadata1 && metadata1.concurrent > 1 && results1 && results1.length > 0;
  const hasConcurrent2 = metadata2 && metadata2.concurrent > 1 && results2 && results2.length > 0;

  if (!hasConcurrent1 && !hasConcurrent2) return null;

  const data1 = prepareConcurrentData(results1, ' (Bench 1)');
  const data2 = prepareConcurrentData(results2, ' (Bench 2)');

  const mergeChartData = (dataA, dataB) => {
    const merged = new Map();
    [...dataA, ...dataB].forEach(item => {
      const existing = merged.get(item.promptSize) || { promptSize: item.promptSize };
      merged.set(item.promptSize, { ...existing, ...item });
    });
    return Array.from(merged.values()).sort((a, b) => a.promptSize - b.promptSize);
  };

  const mergedData = mergeChartData(data1, data2);

  const concurrentValue1 = metadata1?.concurrent || 1;
  const concurrentValue2 = metadata2?.concurrent || 1;

  let title = '⚡ Concurrent Performance';
  if (hasConcurrent1 && hasConcurrent2) {
    title += ' (Bench 1: ' + concurrentValue1 + ', Bench 2: ' + concurrentValue2 + ')';
  } else if (hasConcurrent1) {
    title += ' (concurrency=' + concurrentValue1 + ')';
  } else {
    title += ' (concurrency=' + concurrentValue2 + ')';
  }

  return (
    <div className="mb-8">
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
        <p className="text-gray-500 text-sm mb-4">
          Throughput under simultaneous requests. Higher is better.
        </p>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={mergedData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="promptSize"
              stroke="#6b7280"
              tick={{ fontSize: 12 }}
              label={{ value: 'Prompt Size (tokens)', position: 'insideBottom', offset: -5, fill: '#6b7280' }}
            />
            <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
              labelStyle={{ color: '#374151' }}
            />
            <Legend />
            {hasConcurrent1 && (
              <Bar dataKey="Input t/s (Bench 1)" fill="#0891b2" radius={[4, 4, 0, 0]} />
            )}
            {hasConcurrent1 && (
              <Bar dataKey="Output t/s (Bench 1)" fill="#7c3aed" radius={[4, 4, 0, 0]} />
            )}
            {hasConcurrent2 && (
              <Bar dataKey="Input t/s (Bench 2)" fill="#d97706" radius={[4, 4, 0, 0]} />
            )}
            {hasConcurrent2 && (
              <Bar dataKey="Output t/s (Bench 2)" fill="#ec4899" radius={[4, 4, 0, 0]} />
            )}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}