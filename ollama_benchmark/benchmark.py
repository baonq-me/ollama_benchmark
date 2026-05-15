"""Benchmark engine for Ollama model throughput and latency measurement."""

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import requests
import numpy as np
from rich.console import Console

console = Console()

# ── Prompt generation ──────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are an expert coding assistant. You provide clear, concise, "
    "and correct answers to programming questions. Always include code "
    "examples when relevant and explain your reasoning step by step."
)

# A coding-related prompt template that we pad to reach the target token count.
# ~1.3 tokens per English word is a reasonable heuristic for most LLM tokenizers.
PROMPT_TEMPLATE = (
    "I need help with a complex software engineering problem. "
    "I am building a distributed system that needs to handle high-throughput "
    "data processing with the following requirements:\n\n"
    "{padding}\n\n"
    "Please provide a detailed solution including architecture, code examples, "
    "and trade-off analysis. Consider edge cases like network partitions, "
    "data consistency, and monitoring."
)


def generate_prompt(target_tokens: int) -> str:
    """Generate a coding-assistant prompt of approximately *target_tokens* tokens.

    Uses a word-count heuristic (~1.3 tokens/word) to pad a base template.
    """
    base_words = len(PROMPT_TEMPLATE.format(padding="").split())
    target_words = int(target_tokens / 1.3)
    padding_words_needed = max(0, target_words - base_words)

    # Build padding from repeated technical sentences
    padding_sentences = [
        "The system must support horizontal scaling across multiple availability zones.",
        "We need to ensure exactly-once processing semantics for all critical events.",
        "Latency should remain under 100ms at the 99th percentile under peak load.",
        "The data pipeline includes ingestion, validation, transformation, and storage stages.",
        "We are using Kafka for message queuing and PostgreSQL for persistent storage.",
        "Authentication and authorization must follow OAuth2 with role-based access control.",
        "All services must expose health-check endpoints and integrate with Prometheus for monitoring.",
        "The deployment strategy uses blue-green deployments with automated rollback capabilities.",
        "We need comprehensive integration tests covering all failure scenarios.",
        "The system processes approximately 50,000 events per second during normal operation.",
    ]

    padding_parts: list[str] = []
    while len(" ".join(padding_parts).split()) < padding_words_needed:
        for sentence in padding_sentences:
            padding_parts.append(sentence)
            if len(" ".join(padding_parts).split()) >= padding_words_needed:
                break

    padding = " ".join(padding_parts)
    return PROMPT_TEMPLATE.format(padding=padding)


# ── Retry helper ────────────────────────────────────────────────────────────

def _retry_request(
    method: str,
    url: str,
    retries: int,
    retry_delay: float,
    **kwargs: Any,
) -> tuple[requests.Response, int]:
    """Perform an HTTP request with exponential-backoff retry logic.

    Catches ConnectionError, Timeout, ChunkedEncodingError, and HTTP 5xx.
    Returns a tuple of (response, retries_used) on success.
    Raises the last exception after all retries are exhausted.
    """
    last_exception: Exception | None = None
    retries_used = 0

    for attempt in range(1, retries + 1):
        try:
            resp = requests.request(method, url, **kwargs)
            if resp.status_code >= 500:
                raise requests.exceptions.HTTPError(
                    f"Server error {resp.status_code}", response=resp
                )
            retries_used = attempt - 1  # 0 if first attempt succeeded
            return resp, retries_used
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.HTTPError,
        ) as exc:
            last_exception = exc
            retries_used = attempt
            if attempt < retries:
                delay = retry_delay * (2 ** (attempt - 1))
                console.log(
                    f"[yellow]Attempt {attempt}/{retries} failed: {exc}. "
                    f"Retrying in {delay:.1f}s...[/yellow]"
                )
                time.sleep(delay)

    raise last_exception  # type: ignore[misc]


# ── Single benchmark run ────────────────────────────────────────────────────

