#!/usr/bin/env python3
"""
Data-to-Charts: Automatically generate publication-quality figures from experimental data.

Supports CSV and JSON inputs. Intelligently infers chart type from data structure
to produce training curves, comparison bar charts, ablation studies, and more.

Usage:
    python data_to_charts.py data.csv --output-dir ./charts
    python data_to_charts.py data.json --output-dir ./charts --dpi 300

Dependencies:
    pandas, matplotlib, numpy
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# =============================================================================
# SCI Paper Color Palette (Colorblind-safe)
# =============================================================================
COLORS = {
    'blue': '#377EB8',
    'red': '#E41A1C',
    'green': '#4DAF4A',
    'purple': '#984EA3',
    'orange': '#FF7F00',
    'gray': '#999999',
    'dark': '#333333',
    'lightgray': '#CCCCCC',
}

PALETTE = [COLORS['blue'], COLORS['red'], COLORS['green'],
           COLORS['purple'], COLORS['orange'], COLORS['gray']]

# =============================================================================
# Matplotlib Global Settings for SCI Papers
# =============================================================================
plt.rcParams.update({
    'font.size': 10,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.transparent': True,
    'savefig.bbox': 'tight',
    'axes.spines.top': False,
    'axes.spines.right': False,
})


def load_data(filepath):
    """Load data from CSV or JSON file."""
    ext = Path(filepath).suffix.lower()
    if ext == '.csv':
        import pandas as pd
        return pd.read_csv(filepath)
    elif ext in ('.json', '.jsonl'):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, dict) and 'data' in data:
            import pandas as pd
            return pd.DataFrame(data['data'])
        elif isinstance(data, list):
            import pandas as pd
            return pd.DataFrame(data)
        else:
            raise ValueError("Unsupported JSON structure. Expected {'data': [...]} or [...]")
    else:
        raise ValueError(f"Unsupported file format: {ext}. Use .csv or .json")


def infer_chart_type(df):
    """Intelligently infer the most appropriate chart type from DataFrame structure."""
    cols = list(df.columns)
    n_cols = len(cols)
    n_rows = len(df)

    # Check for training curve pattern: has epoch/step/iteration + loss/accuracy/reward
    step_keywords = ['epoch', 'step', 'iteration', 'episode', 'batch', 'time',
                     'cycle', 'run', 'trial', 'sample', 'index', 'point']
    metric_keywords = ['loss', 'accuracy', 'acc', 'reward', 'error', 'score',
                       'precision', 'recall', 'f1', 'mAP', 'bleu', 'rouge',
                       # Battery / materials domain
                       'capacity', 'conductivity', 'efficiency', 'voltage', 'current',
                       'resistance', 'impedance', 'density', 'energy', 'power',
                       'cycle', 'lifetime', 'retention', 'stability', 'degradation',
                       'fade', 'gap', 'overpotential', 'polarization', 'diffusion',
                       'coefficient', 'rate', 'velocity', 'speed', 'torque',
                       'force', 'stress', 'strain', 'temperature', 'pressure']

    step_col = None
    for kw in step_keywords:
        matches = [c for c in cols if kw.lower() in c.lower()]
        if matches:
            step_col = matches[0]
            break

    metric_cols = []
    for kw in metric_keywords:
        matches = [c for c in cols if kw.lower() in c.lower()]
        metric_cols.extend(matches)

    if step_col and metric_cols:
        if n_rows >= 50:  # Long time series = training curve
            return 'training_curve', {'step_col': step_col, 'metric_cols': metric_cols}

    # Check for comparison pattern: first col = category/label, rest = numeric metrics
    if n_cols >= 2:
        first_col = cols[0]
        # If first col looks like categorical labels
        if df[first_col].dtype == object or df[first_col].nunique() <= min(20, n_rows):
            rest_numeric = all(df[c].dtype in (np.float64, np.int64, np.float32, np.int32)
                               for c in cols[1:])
            if rest_numeric:
                if 'ablation' in first_col.lower() or 'variant' in first_col.lower() or 'config' in first_col.lower():
                    return 'ablation_bar', {'label_col': first_col, 'value_cols': cols[1:]}
                return 'comparison_bar', {'label_col': first_col, 'value_cols': cols[1:]}

    # Check for scatter/plot pattern: two numeric columns
    numeric_cols = [c for c in cols if df[c].dtype in (np.float64, np.int64, np.float32, np.int32)]
    if len(numeric_cols) >= 2:
        return 'scatter', {'x_col': numeric_cols[0], 'y_col': numeric_cols[1]}

    # Default: line plot of all numeric columns
    return 'line', {'cols': numeric_cols if numeric_cols else cols}


def generate_training_curve(df, step_col, metric_cols, output_path, title=None):
    """Generate training curves (loss/accuracy over epochs)."""
    n_metrics = len(metric_cols)
    if n_metrics == 1:
        fig, ax = plt.subplots(figsize=(5, 3.5))
        axes = [ax]
    else:
        fig, axes = plt.subplots(1, min(n_metrics, 3), figsize=(5 * min(n_metrics, 3), 3.5))
        if n_metrics == 1:
            axes = [axes]
        else:
            axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]

    x = df[step_col].values

    for idx, metric_col in enumerate(metric_cols[:len(axes)]):
        ax = axes[idx]
        y = df[metric_col].values

        # Smooth curve
        window = min(50, max(5, len(y) // 20))
        if len(y) > window:
            y_smooth = np.convolve(y, np.ones(window)/window, mode='valid')
            x_smooth = x[window-1:]
        else:
            y_smooth = y
            x_smooth = x

        ax.plot(x, y, color=COLORS['lightgray'], linewidth=0.8, alpha=0.4, label='Raw')
        ax.plot(x_smooth, y_smooth, color=COLORS['blue'], linewidth=2, label='Smoothed')
        ax.fill_between(x_smooth, y_smooth * 0.98, y_smooth * 1.02,
                        color=COLORS['blue'], alpha=0.08)

        ax.set_xlabel(step_col.replace('_', ' ').title())
        ax.set_ylabel(metric_col.replace('_', ' ').title())
        chart_title = title or f"{metric_col.replace('_', ' ').title()} vs {step_col.replace('_', ' ').title()}"
        ax.set_title(chart_title, fontweight='bold')
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"  [Training Curve] Saved: {output_path}")
    return output_path


def generate_comparison_bar(df, label_col, value_cols, output_path, title=None):
    """Generate comparison bar chart."""
    labels = df[label_col].astype(str).tolist()
    n_groups = len(labels)
    n_bars = len(value_cols)

    fig, ax = plt.subplots(figsize=(max(6, n_groups * 1.2), 4))

    x = np.arange(n_groups)
    width = 0.7 / n_bars
    multiplier = 0

    # Detect "Ours" row for highlighting
    ours_idx = None
    for i, lbl in enumerate(labels):
        if 'ours' in lbl.lower() or 'our' in lbl.lower():
            ours_idx = i
            break

    for idx, col in enumerate(value_cols):
        offset = width * multiplier
        values = df[col].values
        color = PALETTE[idx % len(PALETTE)]
        bars = ax.bar(x + offset, values, width, label=col.replace('_', ' ').title(),
                      color=color, edgecolor='white', linewidth=0.5)

        # Add value labels on bars
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(values)*0.01,
                   f'{val:.1f}', ha='center', va='bottom', fontsize=7.5)
        multiplier += 1

    ax.set_xlabel(label_col.replace('_', ' ').title(), fontweight='bold')
    ax.set_ylabel('Value', fontweight='bold')
    ax.set_title(title or f"Comparison: {', '.join(value_cols)}", fontweight='bold')
    ax.set_xticks(x + width * (n_bars - 1) / 2)
    ax.set_xticklabels(labels, fontsize=9)
    ax.legend(loc='best', ncols=min(n_bars, 3), fontsize=8, framealpha=0.9)
    ax.grid(axis='y', alpha=0.3)

    # Highlight "Ours" row
    if ours_idx is not None:
        for bar in ax.containers:
            if hasattr(bar, '__iter__'):
                for b in bar:
                    if abs(b.get_x() + b.get_width()/2 - (x[ours_idx] + width * (n_bars - 1) / 2)) < 0.5:
                        b.set_edgecolor(COLORS['blue'])
                        b.set_linewidth(2)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"  [Comparison Bar] Saved: {output_path}")
    return output_path


def generate_ablation_bar(df, label_col, value_cols, output_path, title=None):
    """Generate ablation study bar chart with baseline comparison."""
    labels = df[label_col].astype(str).tolist()
    n_groups = len(labels)

    fig, ax = plt.subplots(figsize=(max(6, n_groups * 1.0), 4))

    # Detect baseline and "ours"
    baseline_idx = None
    ours_idx = None
    for i, lbl in enumerate(labels):
        l = lbl.lower()
        if 'baseline' in l or 'vanilla' in l or 'standard' in l:
            baseline_idx = i
        if 'full' in l or 'ours' in l or 'our' in l:
            ours_idx = i

    # Use first value column for ablation
    col = value_cols[0]
    values = df[col].values

    colors = []
    for i in range(n_groups):
        if i == ours_idx:
            colors.append(COLORS['blue'])
        elif i == baseline_idx:
            colors.append(COLORS['red'])
        else:
            colors.append(COLORS['purple'])

    bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=0.5)

    # Add reference lines
    if ours_idx is not None:
        ax.axhline(y=values[ours_idx], color=COLORS['blue'], linewidth=1, linestyle='--', alpha=0.6)
    if baseline_idx is not None:
        ax.axhline(y=values[baseline_idx], color=COLORS['red'], linewidth=1, linestyle='--', alpha=0.6)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(values)*0.01,
               f'{val:.1f}', ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    ax.set_ylabel(col.replace('_', ' ').title(), fontsize=10)
    ax.set_title(title or f"Ablation Study: {col.replace('_', ' ').title()}", fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"  [Ablation Bar] Saved: {output_path}")
    return output_path


def generate_scatter(df, x_col, y_col, output_path, title=None):
    """Generate scatter plot with optional trend line."""
    fig, ax = plt.subplots(figsize=(5, 4))

    x = df[x_col].values
    y = df[y_col].values

    ax.scatter(x, y, c=COLORS['blue'], s=80, alpha=0.6, edgecolors='white', linewidth=1.5)

    # Add trend line
    if len(x) > 2:
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        x_line = np.linspace(x.min(), x.max(), 100)
        ax.plot(x_line, p(x_line), color=COLORS['red'], linewidth=1.5,
                linestyle='--', label=f'Trend: y={z[0]:.3f}x+{z[1]:.3f}')
        ax.legend(fontsize=8)

    ax.set_xlabel(x_col.replace('_', ' ').title(), fontsize=10)
    ax.set_ylabel(y_col.replace('_', ' ').title(), fontsize=10)
    ax.set_title(title or f"{y_col.replace('_', ' ').title()} vs {x_col.replace('_', ' ').title()}", fontweight='bold')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"  [Scatter] Saved: {output_path}")
    return output_path


def generate_line(df, cols, output_path, title=None):
    """Generate multi-line plot."""
    fig, ax = plt.subplots(figsize=(6, 4))

    for idx, col in enumerate(cols):
        y = df[col].values
        x = np.arange(len(y))
        color = PALETTE[idx % len(PALETTE)]
        ax.plot(x, y, color=color, linewidth=2, label=col.replace('_', ' ').title())

    ax.set_xlabel('Index', fontsize=10)
    ax.set_ylabel('Value', fontsize=10)
    ax.set_title(title or "Data Overview", fontweight='bold')
    ax.legend(loc='best', fontsize=8, framealpha=0.9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"  [Line Plot] Saved: {output_path}")
    return output_path


def process_file(filepath, output_dir, title=None):
    """Process a single data file and generate appropriate chart(s)."""
    print(f"\nProcessing: {filepath}")

    df = load_data(filepath)
    print(f"  Columns: {list(df.columns)}")
    print(f"  Rows: {len(df)}")

    chart_type, params = infer_chart_type(df)
    print(f"  Inferred chart type: {chart_type}")

    basename = Path(filepath).stem
    output_path = os.path.join(output_dir, f"{basename}_{chart_type}.png")

    if chart_type == 'training_curve':
        return generate_training_curve(df, **params, output_path=output_path, title=title)
    elif chart_type == 'comparison_bar':
        return generate_comparison_bar(df, **params, output_path=output_path, title=title)
    elif chart_type == 'ablation_bar':
        return generate_ablation_bar(df, **params, output_path=output_path, title=title)
    elif chart_type == 'scatter':
        return generate_scatter(df, **params, output_path=output_path, title=title)
    elif chart_type == 'line':
        return generate_line(df, **params, output_path=output_path, title=title)


def main():
    parser = argparse.ArgumentParser(description='Generate SCI-quality charts from experimental data')
    parser.add_argument('files', nargs='+', help='Input CSV/JSON files')
    parser.add_argument('--output-dir', '-o', default='./charts', help='Output directory')
    parser.add_argument('--title', '-t', default=None, help='Chart title override')
    parser.add_argument('--dpi', type=int, default=300, help='Output DPI')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    plt.rcParams['savefig.dpi'] = args.dpi

    results = []
    for filepath in args.files:
        if not os.path.exists(filepath):
            print(f"Error: File not found: {filepath}")
            continue
        try:
            result = process_file(filepath, args.output_dir, title=args.title)
            results.append(result)
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*50}")
    print(f"Generated {len(results)} chart(s) in: {args.output_dir}")
    for r in results:
        print(f"  - {os.path.basename(r)}")


if __name__ == '__main__':
    main()
