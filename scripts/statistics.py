import os,sys
import pandas as pd
import re
import matplotlib.pyplot as plt
from datetime import datetime
import subprocess
from collections import Counter
import matplotlib.colors as mcolors
from pathlib import Path

# 1. Define your output directory and ensure it exists
output_dir = Path("../output")
output_dir.mkdir(parents=True, exist_ok=True)
BASE_DIR="../logs/"

lognames = set()
for file in os.listdir(BASE_DIR):
    for app in os.listdir(BASE_DIR+file):
        if "access-filtered.log" in app:
            lognames.add(f"{file}/{app}")
MONTH_MAP = {
    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
}

LOG_PATTERN = re.compile(r'^([\d\.]+) - - \[\d{2}/(\w{3})/(\d{4})')


def get_tool_name(log_suffix):
    """Naming logic matching your latest preference."""
    parts = log_suffix.split('/')
    folder = parts[-2] if len(parts) > 1 else ""
    filename = parts[-1].replace('-access-filtered.log', '')
    if folder == "apps":
        folder = ""
    return f"{folder}-{filename}" if folder else filename


def analyze_everything():
    """Extracts hits and unique visitor arrivals in one single pass."""
    tool_stats = {}  # tool -> {'hits': Counter(), 'new_uniques': Counter()}
    all_months = set()

    for log_suffix in lognames:
        full_path = os.path.join(BASE_DIR, log_suffix)
        if not os.path.exists(full_path): continue

        tool_name = get_tool_name(log_suffix)
        tool_stats[tool_name] = {'hits': Counter(), 'new_uniques': Counter()}

        ip_first_seen = {}  # Track first appearance of IP for this tool

        print(f"\t\tReading: {tool_name}...")
        with open(full_path, 'r') as f:
            for line in f:
                match = LOG_PATTERN.match(line)
                if match:
                    ip = match.group(1)
                    month_str = f"{match.group(3)}-{MONTH_MAP[match.group(2)]}"
                    all_months.add(month_str)

                    # 1. Total Hits
                    tool_stats[tool_name]['hits'][month_str] += 1

                    # 2. Track when this IP first appeared
                    if ip not in ip_first_seen or month_str < ip_first_seen[ip]:
                        ip_first_seen[ip] = month_str

        # After reading the file, convert 'first seen' dates into monthly arrival counts
        for first_month in ip_first_seen.values():
            tool_stats[tool_name]['new_uniques'][first_month] += 1

    timeline = sorted(list(all_months))
    return tool_stats, timeline


def get_master_color_map(tool_names):
    """Assigns consistent colors to tools once."""
    color_map = {}
    # Filter out app- tools for coloring, sort to ensure consistent assignment
    colored_tools = sorted([t for t in tool_names if not t.startswith("app-")])
    palette = list(mcolors.TABLEAU_COLORS.values()) + list(mcolors.XKCD_COLORS.values())

    for i, tool in enumerate(tool_names):
        if tool.startswith("app-"):
            color_map[tool] = "#d3d3d3"  # Consistent Gray
        else:
            # Match tool to color based on its sorted position in 'colored_tools'
            idx = colored_tools.index(tool)
            color_map[tool] = palette[idx % len(palette)]
    return color_map