def run_single_benchmark(
    endpoint: str,
    model: str,
    prompt_text: str,
    gen_tokens: int,
    retries: int = 3,
    retry_delay: float = 2.0,
) -> dict[str, Any]:
    """Run a single streaming benchmark against the Ollama /api/chat endpoint.

    Returns a dict with keys:
        ttft_ms, input_tps, output_tps, total_latency_ms,
        prompt_tokens, output_tokens, retries_used
    """
    url = f"{endpoint.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_text},
        ],
        "stream": True,
        "options": {"num_predict": gen_tokens},
    }

    request_start = time.perf_counter()
    first_token_time: float | None = None
    last_token_time: float | None = None
    output_content_length = 0
    final_chunk: dict[str, Any] = {}
    retries_used = 0

    try:
        response, retries_used = _retry_request(
            "POST",
            url,
            retries=retries,
            retry_delay=retry_delay,
            json=payload,
            stream=True,
            timeout=300,
        )
    except Exception:
        # All retries exhausted
        raise

    try:
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            # Some proxies return raw bytes even with decode_unicode=True
            if isinstance(line, bytes):
                line = line.decode("utf-8")

            # Parse the JSON payload — supports both formats:
            #   SSE:  "data: {...}"  (standard Ollama)
            #   NDJSON: "{...}"       (some proxies)
            data_str = line
            if line.startswith("data: "):
                data_str = line[6:]
                if data_str == "[DONE]":
                    break

            try:
                chunk = json.loads(data_str)
            except json.JSONDecodeError:
                continue

            now = time.perf_counter()

            if first_token_time is None:
                first_token_time = now

            last_token_time = now

            if chunk.get("done"):
                final_chunk = chunk
            else:
                content = chunk.get("message", {}).get("content", "")
                output_content_length += len(content)
    finally:
        response.close()

    if first_token_time is None:
        raise RuntimeError("No tokens received from Ollama — empty stream")

    # Use server-reported counts from the final chunk when available
    prompt_tokens = final_chunk.get("prompt_eval_count", 0)
    prompt_eval_duration_ns = final_chunk.get("prompt_eval_duration", 0)
    output_tokens = final_chunk.get("eval_count", 0)
    eval_duration_ns = final_chunk.get("eval_duration", 0)

    # Fallback: estimate from content length if server didn't report
    if output_tokens == 0:
        output_tokens = max(1, int(output_content_length / 4))  # rough char→token

    # Compute metrics
    ttft_ms = (first_token_time - request_start) * 1000

    # Input throughput (prefill): use server-reported prompt_eval_duration
    if prompt_eval_duration_ns > 0:
        input_tps = prompt_tokens / (prompt_eval_duration_ns / 1e9)
    else:
        # Fallback: TTFT approximates prefill time
        input_tps = prompt_tokens / max(ttft_ms / 1000, 0.001)

    # Output throughput (decode): time between first and last token
    decode_time = (last_token_time - first_token_time) if last_token_time and first_token_time else 0.001
    if eval_duration_ns > 0:
        output_tps = output_tokens / (eval_duration_ns / 1e9)
    else:
        output_tps = output_tokens / max(decode_time, 0.001)

    total_latency_ms = (last_token_time - request_start) * 1000 if last_token_time else 0

    return {
        "ttft_ms": round(ttft_ms, 2),
        "input_tps": round(input_tps, 2),
        "output_tps": round(output_tps, 2),
        "total_latency_ms": round(total_latency_ms, 2),
        "prompt_tokens": prompt_tokens,
        "output_tokens": output_tokens,
        "retries_used": retries_used,
    }


# ── Statistics helpers ──────────────────────────────────────────────────────

def _compute_stats(values: list[float]) -> dict[str, float]:
    """Compute median, P95, P99, min, max for a list of values."""
    if not values:
        return {"median": 0, "p95": 0, "p99": 0, "min": 0, "max": 0}
    arr = np.array(values)
    return {
        "median": round(float(np.median(arr)), 2),
        "p95": round(float(np.percentile(arr, 95)), 2),
        "p99": round(float(np.percentile(arr, 99)), 2),
        "min": round(float(np.min(arr)), 2),
        "max": round(float(np.max(arr)), 2),
    }


# ── Benchmark suite ─────────────────────────────────────────────────────────

