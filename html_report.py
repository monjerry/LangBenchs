"""Generates a standalone HTML report with a Chart.js bar chart for benchmark results."""

import json

LANG_COLORS: dict[str, str] = {
    "c++": "#f0ad4e",
    "go": "#5bc0de",
    "java": "#d9534f",
    "node": "#5cb85c",
    "python": "#3572A5",
    "rust": "#e8522a",
}


def _build_datasets(results: dict[str, list[float]], sorted_langs: list[str], colors: list[str]) -> str:
    """Build the Chart.js datasets JSON string.

    Single run produces one dataset with per-language colors.
    Multiple runs produce one dataset per run with borders matching language colors.
    """
    num_runs = len(next(iter(results.values())))

    if num_runs == 1:
        return json.dumps([{
            "label": "Time (s)",
            "data": [round(results[l][0], 4) for l in sorted_langs],
            "backgroundColor": colors,
        }])

    datasets: list[dict] = []
    for r in range(num_runs):
        datasets.append({
            "label": f"Run {r + 1}",
            "data": [round(results[l][r], 4) for l in sorted_langs],
            "backgroundColor": [c + "cc" for c in colors],
            "borderColor": colors,
            "borderWidth": 1,
        })
    return json.dumps(datasets)


def generate_html(benchmark_name: str, results: dict[str, list[float]], sorted_langs: list[str], output_path: str) -> None:
    """Generate a self-contained HTML file with a bar chart of the benchmark results.

    Args:
        benchmark_name: Name of the benchmark (used as the page title).
        results: Map of language name to list of measured times in seconds.
        sorted_langs: Language names in the order they should appear (fastest first).
        output_path: File path where the HTML report will be written.
    """
    colors = [LANG_COLORS.get(l, "#999999") for l in sorted_langs]
    datasets_js = _build_datasets(results, sorted_langs, colors)
    num_runs = len(next(iter(results.values())))
    show_legend = "true" if num_runs > 1 else "false"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Benchmark: {benchmark_name}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    max-width: 800px;
    margin: 60px auto;
    padding: 0 20px;
    background: #f5f5f5;
    color: #333;
  }}
  h1 {{ text-align: center; }}
  .chart-container {{
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    padding: 24px;
  }}
</style>
</head>
<body>
<h1>{benchmark_name.replace("_", " ").title()}</h1>
<div class="chart-container">
  <canvas id="chart"></canvas>
</div>
<script>
const ctx = document.getElementById("chart").getContext("2d");
new Chart(ctx, {{
  type: "bar",
  data: {{
    labels: {json.dumps(sorted_langs)},
    datasets: {datasets_js},
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ display: {show_legend} }},
      title: {{
        display: true,
        text: "Duration in seconds (lower is faster)",
        font: {{ size: 14 }},
      }},
    }},
    scales: {{
      y: {{
        beginAtZero: true,
        title: {{ display: true, text: "Time (s)" }},
      }},
    }},
  }},
}});
</script>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)
