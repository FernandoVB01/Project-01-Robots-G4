#!/usr/bin/env python3
"""Plot Gazebo telemetry and write the values used by the IEEE paper."""

import argparse
import csv
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'ackermann_challenger_control'))
from ackermann_challenger_control.geometry import Course  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path, help='Folder with tracking.csv and summary.json')
    parser.add_argument('output', type=Path, help='Output folder for plots and values')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.run / 'tracking.csv').open(newline='') as stream:
        data = [{key: float(value) for key, value in row.items()}
                for row in csv.DictReader(stream)]
    stats = json.loads((args.run / 'summary.json').read_text())
    if stats['status'] != 'completed' or len(data) != stats['samples']:
        parser.error('The run must have a complete, matching CSV and summary.')

    plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False,
                         'pdf.fonttype': 42, 'figure.dpi': 180})
    ref_x, ref_y = zip(*Course().points)
    fig, ax = plt.subplots(figsize=(3.44, 3.0), layout='constrained')
    ax.plot(ref_x, ref_y, '--', color='#bd5432', linewidth=1.6, label='Reference')
    ax.plot([r['x_m'] for r in data], [r['y_m'] for r in data],
            color='#136a78', linewidth=1.1, label='Gazebo')
    ax.plot(data[0]['x_m'], data[0]['y_m'], 'o', color='#142c3c', markersize=3)
    ax.set(xlabel='X position (m)', ylabel='Y position (m)', aspect='equal')
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.grid(alpha=0.24)
    ax.legend(frameon=False, loc='center', fontsize=8)
    save(fig, args.output / 'trajectory')

    fig, ax = plt.subplots(figsize=(3.44, 1.72), layout='constrained')
    ax.plot([r['time_s'] for r in data], [r['error_m'] * 100 for r in data],
            color='#136a78', linewidth=1.0)
    ax.axhline(stats['rmse_m'] * 100, linestyle='--', linewidth=1, color='#bd5432')
    ax.set(xlabel='Elapsed simulation time (s)', ylabel='Error (cm)', ylim=(0, None))
    ax.grid(alpha=0.24)
    save(fig, args.output / 'tracking_error')

    values = {
        'RouteLength': f'{stats["reference_length_m"]:.2f}',
        'RunDuration': f'{stats["simulated_duration_s"]:.2f}',
        'RunSamples': str(stats['samples']),
        'RunRMSE': f'{100 * stats["rmse_m"]:.2f}',
        'RunMax': f'{100 * stats["max_error_m"]:.2f}',
        'RunFinal': f'{100 * stats["endpoint_error_m"]:.2f}',
        'RunProgress': f'{stats["station_m"]:.2f}',
    }
    (args.output / 'run_values.tex').write_text(''.join(
        '\\newcommand{\\' + name + '}{' + value + '}\n' for name, value in values.items()
    ))
    (args.output / 'chart_data.json').write_text(json.dumps({
        'reference': Course().points[::6],
        'observed': [[r['x_m'], r['y_m']] for r in data[::4]],
        'error': [[r['time_s'], 100 * r['error_m']] for r in data[::4]],
        'statistics': stats,
    }))


def save(fig, path):
    for extension in ('pdf', 'png'):
        fig.savefig(path.with_suffix(f'.{extension}'), dpi=240)
    plt.close(fig)


if __name__ == '__main__':
    main()