def check_and_pull_model(
    endpoint: str,
    model: str,
    retries: int = 3,
    retry_delay: float = 2.0,
) -> bool:
    """Check if model exists locally, pull if needed.

    Returns True if model is available (either already exists or was pulled successfully).
    Returns False if pull failed or model is still not available.
    """
    url_tags = f"{endpoint.rstrip('/')}/api/tags"
    url_pull = f"{endpoint.rstrip('/')}/api/pull"

    # Step 1: Check if model exists in local models list
    try:
        response, _ = _retry_request(
            "GET",
            url_tags,
            retries=retries,
            retry_delay=retry_delay,
            timeout=30,
        )
        data = response.json()
        local_models = data.get("models", [])
        model_names = [m.get("name", "") for m in local_models]

        # Check if exact match or base name match exists
        model_base = model.split(":")[0]  # e.g., "llama3.2" from "llama3.2:7b"
        if model in model_names or model_base in model_names:
            console.log(f"[green]✓ Model '{model}' already available locally[/green]")
            return True
    except Exception as exc:
        console.log(f"[yellow]Warning: Could not list local models: {exc}[/yellow]")

    # Step 2: Model not found, pull it
    console.log(f"[cyan]Model '{model}' not found. Pulling from Ollama...[/cyan]")

    try:
        pull_response, _ = _retry_request(
            "POST",
            url_pull,
            retries=retries,
            retry_delay=retry_delay,
            json={"model": model, "stream": True},
            stream=True,
            timeout=600,  # 10 minute timeout for large model pulls
        )

        # Parse SSE stream to show download progress (single line with speed + ETA)
        last_status = ""
        total_bytes = 0
        completed_bytes = 0
        download_start = time.perf_counter()
        last_progress_time = download_start
        last_completed_bytes = 0

        for line in pull_response.iter_lines(decode_unicode=True):
            if not line:
                continue
            if isinstance(line, bytes):
                line = line.decode("utf-8")

            data_str = line
            if line.startswith("data: "):
                data_str = line[6:]

            try:
                chunk = json.loads(data_str)
            except json.JSONDecodeError:
                continue

            status = chunk.get("status", "")
            last_status = status

            if status == "success":
                console.log(f"[green]✓ Successfully pulled model '{model}'[/green]")
                return True

            if "total" in chunk:
                total_bytes = chunk["total"]

            if "completed" in chunk:
                completed_bytes = chunk["completed"]
                now = time.perf_counter()

                # Update progress at most ~4 times per second
                if total_bytes > 0 and (now - last_progress_time >= 0.25 or completed_bytes >= total_bytes):
                    elapsed = now - download_start
                    progress_elapsed = now - last_progress_time
                    bytes_delta = completed_bytes - last_completed_bytes

                    # Calculate speed (MB/s) over the recent interval
                    if progress_elapsed > 0:
                        speed_mbs = (bytes_delta / (1024 * 1024)) / progress_elapsed
                    else:
                        speed_mbs = 0

                    # Calculate overall average speed (MB/s) for ETA
                    if elapsed > 0:
                        avg_speed_mbs = (completed_bytes / (1024 * 1024)) / elapsed
                    else:
                        avg_speed_mbs = 0

                    # Calculate ETA
                    remaining_bytes = total_bytes - completed_bytes
                    if avg_speed_mbs > 0:
                        eta_seconds = remaining_bytes / (avg_speed_mbs * 1024 * 1024)
                        if eta_seconds < 60:
                            eta_str = f"{eta_seconds:.0f}s"
                        else:
                            eta_min = int(eta_seconds // 60)
                            eta_sec = int(eta_seconds % 60)
                            eta_str = f"{eta_min}m{eta_sec:02d}s"
                    else:
                        eta_str = "---"

                    percent = (completed_bytes / total_bytes) * 100
                    mb_completed = completed_bytes / (1024 * 1024)
                    mb_total = total_bytes / (1024 * 1024)

                    # Single-line progress (Rich console with \r to overwrite same line)
                    progress_line = (
                        f"Downloading: {mb_completed:.1f}/{mb_total:.1f} MB "
                        f"({percent:.1f}%)  {speed_mbs:.1f} MB/s  ETA: {eta_str}"
                    )
                    console.print(f"[cyan]{progress_line}[/cyan]", end="\r")

                    last_progress_time = now
                    last_completed_bytes = completed_bytes

        # Clear the progress line and move to next line on completion
        console.print()

        # If we exit the loop without "success", check if model is now available
        if last_status != "success":
            console.log(f"[yellow]Pull may have completed with status: {last_status}[/yellow]")
            # Try again to verify
            verify_response, _ = _retry_request(
                "GET",
                url_tags,
                retries=1,
                retry_delay=0,
                timeout=30,
            )
            data = verify_response.json()
            local_models = data.get("models", [])
            model_names = [m.get("name", "") for m in local_models]
            model_base = model.split(":")[0]
            if model in model_names or model_base in model_names:
                console.log(f"[green]✓ Model '{model}' is now available[/green]")
                return True

    except Exception as exc:
        console.log(f"[red]✗ Failed to pull model '{model}': {exc}[/red]")

    return False


def run_benchmark_suite(
    endpoint: str,
    model: str,
    prompt_sizes: list[int],
    gen_tokens: int,
    iterations: int = 5,
    concurrent: int = 1,
    retries: int = 3,
    retry_delay: float = 2.0,
) -> dict[str, Any]:
    """Run the full benchmark suite across all prompt sizes.

    Args:
        endpoint: Ollama server URL
        model: Model name to benchmark
        prompt_sizes: List of prompt token counts to test
        gen_tokens: Target number of output tokens
        iterations: Number of benchmark runs per prompt size
        concurrent: Number of simultaneous requests
        retries: Max retry attempts on network failure
        retry_delay: Base delay between retries

    Returns:
        A dict matching the JSON output schema
    """
    results: list[dict[str, Any]] = []

    # Always check and pull model if missing
    model_available = check_and_pull_model(
        endpoint, model, retries, retry_delay
    )
    if not model_available:
        console.log(
            f"[yellow]Warning: Model '{model}' may not be fully available. "
            f"Proceeding with benchmark anyway...[/yellow]"
        )

    for prompt_size in prompt_sizes:
        console.rule(f"[bold cyan]Prompt size: {prompt_size} tokens[/bold cyan]")
        prompt_text = generate_prompt(prompt_size)

        runs: list[dict[str, Any]] = []

        if concurrent > 1:
            # Concurrent mode: fire all requests simultaneously
            console.log(f"Running {iterations} iterations with concurrency={concurrent}...")
            with ThreadPoolExecutor(max_workers=concurrent) as executor:
                futures = [
                    executor.submit(
                        run_single_benchmark,
                        endpoint, model, prompt_text, gen_tokens, retries, retry_delay,
                    )
                    for _ in range(iterations)
                ]
                for i, future in enumerate(as_completed(futures), 1):
                    try:
                        result = future.result()
                        runs.append(result)
                        console.log(
                            f"  [{i}/{iterations}] "
                            f"TTFT={result['ttft_ms']:.1f}ms  "
                            f"In={result['input_tps']:.0f} t/s  "
                            f"Out={result['output_tps']:.1f} t/s"
                        )
                    except Exception as exc:
                        console.log(f"  [{i}/{iterations}] [red]Failed: {exc}[/red]")
        else:
            # Sequential mode
            for i in range(1, iterations + 1):
                try:
                    result = run_single_benchmark(
                        endpoint, model, prompt_text, gen_tokens, retries, retry_delay
                    )
                    runs.append(result)
                    console.log(
                        f"  [{i}/{iterations}] "
                        f"TTFT={result['ttft_ms']:.1f}ms  "
                        f"In={result['input_tps']:.0f} t/s  "
                        f"Out={result['output_tps']:.1f} t/s"
                    )
                except Exception as exc:
                    console.log(f"  [{i}/{iterations}] [red]Failed: {exc}[/red]")

        if not runs:
            console.log("[red]All runs failed for this prompt size — skipping[/red]")
            continue

        # Compute aggregate statistics
        stats = {
            "ttft_ms": _compute_stats([r["ttft_ms"] for r in runs]),
            "input_tps": _compute_stats([r["input_tps"] for r in runs]),
            "output_tps": _compute_stats([r["output_tps"] for r in runs]),
            "total_latency_ms": _compute_stats([r["total_latency_ms"] for r in runs]),
        }

        entry: dict[str, Any] = {
            "prompt_size": prompt_size,
            "runs": runs,
            "stats": stats,
        }
        results.append(entry)

    return {
        "metadata": {
            "model": model,
            "gen_tokens": gen_tokens,
            "iterations": iterations,
            "concurrent": concurrent,
            "retries": retries,
            "retry_delay": retry_delay,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        },
        "results": results,
    }