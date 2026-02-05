import subprocess
import time
import os

import click

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
    help="Number of times to run each benchmark.",
)
def for_loop(languages, runs):
    """Benchmark: for loop (10 000 000 iterations)."""
    selected = [l.lower() for l in languages] if languages else LANGUAGES
    results = {}

    click.echo("\nCompiling...")
    for lang in selected:
        compile_benchmark("for_loop", lang)
    click.echo("Done.\n")

    click.echo("Running benchmarks...")
    for lang in selected:
        run_benchmark("for_loop", lang)  # warm-up run, not measured
        times = []
        for _ in range(runs):
            times.append(run_benchmark("for_loop", lang))
        results[lang] = times
    click.echo("Done.\n")

    sorted_langs = sorted(results, key=lambda l: sum(results[l]) / len(results[l]))

    click.echo(f"{'Language':<10} {'Run':<5} {'Time (s)':<12}")
    click.echo("-" * 30)
    for lang in sorted_langs:
        for r, elapsed in enumerate(results[lang], 1):
            click.echo(f"{lang:<10} {r:<5} {elapsed:<12.4f}")

    if runs > 1:
        click.echo("\n" + "-" * 30)
        click.echo(f"{'Language':<10} {'Avg (s)':<12}")
        click.echo("-" * 30)
        for lang in sorted_langs:
            avg = sum(results[lang]) / len(results[lang])
            click.echo(f"{lang:<10} {avg:<12.4f}")

    click.echo()


if __name__ == "__main__":
    cli()
