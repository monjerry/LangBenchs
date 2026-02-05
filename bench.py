import subprocess
import time
import os
import click

from html_report import generate_html

BASE = os.path.dirname(os.path.abspath(__file__))

BENCHMARKS = {
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

LANGUAGES = sorted(next(iter(BENCHMARKS.values())).keys())

def compile_benchmark(name, language):
    cmd = BENCHMARKS[name][language]["compile"]
    if cmd is None:
        return
    build_dir = os.path.join(BASE, language, "build")
    os.makedirs(build_dir, exist_ok=True)
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_benchmark(name, language):
    cmd = BENCHMARKS[name][language]["run"]
    start = time.perf_counter()
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return time.perf_counter() - start


@click.group()
def cli():
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
def for_loop(languages, runs, html_output, skip_first):
    """Benchmark: for loop (10 000 000 iterations)."""
    if skip_first and runs < 2:
        raise click.UsageError("--skip-first requires --runs >= 2")

    selected = [l.lower() for l in languages] if languages else LANGUAGES
    results = {}

    click.echo("\nCompiling...")
    for lang in selected:
        compile_benchmark("for_loop", lang)
    click.echo("Done.\n")

    click.echo("Running benchmarks...")
    for lang in selected:
        times = []
        for _ in range(runs):
            times.append(run_benchmark("for_loop", lang))
        results[lang] = times
    click.echo("Done.\n")

    # measured excludes run 1 when --skip-first is set; used for sorting, averages, and HTML
    measured = {l: t[1:] if skip_first else t for l, t in results.items()}
    sorted_langs = sorted(measured, key=lambda l: sum(measured[l]) / len(measured[l]))

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
