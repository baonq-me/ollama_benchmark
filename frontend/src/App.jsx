import { useState, useMemo } from 'react';
import FileLoader from './components/FileLoader';
import SummaryTable from './components/SummaryTable';
import ThroughputCharts from './components/ThroughputCharts';
import LatencyCharts from './components/LatencyCharts';
import ConcurrentCharts from './components/ConcurrentCharts';

function App() {
  const [benchmarks, setBenchmarks] = useState([]);

  const hasData = benchmarks.some(b => b);

  // Parse benchmarks into structured data
  const parsedBenchmarks = useMemo(() => {
    return benchmarks.map((data, index) => ({
      index,
      data,
      metadata: data?.metadata,
      results: data?.results,
    })).filter(b => b.data);
  }, [benchmarks]);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800">
      <header className="border-b border-gray-200 bg-white/80 backdrop-blur shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-500 to-purple-500 bg-clip-text text-transparent">
            🚀 Ollama Benchmark Dashboard
          </h1>
          {parsedBenchmarks.map((bench, idx) => (
            <div key={bench.index} className="mt-3 flex flex-wrap gap-4 text-sm text-gray-600">
              <h2 className={`text-xl font-semibold w-full ${idx === 0 ? 'text-cyan-600' : idx === 1 ? 'text-purple-600' : idx === 2 ? 'text-orange-600' : idx === 3 ? 'text-red-600' : 'text-green-600'}`}>
                Benchmark {bench.index + 1}
              </h2>
              {bench.metadata && (
                <>
                  <span className="flex items-center gap-1">
                    <span className="text-gray-400">Model:</span>
                    <span className={`font-mono font-medium ${idx === 0 ? 'text-cyan-600' : idx === 1 ? 'text-purple-600' : idx === 2 ? 'text-orange-600' : idx === 3 ? 'text-red-600' : 'text-green-600'}`}>
                      {bench.metadata.model}
                    </span>
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="text-gray-400">Gen tokens:</span>
                    <span className="text-gray-700">{bench.metadata.gen_tokens}</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="text-gray-400">Iterations:</span>
                    <span className="text-gray-700">{bench.metadata.iterations}</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="text-gray-400">Concurrent:</span>
                    <span className="text-gray-700">{bench.metadata.concurrent}</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="text-gray-400">Retries:</span>
                    <span className="text-gray-700">{bench.metadata.retries}</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="text-gray-400">Timestamp:</span>
                    <span className="text-gray-700">{bench.metadata.timestamp}</span>
                  </span>
                </>
              )}
            </div>
          ))}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {!hasData ? (
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8">
              <p className="text-gray-500 text-lg">
                Load benchmark result files to visualize and compare performance metrics.
              </p>
            </div>
            <FileLoader onDataLoaded={setBenchmarks} />
            <div className="mt-8 p-6 bg-white rounded-xl border border-gray-200 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">📋 How to generate results:</h3>
              <div className="bg-gray-100 rounded-lg p-4 font-mono text-sm text-gray-700 overflow-x-auto">
                <code>
                  cd ollama_benchmark<br />
                  source venv/bin/activate<br />
                  python -m ollama_benchmark.cli --model llama3.2
                </code>
              </div>
              <p className="text-gray-500 text-sm mt-3">
                This will create <code className="text-cyan-600 font-medium">results.json</code> in the <code className="text-cyan-600 font-medium">frontend/public</code> folder.
                Then drag & drop it here.
              </p>
            </div>
          </div>
        ) : (
          <>
            <SummaryTable benchmarks={parsedBenchmarks} />
            <ThroughputCharts benchmarks={parsedBenchmarks} />
            <LatencyCharts benchmarks={parsedBenchmarks} />
            <ConcurrentCharts benchmarks={parsedBenchmarks} />
          </>
        )}
      </main>

      <footer className="border-t border-gray-200 mt-12 py-6 text-center text-gray-400 text-sm">
        Ollama Benchmark Tool — Built with React + Vite + Tailwind CSS + Recharts
      </footer>
    </div>
  );
}

export default App;