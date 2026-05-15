# 🚀 Ollama Benchmark

A Python CLI tool + React dashboard for benchmarking Ollama LLM performance. Measures 5 metrics: input/output throughput, TTFT, total latency, context scaling (64–8192 tokens), P95/P99 latency, and concurrent performance. Uses streaming `/api/chat` endpoint with SSE parsing. Outputs JSON + CLI summary table. React/Vite/Tailwind/Recharts frontend reads the JSON and renders interactive charts.

## Features

- **5 Key Metrics**: Input/output throughput, TTFT, total latency, context scaling, P95/P99 latency, concurrent performance
- **Streaming API**: Uses Ollama's streaming `/api/chat` endpoint for accurate real-time measurements
- **Retry Logic**: Exponential backoff retry for network failures (configurable)
- **JSON Output**: Clean, structured JSON for easy integration with other tools
- **React Dashboard**: Modern dark-themed dashboard with interactive Recharts charts

## Quick Start

### 1. Setup Python Environment (Required)

**Important**: All Python commands must be run inside the virtual environment (venv).

```bash
# Create and activate the virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r ollama_benchmark/requirements.txt
```

### 2. Run a Benchmark

**Make sure venv is activated** (you should see `(venv)` in your terminal prompt):

```bash
# Basic usage (requires Ollama running locally)
python -m ollama_benchmark.cli --model llama3.2

# Custom endpoint and settings
python -m ollama_benchmark.cli \
  --model qwen3.5:2b \
  --endpoint http://192.168.1.100:11434 \
  --prompt-sizes 64,1024,8192 \
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

Then open http://localhost:5173 and drag & drop your `results_{model}_{timestamp}.json` file. The output filename includes a timestamp (format: `YYYYMMDD_HHMMSS`) to ensure uniqueness across runs.

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--endpoint` | `http://127.0.0.1:11434` | Ollama server URL (default) |
| `--model` | `qwen3.5:2b` | Ollama model name (e.g. llama3.2, codellama:7b) |
| `--output` | `frontend/public/results_{model}_{timestamp}.json` | Output JSON file path (auto-generated with timestamp if not specified) |
| `--prompt-sizes` | `64,1024,8192` | Comma-separated prompt token counts (default: 3 sizes) |
| `--gen-tokens` | `512` | Target number of output tokens to generate |
| `--iterations` | `3` | Number of benchmark runs per prompt size |
| `--concurrent` | `1` | Number of simultaneous requests for concurrent testing |
| `--retries` | `3` | Max retry attempts on network failure |
| `--retry-delay` | `2.0` | Base delay between retries in seconds (exponential backoff) |

## Key Technical Details

### Python CLI (`cli.py`)

- **Entry**: `python -m ollama_benchmark.cli --model <name>`
- **Default endpoint**: `http://127.0.0.1:11434`
- **Default prompt sizes**: `64,1024,8192` (3 sizes)
- **Default gen_tokens**: 512, **iterations**: 3, **concurrent**: 1, **retries**: 3, **retry_delay**: 2.0s
- **Output**: `results_{model}_{timestamp}.json` (auto-generated with timestamp, or custom path via `--output`)
- **Summary table**: Includes model name in title, displays median metrics per prompt size
- **Error handling**: Handles errors gracefully (OOM, connection refused, model not found)

### Benchmark Engine (`benchmark.py`)

- **API**: `POST /api/chat` with `stream: true`, `options: {num_predict: gen_tokens}`
- **SSE Parsing**: Iterates `response.iter_lines()`, parses `data: {...}` chunks
- **Timestamps**: `request_start`, `first_token_time`, `last_token_time` via `time.perf_counter()`
- **Metrics computed**:
  - **TTFT (ms)** = `(first_token_time - request_start) * 1000`
  - **Input tps** = `prompt_tokens / (prompt_eval_duration_ns / 1e9)` — from final chunk
  - **Output tps** = `output_tokens / (eval_duration_ns / 1e9)` — from final chunk
  - **Total latency (ms)** = `(last_token_time - request_start) * 1000`
- **Fallback**: If server doesn't report durations, uses wall-clock times
- **Retry**: `_retry_request()` with exponential backoff (`delay * 2^(attempt-1)`), catches ConnectionError, Timeout, ChunkedEncodingError, HTTP 5xx
- **Statistics**: `numpy` median, P95, P99, min, max per metric per prompt size
- **Concurrent**: `ThreadPoolExecutor` with `max_workers=concurrent`
- **Prompt generation**: Coding-assistant system prompt + padded template, ~1.3 tokens/word heuristic

