# Language Benchmarks

A CLI tool for running performance benchmarks across multiple programming languages and generating HTML reports with charts.

## Supported Languages

| Language | Type         |
|----------|--------------|
| C++      | Compiled     |
| Go       | Compiled     |
| Java     | Compiled     |
| Rust     | Compiled     |
| Node.js  | Interpreted  |
| Python   | Interpreted  |

## Setup

Create and activate the conda environment:

```sh
conda create -n benchmarks
conda activate benchmarks
```

```sh
pip install -r requirements.txt
```

## Usage

### Run a benchmark

```sh
python bench.py for-loop
python bench.py monte-carlo
```

### Select specific languages

```sh
python bench.py for-loop -l python -l rust -l go
```

### Multiple runs with averages

```sh
python bench.py for-loop --runs 5
```

### Drop the first run (cold-start)

The first run of compiled languages often includes process startup overhead. Use `--skip-first` to exclude it from averages and the HTML report — it will still be displayed in the terminal output, marked as skipped.

```sh
python bench.py for-loop --runs 3 --skip-first
```

### Generate an HTML report

Produces a standalone HTML file with an overview chart and a per-language breakdown, both powered by Chart.js.

```sh
python bench.py for-loop --runs 3 --skip-first --html results.html
```

### All options

Every benchmark command shares the same set of flags:

```
python bench.py <benchmark> --help
```

| Flag              | Description                                                  |
|-------------------|--------------------------------------------------------------|
| `-l`, `--languages` | Languages to benchmark (repeatable). Defaults to all.      |
| `-r`, `--runs`      | Number of measured runs. Default: 1.                        |
| `--skip-first`      | Exclude the first run from averages and the HTML report.    |
| `--html`            | Path to write the HTML report to.                           |

## Benchmarks

### for-loop

A simple summation loop running 10,000,000 iterations.

### monte-carlo

Estimates pi using the Monte Carlo method: 10,000,000 random (x, y) points are generated inside a unit square and the fraction that land inside the unit circle is used to approximate pi. Each language uses a seeded PRNG so runs are reproducible. Rust uses a custom xorshift64 implementation to avoid external crates; the other languages use their standard-library PRNGs.

---

Each language's source lives in its own directory (e.g. `python/for_loop.py`, `rust/monte_carlo.rs`). Compiled languages output their binaries into a `<lang>/build/` directory, which is git-ignored.

## Adding a new benchmark

1. Add the source file in the appropriate language directory.
2. Add a new entry under `BENCHMARKS` in `bench.py` with `compile` and `run` commands for each language.
3. Add a new `@cli.command()` decorated with `@_benchmark_options` in `bench.py` that calls `_execute_benchmark` with the benchmark name.
