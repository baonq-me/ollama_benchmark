# Ollama Benchmark Project — Knowledge Base

## Overview
A Python CLI tool + React dashboard for benchmarking Ollama LLM performance. Measures 7 metrics: input/output throughput, TTFT, total latency, context scaling (64–32768 tokens), P95/P99 latency, KV cache memory, and concurrent performance. Uses streaming `/api/chat` endpoint with SSE parsing. Outputs JSON + CLI summary table. React/Vite/Tailwind/Recharts frontend reads the JSON and renders interactive charts.

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
│   │       ├── ResourceCharts.jsx   # KV cache memory chart
│   │       └── ConcurrentCharts.jsx # Concurrent perf bar chart
│   ├── public/sample-results.json   # Sample data for testing
│   ├── vite.config.js               # Vite + React + Tailwind v4 plugin
│   └── package.json                 # react 19, recharts 3, tailwind 4, vite 8
├── venv/                      # Python virtual environment (git-ignored)
└── README.md                  # Full usage docs
```

## Key Technical Details

### Python CLI (`cli.py`)
- Entry: `python -m ollama_benchmark.cli --model <name>`
- Default endpoint: `http://127.0.0.1:11434`
- Default prompt sizes: `64,256,512,1024,2048,4096,8192,16384,32768` (9 sizes)
- Default gen_tokens: 512, iterations: 5, concurrent: 1, retries: 3, retry_delay: 2.0s
- Output: `results.json` (configurable via `--output`)
- Prints a rich CLI table with median metrics per prompt size
- Handles errors gracefully (OOM, connection refused, model not found)

### Benchmark Engine (`benchmark.py`)
- **API**: `POST /api/chat` with `stream: true`, `options: {num_predict: gen_tokens}`
- **SSE Parsing**: Iterates `response.iter_lines()`, parses `data: {...}` chunks
- **Timestamps**: `request_start`, `first_token_time`, `last_token_time` via `time.perf_counter()`
- **Metrics computed**:
  - TTFT (ms) = `(first_token_time - request_start) * 1000`
  - Input tps = `prompt_tokens / (prompt_eval_duration_ns / 1e9)` — from final chunk
  - Output tps = `output_tokens / (eval_duration_ns / 1e9)` — from final chunk
  - Total latency (ms) = `(last_token_time - request_start) * 1000`
- **Fallback**: If server doesn't report durations, uses wall-clock times
- **Retry**: `_retry_request()` with exponential backoff (`delay * 2^(attempt-1)`), catches ConnectionError, Timeout, ChunkedEncodingError, HTTP 5xx
- **KV Cache**: `get_kv_cache_stats()` calls `GET /api/stats`, returns raw dict
- **Concurrent**: `ThreadPoolExecutor` with `max_workers=concurrent`
- **Statistics**: `numpy` median, P95, P99, min, max per metric per prompt size
- **Prompt generation**: Coding-assistant system prompt + padded template, ~1.3 tokens/word heuristic

### JSON Output Schema
```json
{
  "metadata": { "model", "endpoint", "gen_tokens", "iterations", "concurrent", "retries", "retry_delay", "timestamp" },
  "results": [
    {
      "prompt_size": 128,
      "kv_cache": { "raw": { ... } },
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
- **Conditional**: ResourceCharts only renders if kv_cache data present; ConcurrentCharts only if concurrent > 1
- **Sample data**: `frontend/public/sample-results.json` for testing without running benchmarks

## How to Run

### Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r ollama_benchmark/requirements.txt
```

### Run benchmark
```bash
python -m ollama_benchmark.cli --model llama3.2
# Custom: --endpoint http://... --prompt-sizes 256,1024 --gen-tokens 256 --iterations 3 --concurrent 4
```

### View dashboard
```bash
cd frontend
npm install
npm run dev        # → http://localhost:5173
npm run build      # Production build → frontend/dist/
```

## Known Issues / Gotchas
- `retries_used` in run results is always 0 — the retry counter isn't propagated from `_retry_request()` to the result dict. The retry attempts are only visible in console logs.
- Prompt token counts are approximate (word-count heuristic, ~1.3 tokens/word). Actual token counts depend on the model's tokenizer.
- KV cache data depends on Ollama's `/api/stats` endpoint being available. If unavailable, `kv_cache` field is omitted from results.
- The `statistics` import in benchmark.py is unused (numpy is used instead).
- No GPU monitoring — explicitly excluded per user request.
- Frontend has a chunk size warning on build (Recharts is ~570KB). Could be code-split later.

## User Preferences (from conversation)
- Default endpoint: `http://127.0.0.1:11434` (not localhost)
- Use venv for Python
- No GPU monitoring
- Streaming mode for benchmarks
- JSON output + React/Vite/Tailwind frontend (not standalone HTML)
- Retry logic with exponential backoff for network failures
- Coding-assistant-style prompts for benchmarking