def plot_combined_figure(tool_stats, timeline, color_map, output_dir, figure_name="usage_statistics_combined"):
    fig, (ax2, ax1) = plt.subplots(2, 1, figsize=(16, 20))

    base_colors = {
        "drugstone": "#9B5C97",
        "epistasis-disease-atlas": "#C03830",
        "digest": "#155289",
        "nedrex-web": "#489FA7"
    }
    line_styles = ['-', '--', '-.', ':']

    style_tracker_a = {key: 0 for key in base_colors.keys()}
    sorted_tools_hits = sorted(tool_stats.keys(), key=lambda t: sum(tool_stats[t]['hits'].values()), reverse=True)

    for tool in sorted_tools_hits:
        values = [tool_stats[tool]['hits'].get(m, 0) for m in timeline]
        total_val = sum(values)
        formatted_label = f"{tool} ({total_val:,})"
        is_app = tool.startswith("app-")
        plot_color = color_map.get(tool, '#CCCCCC')
        plot_linestyle = '-'

        if not is_app:
            for base_app, b_color in base_colors.items():
                if tool.startswith(base_app):
                    plot_color = b_color
                    plot_linestyle = line_styles[style_tracker_a[base_app] % len(line_styles)]
                    style_tracker_a[base_app] += 1
                    break

        ax1.plot(
            timeline, values, label=formatted_label,
            color=plot_color, linestyle=plot_linestyle,
            alpha=0.6 if is_app else 0.9, linewidth=1.0 if is_app else 2.0,
            zorder=1 if is_app else 2, marker='.', markersize=3 if is_app else 5
        )

    ax1.set_yscale('log')
    ax1.set_title("Monthly Total Requests (Hits)", fontsize=22, pad=20, fontweight='500')
    ax1.set_ylabel("Hits per Month (log scale)", fontsize=16)
    ax1.tick_params(axis='both', which='major', labelsize=14)

    xticks_pos = range(0, len(timeline), 2 if len(timeline) > 20 else 1)
    xticks_labels = timeline[::2 if len(timeline) > 20 else 1]
    ax1.set_xticks(xticks_pos)
    ax1.set_xticklabels(xticks_labels, rotation=45, ha='right')

    ax1.text(-0.06, 1.05, 'B', transform=ax1.transAxes, fontsize=36, fontweight='bold', va='top', ha='right')

    ax1.grid(True, which='major', axis='y', linestyle='-', alpha=0.15)
    ax1.grid(True, which='minor', axis='y', linestyle=':', alpha=0.10)
    for spine in ['top', 'right']: ax1.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']: ax1.spines[spine].set_color('#555555')

    ax1.legend(bbox_to_anchor=(1.02, 0.5), loc='center left', fontsize='small', ncol=1, frameon=False,
               labelspacing=0.9, title="Tools (Sorted by Total Hits)", title_fontsize='medium', handlelength=2.5, alignment='left')
    ax1.get_legend().get_title().set_ha("left")

    style_tracker_b = {key: 0 for key in base_colors.keys()}  # Reset tracker for second plot
    sorted_tools_cum = sorted(tool_stats.keys(), key=lambda t: sum(tool_stats[t]['new_uniques'].values()), reverse=True)

    for tool in sorted_tools_cum:
        values = []
        running_total = 0
        for m in timeline:
            running_total += tool_stats[tool]['new_uniques'].get(m, 0)
            values.append(running_total)
        total_val = running_total

        formatted_label = f"{tool} ({total_val:,})"
        is_app = tool.startswith("app-")
        plot_color = color_map.get(tool, '#CCCCCC')
        plot_linestyle = '-'

        if not is_app:
            for base_app, b_color in base_colors.items():
                if tool.startswith(base_app):
                    plot_color = b_color
                    plot_linestyle = line_styles[style_tracker_b[base_app] % len(line_styles)]
                    style_tracker_b[base_app] += 1
                    break

        ax2.plot(
            timeline, values, label=formatted_label,
            color=plot_color, linestyle=plot_linestyle,
            alpha=0.6 if is_app else 0.9, linewidth=1.0 if is_app else 2.0,
            zorder=1 if is_app else 2, marker='.', markersize=3 if is_app else 5
        )

    ax2.set_title("Cumulative Unique Visitors", fontsize=22, pad=20, fontweight='500')
    ax2.set_ylabel("Total Unique IPs", fontsize=16)
    ax2.tick_params(axis='both', which='major', labelsize=14)

    ax2.set_xticks(xticks_pos)
    ax2.set_xticklabels(xticks_labels, rotation=45, ha='right')

    ax2.text(-0.06, 1.05, 'A', transform=ax2.transAxes, fontsize=36, fontweight='bold', va='top', ha='right')

    ax2.grid(True, which='major', axis='y', linestyle='-', alpha=0.15)
    for spine in ['top', 'right']: ax2.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']: ax2.spines[spine].set_color('#555555')

    ax2.legend(bbox_to_anchor=(1.02, 0.5), loc='center left', fontsize='small', ncol=1, frameon=False,
               labelspacing=0.9, title="Tools (Sorted by Total Uniques)", title_fontsize='medium', handlelength=2.5, alignment='left')
    ax2.get_legend().get_title().set_ha("left")

    plt.tight_layout(pad=4.0)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    file_path = out_path / f"{figure_name}.png"

    plt.savefig(
        file_path,
        format='png',
        dpi=600,
        bbox_inches='tight',
        transparent=True
    )
    plt.close()

print("Creating summary figure for unique visits and absolute number of requests...")

print("\tReading filtered logs...")
stats, timeline = analyze_everything()
colors = get_master_color_map(list(stats.keys()))
print("\t...Done")

print("\tGenerating Combined Publication Figure...")
plot_combined_figure(
    tool_stats=stats,
    timeline=timeline,
    color_map=colors,
    output_dir=output_dir,
    figure_name="figure-usage_statistics_combined"
)
print("\t...Done")
print("Figure safed as ../output/figure-usage_statistics_combined.png")