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

function prepareChartData(results, metricKey, label, suffix) {
  if (!results) return [];
  return results.map((entry) => ({
    promptSize: entry.prompt_size,
    [label + suffix]: entry.stats[metricKey].median,
    [label + suffix + ' P95']: entry.stats[metricKey].p95,
    [label + suffix + ' P99']: entry.stats[metricKey].p99,
  }));
}

export default function LatencyCharts({ results1, results2 }) {
  if (!results1 && !results2) return null;

  const ttftData1 = prepareChartData(results1, 'ttft_ms', 'TTFT (ms)', ' (Bench 1)');
  const latencyData1 = prepareChartData(results1, 'total_latency_ms', 'Total Latency (ms)', ' (Bench 1)');

  const ttftData2 = prepareChartData(results2, 'ttft_ms', 'TTFT (ms)', ' (Bench 2)');
  const latencyData2 = prepareChartData(results2, 'total_latency_ms', 'Total Latency (ms)', ' (Bench 2)');

  const mergeChartData = (dataA, dataB) => {
    const merged = new Map();
    [...dataA, ...dataB].forEach(item => {
      const existing = merged.get(item.promptSize) || { promptSize: item.promptSize };
      merged.set(item.promptSize, { ...existing, ...item });
    });
    return Array.from(merged.values()).sort((a, b) => a.promptSize - b.promptSize);
  };

  const mergedTtftData = mergeChartData(ttftData1, ttftData2);
  const mergedLatencyData = mergeChartData(latencyData1, latencyData2);

  const renderLines = (dataKey, color) => [
    <Line
      key={dataKey}
      type="monotone"
      dataKey={dataKey}
      stroke={color}
      strokeWidth={2}
      dot={{ fill: color, r: 4 }}
      name={dataKey}
    />,
    <Line
      key={dataKey + ' P95'}
      type="monotone"
      dataKey={dataKey + ' P95'}
      stroke={color}
      strokeWidth={1}
      strokeDasharray="5 5"
      dot={false}
      opacity={0.5}
    />,
    <Line
      key={dataKey + ' P99'}
      type="monotone"
      dataKey={dataKey + ' P99'}
      stroke={color}
      strokeWidth={1}
      strokeDasharray="2 2"
      dot={false}
      opacity={0.3}
    />,
  ];

  const chartConfig = (title, data, unit) => (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="promptSize"
            stroke="#6b7280"
            tick={{ fontSize: 12 }}
            label={{ value: 'Prompt Size (tokens)', position: 'insideBottom', offset: -5, fill: '#6b7280' }}
          />
          <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} unit={unit} />
          <Tooltip
            contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
            labelStyle={{ color: '#374151' }}
          />
          <Legend />
          {results1 && renderLines('TTFT (ms) (Bench 1)', '#d97706')}
          {results2 && renderLines('TTFT (ms) (Bench 2)', '#059669')}
          {results1 && renderLines('Total Latency (ms) (Bench 1)', '#dc2626')}
          {results2 && renderLines('Total Latency (ms) (Bench 2)', '#7c3aed')}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      {results1 && chartConfig('Time to First Token (TTFT)', mergedTtftData, ' ms')}
      {results2 && chartConfig('Total Generation Latency', mergedLatencyData, ' ms')}
    </div>
  );
}