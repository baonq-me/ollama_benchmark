export default function SummaryTable({ results1, results2 }) {
  if (!results1 && !results2) return null;

  const formatKvCache = (kv) => {
    if (!kv) return '—';
    const used = kv.kv_cache_used ?? kv.memory_used;
    if (used !== undefined) {
      return typeof used === 'number' ? `${(used / 1024 / 1024).toFixed(0)} MB` : String(used);
    }
    return '—';
  };

  const commonPromptSizes = Array.from(new Set([
    ...(results1 || []).map(r => r.prompt_size),
    ...(results2 || []).map(r => r.prompt_size)
  ])).sort((a, b) => a - b);

  return (
    <div className="mb-8">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">📊 Summary Table (Median Values)</h2>
      <div className="overflow-x-auto rounded-xl border border-gray-200 shadow-sm">
        <table className="w-full text-sm text-left">
          <thead className="bg-gray-100 text-gray-500 uppercase text-xs tracking-wider">
            <tr>
              <th className="px-4 py-3" rowSpan="2">Prompt Size</th>
              {results1 && <th className="px-4 py-3 text-cyan-600" colSpan="5">Benchmark 1</th>}
              {results2 && <th className="px-4 py-3 text-purple-600" colSpan="5">Benchmark 2</th>}
            </tr>
            <tr>
              {results1 && (<>
                <th className="px-4 py-3">TTFT (ms)</th>
                <th className="px-4 py-3">Input t/s</th>
                <th className="px-4 py-3">Output t/s</th>
                <th className="px-4 py-3">Total Lat (ms)</th>
                <th className="px-4 py-3">KV Cache</th>
              </>)}
              {results2 && (<>
                <th className="px-4 py-3">TTFT (ms)</th>
                <th className="px-4 py-3">Input t/s</th>
                <th className="px-4 py-3">Output t/s</th>
                <th className="px-4 py-3">Total Lat (ms)</th>
                <th className="px-4 py-3">KV Cache</th>
              </>)}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {commonPromptSizes.map((promptSize, i) => {
              const entry1 = (results1 || []).find(r => r.prompt_size === promptSize);
              const entry2 = (results2 || []).find(r => r.prompt_size === promptSize);
              const rowClassName = i % 2 === 0 ? 'bg-white' : 'bg-gray-50';

              return (
                <tr key={promptSize} className={rowClassName}>
                  <td className="px-4 py-3 font-mono text-cyan-600 font-medium">{promptSize}</td>
                  {entry1 ? (
                    <>
                      <td className="px-4 py-3 text-cyan-600">{entry1.stats.ttft_ms.median.toFixed(1)}</td>
                      <td className="px-4 py-3 text-cyan-600">{entry1.stats.input_tps.median.toFixed(0)}</td>
                      <td className="px-4 py-3 text-cyan-600">{entry1.stats.output_tps.median.toFixed(1)}</td>
                      <td className="px-4 py-3 text-cyan-600">{entry1.stats.total_latency_ms.median.toFixed(0)}</td>
                      <td className="px-4 py-3 text-cyan-600">{formatKvCache(entry1.kv_cache?.raw)}</td>
                    </>
                  ) : (
                    results1 && <td colSpan="5" className="px-4 py-3 text-gray-400">— N/A —</td>
                  )}
                  {entry2 ? (
                    <>
                      <td className="px-4 py-3 text-purple-600">{entry2.stats.ttft_ms.median.toFixed(1)}</td>
                      <td className="px-4 py-3 text-purple-600">{entry2.stats.input_tps.median.toFixed(0)}</td>
                      <td className="px-4 py-3 text-purple-600">{entry2.stats.output_tps.median.toFixed(1)}</td>
                      <td className="px-4 py-3 text-purple-600">{entry2.stats.total_latency_ms.median.toFixed(0)}</td>
                      <td className="px-4 py-3 text-purple-600">{formatKvCache(entry2.kv_cache?.raw)}</td>
                    </>
                  ) : (
                    results2 && <td colSpan="5" className="px-4 py-3 text-gray-400">— N/A —</td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}