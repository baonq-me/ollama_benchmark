# Persistent Notes for Ollama Benchmark Project

This file serves as **agentic memory** for long-horizon tasks. It stores architectural decisions, known issues, session context, and task-based navigation guidance that should be carried forward across development sessions.

---

## Quick Reference: Task → Files to Read

| Task | Read Order | Files |
|------|------------|-------|
| **Add new benchmark metric** | 1→2→3 | `benchmark.py` → `cli.py` → `README.md` |
| **Fix CLI argument issue** | 1→2 | `cli.py` → `README.md` |
| **Add frontend chart** | 1→2→3 | `App.jsx` → `src/components/` → `frontend/README.md` |
| **Debug metric calculation** | 1→2 | `benchmark.py` → `docs/RESULT_FORMAT.md` |
| **Add new CLI flag** | 1→2 | `cli.py` → `README.md` |
| **Fix output JSON schema** | 1→2 | `benchmark.py` → `docs/RESULT_FORMAT.md` |
| **Modify prompt generation** | 1 | `benchmark.py` |
| **Change model pull behavior** | 1→2 | `benchmark.py` → `CHANGELOG.md` |
| **Add concurrent testing feature** | 1→2 | `benchmark.py` → `cli.py` |

---

## Component Dependency Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                        ENTRY POINTS                             │
├───────────────────────┬─────────────────────────────────────────┤
│   CLI Layer           │   Frontend Layer                        │
│   cli.py              │   App.jsx                               │
│   - argparse setup    │   - Main React component                │
│   - argument parsing  │   - FileLoader integration              │
│   - result display    │   - Chart composition                   │
└──────────┬────────────┴────────────────┬────────────────────────┘
           │                              │
           ▼                              ▼
┌─────────────────────┐      ┌──────────────────────────────────┐
│  Engine Layer       │      │  Component Layer                  │
│  benchmark.py       │      │  src/components/                  │
│  - run_benchmark    │      │  - FileLoader.jsx                 │
│  - run_single       │      │  - SummaryTable.jsx               │
│  - metrics calc     │      │  - ThroughputCharts.jsx           │
│  - model pull       │      │  - LatencyCharts.jsx              │
└──────────┬──────────┘      │  - ConcurrentCharts.jsx           │
           │                 └────────────────┬─────────────────┘
           ▼                                  │
┌─────────────────────┐                       │
│  Output Layer       │                       │
│  JSON Schema        │                       │
│  - metadata         │                       │
│  - results          │◄──────────────────────┘
│  - stats            │    (consumes JSON)
└─────────────────────┘
```

---

## Task-Based File Paths

### 1. Benchmark Logic Changes
```
Core files:
  ollama_benchmark/benchmark.py
    ├── generate_prompt()          (lines 37-68)
    ├── run_single_benchmark()     (lines 116-244)
    ├── _retry_request()           (lines 73-111)
    ├── check_and_pull_model()     (lines 265-421)
    └── run_benchmark_suite()      (lines 424-540)
  
  ollama_benchmark/cli.py
    ├── main()                     (argparse entry point)
    └── print_results()            (CLI output formatting)
```

### 2. Frontend Chart Changes
```
Core files:
  frontend/src/App.jsx
    ├── FileLoader.jsx             (file upload integration)
    └── Chart components           (rendering logic)
  
  frontend/src/components/
    ├── SummaryTable.jsx           (metrics table)
    ├── ThroughputCharts.jsx       (input/output tps charts)
    ├── LatencyCharts.jsx          (TTFT/total latency charts)
    └── ConcurrentCharts.jsx       (concurrent performance chart)
```

### 3. Output Format Changes
```
Core files:
  ollama_benchmark/benchmark.py
    └── run_benchmark_suite() return value (lines 529-540)
  
  docs/RESULT_FORMAT.md
    └── JSON schema documentation
```

### 4. CLI Interface Changes
```
Core files:
  ollama_benchmark/cli.py
    └── main() argparse configuration
  
  README.md
    └── CLI Options table