### JSON Output Schema

```json
{
  "metadata": { "model", "endpoint", "gen_tokens", "iterations", "concurrent", "retries", "retry_delay", "timestamp" },
  "results": [
    {
      "prompt_size": 128,
      "runs": [
        { "ttft_ms", "input_tps", "output_tps", "total_latency_ms", "prompt_tokens", "output_tokens", "retries_used" }
      ],
      "stats": {
        "ttft_ms": { "median", "p95", "p99", "min", "max" },
        "input_tps": { ... },
        "output_tps": { ... },
        "total_latency_ms": { ... }
      }
    }
  ]
}
```

### Frontend Dashboard

- **Stack**: React 19, Vite 8, Tailwind CSS v4, Recharts 3
- **Theme**: Dark (gray-950 background), cyan/purple gradient header
- **No backend**: Static SPA, reads JSON via FileReader API (drag & drop or file picker)
- **Charts**: All use Recharts with ResponsiveContainer, dark tooltips, P95/P99 dashed lines
- **Conditional**: ConcurrentCharts only renders if concurrent > 1
- **Sample data**: `frontend/public/sample-results.json` for testing without running benchmarks

## Metrics Explained

| Metric | Description |
|--------|-------------|
| **Input Throughput** (tokens/sec) | How fast the model processes the prompt (prefill phase) |
| **Output Throughput** (tokens/sec) | How fast the model generates tokens (decode phase) |
| **TTFT** (ms) | Time to First Token — latency from request to first output |
| **Total Latency** (ms) | Wall-clock time for the entire generation |
| **Context Scaling** | How throughput degrades as prompt length increases |
| **P95/P99 Latency** | Tail latency percentiles across multiple runs |
| **Concurrent Performance** | Throughput under simultaneous request load |

## Requirements

### Python Environment
- Python 3.10+ (must be used with a virtual environment - venv)
- Dependencies: requests, numpy, rich (installed via `pip install -r ollama_benchmark/requirements.txt`)

### Frontend
- Node.js 18+ (for React dashboard)

### Backend
- Ollama server running (local or remote)

## Project Structure

```
ollama_benchmark/
├── ollama_benchmark/          # Python package
│   ├── __init__.py            # Package marker, version 0.1.0
│   ├── cli.py                 # argparse CLI entry point
│   ├── benchmark.py           # Core benchmark engine
│   └── requirements.txt       # requests, numpy, rich
├── frontend/                  # React + Vite dashboard
│   ├── src/
│   │   ├── App.jsx            # Main layout, header, file loader integration
│   │   ├── index.css          # Tailwind v4 import + body styles
│   │   ├── main.jsx           # Vite React entry
│   │   └── components/
│   │       ├── FileLoader.jsx       # Drag & drop JSON upload
│   │       ├── SummaryTable.jsx     # Median metrics table
│   │       ├── ThroughputCharts.jsx # Input/output t/s line charts (P95/P99 bands)
│   │       ├── LatencyCharts.jsx    # TTFT & total latency line charts
│   │       └── ConcurrentCharts.jsx # Concurrent perf bar chart
│   ├── public/sample-results.json   # Sample data for testing
│   ├── vite.config.js               # Vite + React + Tailwind v4 plugin
│   └── package.json                 # react 19, recharts 3, tailwind 4, vite 8
├── venv/                      # Python virtual environment (git-ignored)
└── README.md                  # Full usage docs
```

## Known Issues / Gotchas

- `retries_used` in run results is always 0 — the retry counter isn't propagated from `_retry_request()` to the result dict. The retry attempts are only visible in console logs.
- Prompt token counts are approximate (word-count heuristic, ~1.3 tokens/word). Actual token counts depend on the model's tokenizer.
- The `statistics` import in benchmark.py is unused (numpy is used instead).
- No GPU monitoring — explicitly excluded per user request.
- Frontend has a chunk size warning on build (Recharts is ~570KB). Could be code-split later.
- **venv required**: Python commands must be run inside the virtual environment. Check that `(venv)` appears in your terminal prompt before running benchmarks.

## License

MIT