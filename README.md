# 🚀 Ollama Benchmark

A comprehensive benchmark suite for measuring Ollama LLM performance. Tests throughput, latency, context scaling, KV cache memory, and concurrent performance. Outputs JSON results and provides a beautiful React dashboard for visualization.

## Features

- **7 Key Metrics**: Input/output throughput, TTFT, total latency, context scaling, P95/P99 latency, KV cache memory, concurrent performance
- **Streaming API**: Uses Ollama's streaming `/api/chat` endpoint for accurate real-time measurements
- **Retry Logic**: Exponential backoff retry for network failures (configurable)
- **JSON Output**: Clean, structured JSON for easy integration with other tools
- **React Dashboard**: Modern dark-themed dashboard with interactive Recharts charts

## Quick Start

### 1. Setup Python Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r ollama_benchmark/requirements.txt
```

### 2. Run a Benchmark

```bash
# Basic usage (requires Ollama running locally)
python -m ollama_benchmark.cli --model llama3.2

# Custom endpoint and settings
python -m ollama_benchmark.cli \
  --model codellama:7b \
  --endpoint http://192.168.1.100:11434 \
  --prompt-sizes 256,512,1024,2048 \
  --gen-tokens 256 \
  --iterations 3

# Concurrent testing
python -m ollama_benchmark.cli --model mistral --concurrent 4
```

### 3. View Results

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173 and drag & drop your `results.json` file.

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--endpoint` | `http://127.0.0.1:11434` | Ollama server URL |
| `--model` | *(required)* | Ollama model name |
| `--output` | `results.json` | Output JSON file path |
| `--prompt-sizes` | `64,256,512,1024,2048,4096,8192,16384,32768` | Comma-separated prompt token counts |
| `--gen-tokens` | `512` | Target output tokens to generate |
| `--iterations` | `5` | Runs per prompt size |
| `--concurrent` | `1` | Simultaneous requests for concurrent testing |
| `--retries` | `3` | Max retry attempts on network failure |
| `--retry-delay` | `2.0` | Base delay between retries (exponential backoff) |

## JSON Output Schema

```json
{
  "metadata": {
    "model": "llama3.2",
    "endpoint": "http://127.0.0.1:11434",
    "gen_tokens": 512,
    "iterations": 5,
    "concurrent": 1,
    "retries": 3,
    "retry_delay": 2.0,
    "timestamp": "2026-05-14T10:30:00"
  },
  "results": [
    {
      "prompt_size": 128,
      "kv_cache": { "raw": { ... } },
      "runs": [
        {
          "ttft_ms": 45.2,
          "input_tps": 1234.5,
          "output_tps": 56.7,
          "total_latency_ms": 9123.4,
          "prompt_tokens": 128,
          "output_tokens": 512,
          "retries_used": 0
        }
      ],
      "stats": {
        "ttft_ms": { "median": 44.1, "p95": 48.3, "p99": 49.1, "min": 42.0, "max": 50.2 },
        "input_tps": { ... },
        "output_tps": { ... },
        "total_latency_ms": { ... }
      }
    }
  ]
}
```

## Metrics Explained

| Metric | Description |
|--------|-------------|
| **Input Throughput** (tokens/sec) | How fast the model processes the prompt (prefill phase) |
| **Output Throughput** (tokens/sec) | How fast the model generates tokens (decode phase) |
| **TTFT** (ms) | Time to First Token — latency from request to first output |
| **Total Latency** (ms) | Wall-clock time for the entire generation |
| **Context Scaling** | How throughput degrades as prompt length increases |
| **P95/P99 Latency** | Tail latency percentiles across multiple runs |
| **KV Cache Memory** | Memory used by the key-value cache at different context lengths |
| **Concurrent Performance** | Throughput under simultaneous request load |

## Requirements

- Python 3.10+
- Node.js 18+ (for frontend)
- Ollama server running (local or remote)

## Project Structure

```
ollama_benchmark/
├── ollama_benchmark/       # Python package
│   ├── __init__.py
│   ├── cli.py              # CLI entry point
│   ├── benchmark.py        # Benchmark engine
│   └── requirements.txt    # Python dependencies
├── frontend/               # React + Vite dashboard
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/     # Dashboard components
│   └── package.json
├── venv/                   # Python virtual environment
└── README.md
```

## License

MIT