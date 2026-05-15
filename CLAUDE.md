# Ollama Benchmark - Agent Onboarding Guide

## Quick Overview

A Python CLI tool + React dashboard for benchmarking Ollama LLM performance. Measures input/output throughput, TTFT, total latency, and context scaling across multiple prompt sizes.

## Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Run a benchmark
python -m ollama_benchmark.cli --model llama3.2

# View results in dashboard
cd frontend && npm run dev
```

## Architecture

```
ollama_benchmark/
├── cli.py              # CLI entry point (argparse)
├── benchmark.py        # Core engine (run_benchmark_suite, run_single_benchmark)
└── requirements.txt    # Dependencies (requests, numpy, rich)

frontend/
├── src/App.jsx         # Main React component
└── src/components/     # Chart components (Recharts)
```

## Key Documents

| File | Purpose |
|------|---------|
| `docs/HARNESS.md` | Agent principles (control theory, sensors, feedback) |
| `docs/FILE_GUIDE.md` | Task-based navigation map |
| `docs/NOTES.md` | Known issues, architectural decisions |
| `docs/RESULT_FORMAT.md` | JSON output schema |
| `docs/CONTEXT.md` | Context engineering guidelines |
| `README.md` | Full user documentation |

## Common Tasks

| Task | Files to Read |
|------|---------------|
| Add new benchmark metric | `benchmark.py` → `cli.py` → `docs/RESULT_FORMAT.md` |
| Add CLI flag | `cli.py` → `README.md` |
| Add frontend chart | `App.jsx` → `src/components/` |
| Debug metric calculation | `benchmark.py` → `docs/RESULT_FORMAT.md` |

## Known Issues (see docs/NOTES.md)

- `retries_used` always returns 0 (retry counter not propagated)
- Prompt token counts are approximate (word-count heuristic)
- Unused imports may need cleanup

## Development Workflow

1. Read `docs/FILE_GUIDE.md` for task-specific navigation
2. Make changes in appropriate layer (CLI, Engine, Frontend)
3. Update `README.md` documentation if needed
4. Run `python -m ollama_benchmark.cli --help` to verify CLI
5. Check `docs/NOTES.md` for known issues before committing

## Current Version

v0.1.0