```

---

## Common Scenarios

### Scenario A: Add New Metric (e.g., "cache_hit_rate")

1. **Read `benchmark.py`** (lines 116-244)
   - Find `run_single_benchmark()` return dict
   - Add new metric calculation
   
2. **Read `benchmark.py`** (lines 249-260)
   - Find `_compute_stats()` helper
   - Verify it handles new metric type
   
3. **Read `cli.py`**
   - Find result printing logic
   - Add new metric to display table
   
4. **Read `docs/RESULT_FORMAT.md`**
   - Update JSON schema documentation

### Scenario B: Add New Chart Type to Dashboard

1. **Read `App.jsx`**
   - Understand file loading flow
   - See how components are composed
   
2. **Read existing chart components**
   - `ThroughputCharts.jsx` (example of line chart)
   - `LatencyCharts.jsx` (example with P95/P99 bands)
   
3. **Create new component** in `src/components/`
   - Follow existing patterns
   - Use Recharts library
   
4. **Read `App.jsx`** again
   - Integrate new chart into main layout

### Scenario C: Modify Prompt Generation Strategy

1. **Read `benchmark.py`** (lines 16-68)
   - Understand `SYSTEM_PROMPT` and `PROMPT_TEMPLATE`
   - See `generate_prompt()` implementation
   
2. **Read `docs/CONTEXT.md`** (optional)
   - For context engineering best practices
   
3. **Modify `generate_prompt()`**
   - Update padding sentences
   - Adjust token calculation heuristics

### Scenario D: Debug Metric Calculation Issue

1. **Read `benchmark.py`** (lines 116-244)
   - Trace `run_single_benchmark()` metrics computation
   
2. **Read `docs/RESULT_FORMAT.md`**
   - Verify expected metric definitions
   
3. **Read `docs/CHANGELOG.md`** (optional)
   - Check if recent changes affected metrics

---

## File Reading Priority by Task Type

| Task Type | Primary Files | Secondary Files |
|-----------|---------------|-----------------|
| **Bug fix (CLI)** | `cli.py` | `README.md` |
| **Bug fix (engine)** | `benchmark.py` | `docs/RESULT_FORMAT.md` |
| **Bug fix (frontend)** | `frontend/src/App.jsx` | `frontend/src/components/*` |
| **Feature (CLI)** | `cli.py` | `benchmark.py` |
| **Feature (engine)** | `benchmark.py` | `docs/RESULT_FORMAT.md` |
| **Feature (frontend)** | `frontend/src/App.jsx` | `frontend/src/components/*` |
| **Documentation** | `README.md` | `docs/*` |
| **Testing** | `docs/HARNESS.md` | `benchmark.py` |

---

## Key Entry Points

### Python CLI Entry Point
```
ollama_benchmark/cli.py
  └── main() → argparse → benchmark.run_benchmark_suite()
```

### Frontend Entry Point
```
frontend/src/main.jsx
  └── React.render() → App.jsx
       └── App.jsx
            ├── FileLoader component
            ├── SummaryTable component
            └── Chart components
```

### Benchmark Engine Entry Point
```
ollama_benchmark/benchmark.py
  └── run_benchmark_suite()
       └── run_single_benchmark() (per iteration)
            └── _retry_request() (with retry logic)
```

---

## Cross-References

| Concept | Defined In | Used In |
|---------|------------|---------|
| Prompt generation | `benchmark.py` (lines 37-68) | `benchmark.py` (lines 464-466) |
| Retry logic | `benchmark.py` (lines 73-111) | `benchmark.py` (lines 149-157) |
| Model pull | `benchmark.py` (lines 265-421) | `benchmark.py` (lines 454-462) |
| Metrics calculation | `benchmark.py` (lines 217-234) | `cli.py` (display) |
| JSON output | `benchmark.py` (lines 529-540) | `frontend/*` (consumption) |
| Chart rendering | `frontend/src/components/*` | `App.jsx` |

---

## Current State

### Recent Work (Last Session)
- **Created**: `docs/NOTES.md` - Persistent notes file (merged FILE_GUIDE.md)
- **Created**: `CLAUDE.md` - Agent onboarding guide
- **Focus**: Implementing context engineering improvements per docs/CONTEXT.md

### Active Tasks
- [ ] N/A (no active tasks)

### Completed Tasks
- [x] Added automatic model pull feature (v0.1.0)
- [x] Added individual iteration results display
- [x] Created file discovery guide
- [x] Created persistent notes file
- [x] Created agent onboarding guide (CLAUDE.md)
- [x] Fixed `retries_used` propagation bug in `_retry_request()`
- [x] Removed unused `statistics` import
- [x] Added pytest, ruff, mypy to requirements
- [x] Created pyproject.toml with linting configuration
- [x] Added unit tests for benchmark and CLI modules

---

## Architectural Decisions Log (ADL)

### ADL-001: Streaming SSE Parsing
**Date**: 2026-05-15  
**Decision**: Use SSE streaming with `response.iter_lines()` instead of batch API  
**Rationale**: Enables real-time token timing measurements (TTFT, per-token latency)  
**Trade-offs**: 
- + Accurate timing measurements
- + Real-time progress feedback
- - More complex error handling

### ADL-002: Rich Console Library
**Date**: 2026-05-15  
**Decision**: Use Rich for CLI output formatting  
**Rationale**: Provides consistent styling, progress indicators, and structured tables  
**Trade-offs**:
- + Beautiful terminal output
- + Built-in progress tracking
- - Additional dependency

### ADL-003: React + Vite + Tailwind v4 Frontend
**Date**: 2026-05-15  
**Decision**: Use Vite 8 + React 19 + Tailwind CSS v4  
**Rationale**: Modern stack with fast HMR, type safety, and utility-first styling  
**Trade-offs**:
- + Fast development workflow
- + Dark theme out of the box
- - Build chunk size (~570KB Recharts)

### ADL-004: JSON Output Schema
**Date**: 2026-05-15  
**Decision**: Structured JSON with metadata + results + stats hierarchy  
**Rationale**: Machine-readable format for frontend parsing and external tool integration  
**Trade-offs**:
- + Easy frontend integration
- + Clear separation of concerns
- - Increased file size vs plain text

### ADL-005: Virtual Environment Requirement
**Date**: 2026-05-15  
**Decision**: Require Python venv for all CLI operations  
**Rationale**: Isolates dependencies, prevents version conflicts  
**Trade-offs**:
- + Clean dependency management
- + Reproducible environments
- - Extra activation step for users

### ADL-006: Retry Logic with Exponential Backoff
**Date**: 2026-05-15  
**Decision**: Implement `_retry_request()` with exponential backoff (delay * 2^(attempt-1))  
**Rationale**: Handles transient network failures gracefully  
**Trade-offs**:
- + Resilient to network issues
- + Configurable retry count/delay
- - Added complexity in error tracking

---

## Known Issues

### HIGH Priority
1. **retries_used always 0** (from README)
   - Location: `benchmark.py` line 243
   - Issue: Retry counter isn't propagated from `_retry_request()` to result dict
   - Impact: Users can't see retry attempts in JSON output
   - Fix approach: Track retry count in `_retry_request()` and return it

### MEDIUM Priority
2. **Prompt token counts are approximate**
   - Location: `benchmark.py` lines 37-68
   - Issue: Uses word-count heuristic (~1.3 tokens/word)
   - Impact: Actual token counts vary by model tokenizer
   - Mitigation: Documented in README

3. **Frontend chunk size warning**
   - Location: `frontend/src/components/*`
   - Issue: Recharts bundle is ~570KB
   - Impact: Slower initial page load
   - Fix approach: Consider code-splitting Recharts

### LOW Priority
4. **Unused import in benchmark.py**
   - Location: `benchmark.py` line 6
   - Issue: `import statistics` is unused (numpy is used instead)
   - Impact: Minor lint warning
   - Fix: Remove unused import

5. **No GPU monitoring**
   - Location: N/A (by design)
   - Issue: GPU utilization metrics not collected
   - Impact: Missing performance context
   - Status: Explicitly excluded per user request

---

## Session Context

### Last Session (2026-05-15)
- **Goal**: Implement context engineering improvements
- **Completed**: Created NOTES.md (merged FILE_GUIDE.md)
- **Carry-forward**: No unresolved tasks

### Session Template (for future use)
```
### Session: [DATE]
**Goal**: [What you're trying to accomplish]
**Started from**: [Previous session's last state]
**Work done**:
  - [Task 1]
  - [Task 2]
**Blocked on**: [Any blockers]
**Next session should**: [Recommended next steps]
```

---

## Development Workflow Notes

### Adding New Metrics
1. Calculate metric in `run_single_benchmark()`
2. Add to return dict
3. Update `_compute_stats()` if needed
4. Display in `cli.py` result table
5. Update `docs/RESULT_FORMAT.md` schema
6. Add chart component if visualization needed

### Adding New CLI Flags
1. Add to `cli.py` argparse configuration
2. Pass through to `run_benchmark_suite()`
3. Update `README.md` CLI Options table
4. Add default value to metadata in JSON output

### Frontend Component Guidelines
- Use Recharts 3.x patterns
- Follow dark theme (gray-950 background)
- ResponsiveContainer for all charts
- Tooltips with consistent styling
- P95/P99 as dashed lines for percentiles

---

## Dependencies and Versions

### Python
- Python 3.10+
- requests (HTTP client)
- numpy (statistics)
- rich (CLI formatting)

### Frontend
- React 19
- Vite 8
- Tailwind CSS v4
- Recharts 3

### Backend
- Ollama server (local or remote)
  - API: `/api/chat` (streaming)
  - API: `/api/tags` (model listing)
  - API: `/api/pull` (model download)

---

## Quick Reference

### File Locations
| Component | File Path |
|-----------|-----------|
| CLI Entry | `ollama_benchmark/cli.py` |
| Benchmark Engine | `ollama_benchmark/benchmark.py` |
| React Entry | `frontend/src/main.jsx` |
| Main Component | `frontend/src/App.jsx` |
| Chart Components | `frontend/src/components/` |

### Key Functions
| Function | File | Purpose |
|----------|------|---------|
| `generate_prompt()` | `benchmark.py:37` | Create test prompts |
| `run_single_benchmark()` | `benchmark.py:116` | Execute one benchmark run |
| `_retry_request()` | `benchmark.py:73` | Retry with exponential backoff |
| `check_and_pull_model()` | `benchmark.py:265` | Model availability check |
| `run_benchmark_suite()` | `benchmark.py:424` | Full benchmark execution |

### Key Line Numbers (benchmark.py)
- Lines 16-68: Prompt generation
- Lines 73-111: Retry helper
- Lines 116-244: Single benchmark run
- Lines 249-260: Statistics computation
- Lines 265-421: Model pull logic
- Lines 424-540: Benchmark suite

---

## Changelog Summary

### v0.1.0 (2026-05-15)
- Added automatic model pull with progress indicator
- Added individual iteration results display
- Added multi-file upload to frontend
- Removed KV Cache column from summary table
- Implemented color-coded multi-legend for N benchmarks
- Created NOTES.md for persistent memory (merged FILE_GUIDE.md)

---

## TODO List

### Pending Features
- [ ] Add GPU monitoring (optional, per ADL)
- [ ] Code-split Recharts for smaller bundle
- [ ] Add unit tests for benchmark logic
- [ ] Add E2E tests for CLI workflow

### Pending Fixes
- [ ] Fix `retries_used` always being 0
- [ ] Remove unused `statistics` import

### Future Enhancements
- [ ] Add export to CSV format
- [ ] Add comparison mode (baseline vs new model)
- [ ] Add model cost estimation
- [ ] Add custom prompt support