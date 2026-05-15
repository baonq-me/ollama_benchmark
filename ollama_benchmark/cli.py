#!/usr/bin/env python3
"""CLI entry point for Ollama Benchmark.

Usage:
    python -m ollama_benchmark.cli --model llama3.2
    python -m ollama_benchmark.cli --model llama3.2 --endpoint http://127.0.0.1:11434
    python -m ollama_benchmark.cli --model llama3.2 --prompt-sizes 64,256,1024 --gen-tokens 256 --iterations 3
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table

from ollama_benchmark.benchmark import run_benchmark_suite

console = Console()


def parse_prompt_sizes(value: str) -> list[int]:
    """Parse comma-separated prompt sizes, e.g. '64,256,512'."""
    sizes = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            sizes.append(int(part))
        except ValueError:
            raise argparse.ArgumentTypeError(f"Invalid prompt size: {part}")
    return sorted(sizes)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Benchmark Ollama model throughput and latency.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m ollama_benchmark.cli --model llama3.2
  python -m ollama_benchmark.cli --model codellama:7b --prompt-sizes 256,1024,4096 --gen-tokens 256
  python -m ollama_benchmark.cli --model mistral --endpoint http://192.168.1.100:11434 --concurrent 4
        """,
    )
    parser.add_argument(
        "--endpoint",
        default="http://127.0.0.1:11434",
        help="Ollama server URL (default: http://127.0.0.1:11434)",
    )
    parser.add_argument(
        "--model",
        default="qwen3.5:2b",
        help="Ollama model name (e.g. llama3.2, codellama:7b) (default: qwen3.5:2b)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON file path (default: frontend/public/results_{model}_{timestamp}.json)",
    )
    parser.add_argument(
        "--prompt-sizes",
        default="64,1024,8192",
        type=parse_prompt_sizes,
        help="Comma-separated prompt token counts (default: 64,1024,8192)",
    )
    parser.add_argument(
        "--gen-tokens",
        type=int,
        default=512,
        help="Target number of output tokens to generate (default: 512)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of benchmark runs per prompt size (default: 3)",
    )
    parser.add_argument(
        "--concurrent",
        type=int,
        default=1,
        help="Number of simultaneous requests for concurrent testing (default: 1)",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Max retry attempts on network failure (default: 3)",
    )
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=2.0,
        help="Base delay between retries in seconds, uses exponential backoff (default: 2.0)",
    )
    return parser


def print_individual_runs(data: dict) -> None:
    """Print individual run results for each iteration."""
    results = data.get("results", [])
    if not results:
        return

    # Get model name from metadata if available
    metadata = data.get("metadata", {})
    model_name = metadata.get("model", "Unknown")

    for entry in results:
        ps = entry["prompt_size"]
        runs = entry["runs"]

        console.rule(f"[bold cyan]Prompt Size: {ps} tokens — Individual Run Results[/bold cyan]")

        # Create table for individual runs
        table = Table(title=f"Model: {model_name}")
        table.add_column("Run", justify="center", style="cyan")
        table.add_column("TTFT (ms)", justify="right")
        table.add_column("Input t/s", justify="right")
        table.add_column("Output t/s", justify="right")
        table.add_column("Total Lat (ms)", justify="right")
        table.add_column("Prompt Tokens", justify="right")
        table.add_column("Output Tokens", justify="right")

        for i, run in enumerate(runs, 1):
            table.add_row(
                str(i),
                f"{run['ttft_ms']:.1f}",
                f"{run['input_tps']:.0f}",
                f"{run['output_tps']:.1f}",
                f"{run['total_latency_ms']:.0f}",
                str(run['prompt_tokens']),
                str(run['output_tokens']),
            )

        console.print(table)
        console.print()


def print_summary_table(data: dict) -> None:
    """Print a rich CLI table summarizing median metrics per prompt size."""
    results = data.get("results", [])
    if not results:
        console.print("[yellow]No results to display.[/yellow]")
        return

    # Get model name from metadata if available
    metadata = data.get("metadata", {})
    model_name = metadata.get("model", "Unknown")
    
    table = Table(title=f"Ollama Benchmark Results — {model_name} — Median Metrics")
    table.add_column("Prompt Size", justify="right", style="cyan")
    table.add_column("TTFT (ms)", justify="right")
    table.add_column("Input t/s", justify="right")
    table.add_column("Output t/s", justify="right")
    table.add_column("Total Lat (ms)", justify="right")

    for entry in results:
        ps = entry["prompt_size"]
        s = entry["stats"]

        table.add_row(
            str(ps),
            f"{s['ttft_ms']['median']:.1f}",
            f"{s['input_tps']['median']:.0f}",
            f"{s['output_tps']['median']:.1f}",
            f"{s['total_latency_ms']['median']:.0f}",
        )

    console.print(table)


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    console.print(f"[bold]Ollama Benchmark[/bold]")
    console.print(f"  Endpoint:  {args.endpoint}")
    console.print(f"  Model:     {args.model}")
    console.print(f"  Prompt sizes: {args.prompt_sizes}")
    console.print(f"  Gen tokens:   {args.gen_tokens}")
    console.print(f"  Iterations:   {args.iterations}")
    console.print(f"  Concurrent:   {args.concurrent}")
    console.print(f"  Retries:      {args.retries} (delay={args.retry_delay}s)")
    console.print()

    try:
        data = run_benchmark_suite(
            endpoint=args.endpoint,
            model=args.model,
            prompt_sizes=args.prompt_sizes,
            gen_tokens=args.gen_tokens,
            iterations=args.iterations,
            concurrent=args.concurrent,
            retries=args.retries,
            retry_delay=args.retry_delay,
        )
    except Exception as exc:
        console.print(f"[red]Fatal error: {exc}[/red]")
        sys.exit(1)

    # Write JSON output
    if args.output:
        output_path = Path(args.output)
    else:
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_model = args.model.replace(":", "_").replace("/", "_")
        output_path = Path(f"frontend/public/results_{safe_model}_{timestamp}.json")
    
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    console.print(f"\n[green]Results written to {output_path.resolve()}[/green]")

    # Print individual run results first
    console.print()
    print_individual_runs(data)

    # Print summary table with median metrics
    console.print()
    print_summary_table(data)


if __name__ == "__main__":
    main()