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

### Run all benchmarks

```sh
python bench.py for-loop
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

```
python bench.py for-loop --help
```

| Flag              | Description                                                  |
|-------------------|--------------------------------------------------------------|
| `-l`, `--languages` | Languages to benchmark (repeatable). Defaults to all.      |
| `-r`, `--runs`      | Number of measured runs. Default: 1.                        |
| `--skip-first`      | Exclude the first run from averages and the HTML report.    |
| `--html`            | Path to write the HTML report to.                           |

## Benchmarks

### for-loop

A simple summation loop running 10,000,000 iterations. Each language's source lives in its own directory (e.g. `python/for_loop.py`, `rust/for_loop.rs`). Compiled languages output their binaries into a `<lang>/build/` directory, which is git-ignored.

## Adding a new benchmark

1. Add the source file in the appropriate language directory.
2. Add a new entry under `BENCHMARKS` in `bench.py` with `compile` and `run` commands.
3. Add a new `@cli.command()` function in `bench.py` that calls `compile_benchmark` and `run_benchmark`, then displays results and optionally calls `generate_html`.
