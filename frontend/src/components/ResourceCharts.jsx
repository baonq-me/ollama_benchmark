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

function prepareKvCacheData(results, suffix) {
  if (!results) return [];
  return results
    .filter((e) => e.kv_cache?.raw)
    .map((entry) => {
      const kv = entry.kv_cache.raw;
      const used = kv.kv_cache_used ?? kv.memory_used ?? 0;
      const total = kv.kv_cache_total ?? kv.memory_total ?? 1;
      return {
        promptSize: entry.prompt_size,
        ['usedMB' + suffix]: typeof used === 'number' ? +(used / 1024 / 1024).toFixed(1) : 0,
        ['totalMB' + suffix]: typeof total === 'number' ? +(total / 1024 / 1024).toFixed(1) : 0,
      };
    });
}

export default function ResourceCharts({ results1, results2 }) {
  if (!results1 && !results2) return null;

  const data1 = prepareKvCacheData(results1, ' (Bench 1)');
  const data2 = prepareKvCacheData(results2, ' (Bench 2)');

  const hasKvCache1 = results1?.some((e) => e.kv_cache?.raw);
  const hasKvCache2 = results2?.some((e) => e.kv_cache?.raw);

  if (!hasKvCache1 && !hasKvCache2) return null;

  const mergeChartData = (dataA, dataB) => {
    const merged = new Map();
    [...dataA, ...dataB].forEach(item => {
      const existing = merged.get(item.promptSize) || { promptSize: item.promptSize };
      merged.set(item.promptSize, { ...existing, ...item });
    });
    return Array.from(merged.values()).sort((a, b) => a.promptSize - b.promptSize);
  };

  const mergedData = mergeChartData(data1, data2);

  if (mergedData.length === 0) return null;

  return (
    <div className="mb-8">
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">🗄️ KV Cache Memory Usage</h3>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={mergedData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="promptSize"
              stroke="#6b7280"
              tick={{ fontSize: 12 }}
              label={{ value: 'Prompt Size (tokens)', position: 'insideBottom', offset: -5, fill: '#6b7280' }}
            />
            <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} unit=" MB" />
            <Tooltip
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
              labelStyle={{ color: '#374151' }}
            />
            <Legend />
            {hasKvCache1 && (
              <Line
                type="monotone"
                dataKey="usedMB (Bench 1)"
                stroke="#059669"
                strokeWidth={2}
                dot={{ fill: '#059669', r: 4 }}
                name="Used (MB) (Bench 1)"
              />
            )}
            {hasKvCache1 && (
              <Line
                type="monotone"
                dataKey="totalMB (Bench 1)"
                stroke="#9ca3af"
                strokeWidth={1}
                strokeDasharray="5 5"
                dot={false}
                name="Total (MB) (Bench 1)"
              />
            )}
            {hasKvCache2 && (
              <Line
                type="monotone"
                dataKey="usedMB (Bench 2)"
                stroke="#d97706"
                strokeWidth={2}
                dot={{ fill: '#d97706', r: 4 }}
                name="Used (MB) (Bench 2)"
              />
            )}
            {hasKvCache2 && (
              <Line
                type="monotone"
                dataKey="totalMB (Bench 2)"
                stroke="#6b7280"
                strokeWidth={1}
                strokeDasharray="5 5"
                dot={false}
                name="Total (MB) (Bench 2)"
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}