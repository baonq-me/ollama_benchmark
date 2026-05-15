# Changelog

## [0.1.0] - 2026-05-15

### Added
- Automatic model pull feature: The benchmark now automatically checks if the requested model exists locally and pulls it from Ollama if missing
- `--pull-missing` flag (default: enabled): Enables automatic model pull if not found locally
- `--no-pull` flag: Disables automatic model pull, runs benchmark anyway
- Individual iteration results display: CLI now shows a detailed table with results from each iteration run
- Download progress indicator: Shows real-time download speed and ETA when pulling models

### Changed
- `check_and_pull_model()` function added to `benchmark.py` for model availability checking and pulling
- `run_benchmark_suite()` now accepts `pull_if_missing` parameter (default: True)
- Download progress output consolidated to a single self-updating line showing:
  - Downloaded/Total MB
  - Percentage complete
  - Current download speed (MB/s)
  - Estimated time to completion (ETA)
- CLI output now includes individual run results table before the summary table
- Added `--pull-missing` and `--no-pull` CLI flags to `cli.py`

### Updated
- `README.md`: Added documentation for `--pull-missing` and `--no-pull` CLI flags
- `README.md`: Updated CLI Options table with new flags

### Files Modified
- `ollama_benchmark/benchmark.py`: Added `check_and_pull_model()` function, updated `run_benchmark_suite()` signature
- `ollama_benchmark/cli.py`: Added `print_individual_runs()` function, added `--pull-missing` and `--no-pull` flags
- `README.md`: Updated CLI Options documentation

### Technical Details
- Uses Ollama's `GET /api/tags` endpoint to check for local models
- Uses Ollama's `POST /api/pull` endpoint for model downloads with streaming progress
- Download progress updates at ~4 Hz using Rich console with carriage return (`\r`) for single-line updates
- Progress line uses Rich's `[cyan]` color markup for consistent styling