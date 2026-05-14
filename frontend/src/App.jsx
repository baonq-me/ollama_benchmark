import { useState } from 'react';
import FileLoader from './components/FileLoader';
import SummaryTable from './components/SummaryTable';
import ThroughputCharts from './components/ThroughputCharts';
import LatencyCharts from './components/LatencyCharts';
import ResourceCharts from './components/ResourceCharts';
import ConcurrentCharts from './components/ConcurrentCharts';

function App() {
  const [benchmarkData, setBenchmarkData] = useState([null, null]);

  const data1 = benchmarkData[0];
  const data2 = benchmarkData[1];

  const metadata1 = data1?.metadata;
  const results1 = data1?.results;
  const metadata2 = data2?.metadata;
  const results2 = data2?.results;

  const hasData = data1 || data2;

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800">
      <header className="border-b border-gray-200 bg-white/80 backdrop-blur shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-500 to-purple-500 bg-clip-text text-transparent">
            🚀 Ollama Benchmark Dashboard
          </h1>
          {metadata1 && (
            <div className="mt-3 flex flex-wrap gap-4 text-sm text-gray-600">
              <h2 className="text-xl font-semibold text-cyan-600 w-full">Benchmark 1</h2>
              <span className="flex items-center gap-1">
                <span className="text-gray-400">Model:</span>
                <span className="text-cyan-600 font-mono font-medium">{metadata1.model}</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="text-gray-400">Endpoint:</span>
                <span className="text-purple-600 font-mono font-medium">{metadata1.endpoint}</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="text-gray-400">Gen tokens:</span>
                <span className="text-gray-700">{metadata1.gen_tokens}</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="text-gray-400">Iterations:</span>
                <span className="text-gray-700">{metadata1.iterations}</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="text-gray-400">Concurrent:</span>
                <span className="text-gray-700">{metadata1.concurrent}</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="text-gray-400">Retries:</span>
                <span className="text-gray-700">{metadata1.retries}</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="text-gray-400">Timestamp:</span>
                <span className="text-gray-700">{metadata1.timestamp}</span>
              </span>
            </div>
          )}
           {metadata2 && (
            <div className="mt-3 flex flex-wrap gap-4 text-sm text-gray-600">
              <h2 className="text-xl font-semibold text-purple-600 w-full">Benchmark 2</h2>
              <span className="flex items-center gap-1">
                <span className="text-gray-400">Model:</span>
                <span className="text-purple-600 font-mono font-medium">{metadata2.model}</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="text-gray-400">Endpoint:</span>
                <span className="text-purple-600 font-mono font-medium">{metadata2.endpoint}</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="text-gray-400">Gen tokens:</span>
                <span className="text-gray-700">{metadata2.gen_tokens}</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="text-gray-400">Iterations:</span>
                <span className="text-gray-700">{metadata2.iterations}</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="text-gray-400">Concurrent:</span>
                <span className="text-gray-700">{metadata2.concurrent}</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="text-gray-400">Retries:</span>
                <span className="text-gray-700">{metadata2.retries}</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="text-gray-400">Timestamp:</span>
                <span className="text-gray-700">{metadata2.timestamp}</span>
              </span>
            </div>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {!hasData ? (
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8">
              <p className="text-gray-500 text-lg">
                Load one or two benchmark results files to visualize performance metrics.
              </p>
            </div>
            <FileLoader onDataLoaded={setBenchmarkData} />
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
            <SummaryTable results1={results1} results2={results2} />
            <ThroughputCharts results1={results1} results2={results2} />
            <LatencyCharts results1={results1} results2={results2} />
            <ResourceCharts results1={results1} results2={results2} />
            <ConcurrentCharts metadata1={metadata1} results1={results1} metadata2={metadata2} results2={results2} />
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