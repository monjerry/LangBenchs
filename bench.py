"""CLI benchmark runner for comparing language performance across different tasks."""

import subprocess
import time
import os

import click

from html_report import generate_html

BASE: str = os.path.dirname(os.path.abspath(__file__))

# Each benchmark maps language -> { "compile": cmd | None, "run": cmd }.
# "compile" is None for interpreted languages.
BENCHMARKS: dict[str, dict[str, dict[str, list[str] | None]]] = {
    "for_loop": {
        "c++": {
            "compile": ["g++", "-O2", "-o", os.path.join(BASE, "c++", "build", "for_loop"), os.path.join(BASE, "c++", "for_loop.cpp")],
            "run": [os.path.join(BASE, "c++", "build", "for_loop")],
        },
        "go": {
            "compile": ["go", "build", "-o", os.path.join(BASE, "go", "build", "for_loop"), os.path.join(BASE, "go", "for_loop.go")],
            "run": [os.path.join(BASE, "go", "build", "for_loop")],
        },
        "java": {
            "compile": ["javac", "-d", os.path.join(BASE, "java", "build"), os.path.join(BASE, "java", "ForLoop.java")],
            "run": ["java", "-cp", os.path.join(BASE, "java", "build"), "ForLoop"],
        },
        "node": {
            "compile": None,
            "run": ["node", os.path.join(BASE, "node", "for_loop.js")],
        },
        "python": {
            "compile": None,
            "run": ["python3", os.path.join(BASE, "python", "for_loop.py")],
        },
        "rust": {
            "compile": ["rustc", "-O", "-o", os.path.join(BASE, "rust", "build", "for_loop"), os.path.join(BASE, "rust", "for_loop.rs")],
            "run": [os.path.join(BASE, "rust", "build", "for_loop")],
        },
    },
}

LANGUAGES: list[str] = sorted(next(iter(BENCHMARKS.values())).keys())


def compile_benchmark(name: str, language: str) -> None:
    """Compile a benchmark for a given language.

    Creates the per-language build/ directory if it does not exist, then runs
    the compile command defined in BENCHMARKS.  Does nothing for interpreted
    languages (where compile is None).

    Args:
        name: The benchmark name (key in BENCHMARKS).
        language: The language to compile (e.g. "c++", "rust").
    """
    cmd = BENCHMARKS[name][language]["compile"]
    if cmd is None:
        return
    build_dir = os.path.join(BASE, language, "build")
    os.makedirs(build_dir, exist_ok=True)
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_benchmark(name: str, language: str) -> float:
    """Execute a benchmark and return the elapsed wall-clock time in seconds.

    Args:
        name: The benchmark name (key in BENCHMARKS).
        language: The language to run (e.g. "python", "go").

    Returns:
        Elapsed time in seconds measured via time.perf_counter().
    """
    cmd = BENCHMARKS[name][language]["run"]
    start = time.perf_counter()
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return time.perf_counter() - start


@click.group()
def cli() -> None:
    """Language benchmark runner."""


@cli.command()
@click.option(
    "--languages",
    "-l",
    multiple=True,
    type=click.Choice(LANGUAGES, case_sensitive=False),
    help="Languages to benchmark. Defaults to all.",
)
@click.option(
    "--runs",
    "-r",
    default=1,
    show_default=True,
    help="Number of measured runs (a warm-up run is always done first).",
)
@click.option(
    "--html",
    "html_output",
    default=None,
    type=click.Path(dir_okay=False, writable=True),
    help="If set, write an HTML report with a chart to this path.",
)
@click.option(
    "--skip-first",
    is_flag=True,
    default=False,
    help="Exclude the first run from averages and the HTML report (useful to drop cold-start).",
)
def for_loop(languages: tuple[str, ...], runs: int, html_output: str | None, skip_first: bool) -> None:
    """Benchmark: for loop (10 000 000 iterations)."""
    if skip_first and runs < 2:
        raise click.UsageError("--skip-first requires --runs >= 2")

    selected: list[str] = [l.lower() for l in languages] if languages else LANGUAGES
    results: dict[str, list[float]] = {}

    click.echo("\nCompiling...")
    for lang in selected:
        compile_benchmark("for_loop", lang)
    click.echo("Done.\n")

    click.echo("Running benchmarks...")
    for lang in selected:
        times: list[float] = []
        for _ in range(runs):
            times.append(run_benchmark("for_loop", lang))
        results[lang] = times
    click.echo("Done.\n")

    # measured excludes run 1 when --skip-first is set; used for sorting, averages, and HTML
    measured: dict[str, list[float]] = {l: t[1:] if skip_first else t for l, t in results.items()}
    sorted_langs: list[str] = sorted(measured, key=lambda l: sum(measured[l]) / len(measured[l]))

    click.echo(f"{'Language':<10} {'Run':<5} {'Time (s)':<12}")
    click.echo("-" * 30)
    for lang in sorted_langs:
        for r, elapsed in enumerate(results[lang], 1):
            suffix = " (skipped)" if skip_first and r == 1 else ""
            click.echo(f"{lang:<10} {r:<5} {elapsed:<12.4f}{suffix}")

    if len(measured[sorted_langs[0]]) > 1:
        click.echo("\n" + "-" * 30)
        click.echo(f"{'Language':<10} {'Avg (s)':<12}")
        click.echo("-" * 30)
        for lang in sorted_langs:
            avg = sum(measured[lang]) / len(measured[lang])
            click.echo(f"{lang:<10} {avg:<12.4f}")

    click.echo()

    if html_output:
        generate_html("for_loop", measured, sorted_langs, html_output)
        click.echo(f"HTML report written to {html_output}")


if __name__ == "__main__":
    cli()
