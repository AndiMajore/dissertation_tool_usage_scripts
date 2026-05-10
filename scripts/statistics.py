import os,sys
import pandas as pd
import re
import matplotlib.pyplot as plt
from collections import Counter
import matplotlib.colors as mcolors
from pathlib import Path

output_dir = Path("../output")
output_dir.mkdir(parents=True, exist_ok=True)
BASE_DIR="../logs/"
BASE_TOOLS = ["drugstone", "epistasis-disease-atlas", "digest", "nedrex-web"]

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
    filename = parts[-1]
    if "-access-filtered.log" in filename:
        filename = filename.replace('-access-filtered.log', '')
    if "-access.log" in filename:
        filename = filename.replace('-access.log', '')

    if folder == "apps":
        folder = ""
    return f"{folder}-{filename}" if folder else filename


def analyze_everything():
    """Extracts hits and unique visitor arrivals in one single pass.
       Builds both component-level and deduplicated aggregated datasets."""

    component_stats = {}
    aggregated_stats = {}
    all_months = set()

    agg_ip_first_seen = {base: {} for base in BASE_TOOLS}
    agg_hits = {base: Counter() for base in BASE_TOOLS}

    for log_suffix in lognames:
        full_path = os.path.join(BASE_DIR, log_suffix)
        if not os.path.exists(full_path): continue

        tool_name = get_tool_name(log_suffix)
        component_stats[tool_name] = {'hits': Counter(), 'new_uniques': Counter()}
        comp_ip_first_seen = {}

        matched_base = None
        for base in BASE_TOOLS:
            if base in tool_name:
                matched_base = base
                break

        if not matched_base and tool_name.startswith("app-"):
            parts = tool_name.split("-")
            if len(parts) >= 2:
                matched_base = f"{parts[0]}-{parts[1]}"

        target_agg = matched_base if matched_base else tool_name

        if target_agg not in agg_ip_first_seen:
            agg_ip_first_seen[target_agg] = {}
            agg_hits[target_agg] = Counter()

        print(f"\t\tReading: {tool_name} (Aggregating to: {target_agg})...")
        with open(full_path, 'r') as f:
            for line in f:
                match = LOG_PATTERN.match(line)
                if match:
                    ip = match.group(1)
                    month_str = f"{match.group(3)}-{MONTH_MAP[match.group(2)]}"
                    all_months.add(month_str)

                    component_stats[tool_name]['hits'][month_str] += 1
                    if ip not in comp_ip_first_seen or month_str < comp_ip_first_seen[ip]:
                        comp_ip_first_seen[ip] = month_str

                    agg_hits[target_agg][month_str] += 1
                    if ip not in agg_ip_first_seen[target_agg] or month_str < agg_ip_first_seen[target_agg][ip]:
                        agg_ip_first_seen[target_agg][ip] = month_str

        for first_month in comp_ip_first_seen.values():
            component_stats[tool_name]['new_uniques'][first_month] += 1

    for agg_key, ip_dict in agg_ip_first_seen.items():
        if sum(agg_hits[agg_key].values()) == 0:
            continue

        aggregated_stats[agg_key] = {'hits': agg_hits[agg_key], 'new_uniques': Counter()}
        for first_month in ip_dict.values():
            aggregated_stats[agg_key]['new_uniques'][first_month] += 1

    timeline = sorted(list(all_months))
    return component_stats, aggregated_stats, timeline

def get_master_color_map(tool_names):
    """Assigns consistent colors to tools once."""
    color_map = {}
    colored_tools = sorted([t for t in tool_names if not t.startswith("app-")])
    palette = list(mcolors.TABLEAU_COLORS.values()) + list(mcolors.XKCD_COLORS.values())

    for i, tool in enumerate(tool_names):
        if tool.startswith("app-"):
            color_map[tool] = "#d3d3d3"  # Consistent Gray
        else:
            idx = colored_tools.index(tool)
            color_map[tool] = palette[idx % len(palette)]
    return color_map


def plot_double_figure_equal_content(component_stats, aggregated_stats, timeline, color_map, output_dir,
                                     figure_name="usage_statistics", metric="unique"):
    fig, (ax_1, ax_2) = plt.subplots(2, 1, figsize=(18, 22))
    fig.subplots_adjust(hspace=0.3)

    figure_name_full = f"{figure_name}_{metric}"

    base_colors = {
        "drugstone": "#9B5C97",
        "epistasis-disease-atlas": "#C03830",
        "digest": "#155289",
        "nedrex-web": "#489FA7"
    }
    line_styles = ['-', '--', '-.', ':']

    def get_view_data(mode):
        if mode == "aggregated":
            return aggregated_stats
        elif mode == "components":
            return component_stats
        return component_stats

    for (ax, view_mode, letter) in [(ax_1, "aggregated", "A"),(ax_2, "components", "B")]:

        view_data = get_view_data(view_mode)
        style_tracker = {key: 0 for key in base_colors.keys()}
        metric_key = 'hits' if metric == "requests" else 'new_uniques'

        sorted_tools = sorted(view_data.keys(), key=lambda t: sum(view_data[t][metric_key].values()), reverse=True)

        for tool in sorted_tools:
            if metric == "requests":
                values = [view_data[tool][metric_key].get(m, 0) for m in timeline]
                total_val = sum(values)
            else:
                values = []
                running_total = 0
                for m in timeline:
                    running_total += view_data[tool][metric_key].get(m, 0)
                    values.append(running_total)
                total_val = values[-1] if len(values) > 0 else 0

            formatted_label = f"{tool} ({total_val:,})"
            is_app = tool.startswith("app-")
            clean_tool_name = tool.replace(" (TOTAL)", "")

            plot_color = color_map.get(clean_tool_name, '#CCCCCC')
            plot_linestyle = '-'
            # Slightly bumped line widths to match the larger text
            lw = 1.5 if is_app else 3.0
            z_ord = 1 if is_app else 2
            alpha_val = 0.6 if is_app else 0.9

            if not is_app:
                for base_app, b_color in base_colors.items():
                    if base_app in clean_tool_name:
                        plot_color = b_color
                        if view_mode == "aggregated":
                            plot_linestyle = '-'
                            lw = 4.5 # Bolder master line
                            z_ord = 3
                            alpha_val = 1.0
                        else:
                            plot_linestyle = line_styles[(style_tracker[base_app] + 1) % len(line_styles)]
                            style_tracker[base_app] += 1
                        break

            ax.plot(
                timeline, values, label=formatted_label,
                color=plot_color, linestyle=plot_linestyle,
                alpha=alpha_val, linewidth=lw,
                zorder=z_ord, marker='.', markersize=5 if is_app else 8
            )

        if metric == "requests":
            ax.set_yscale('log')
            # Increased Y-label font
            ax.set_ylabel("Hits per Month (log scale)", fontsize=24)
            ax.grid(True, which='minor', axis='y', linestyle=':', alpha=0.10)

            if view_mode == "aggregated":
                plot_title = "Monthly Total Requests (Aggregated Main Tools)"
            else:
                plot_title = "Monthly Total Requests (Individual Components)"
        else:
            # Increased Y-label font
            ax.set_ylabel("Total Unique IPs", fontsize=24)

            if view_mode == "aggregated":
                plot_title = "Cumulative Unique Visitors (Aggregated Main Tools)"
            else:
                plot_title = "Cumulative Unique Visitors (Individual Components)"

        # Increased title and tick labels
        ax.set_title(plot_title, fontsize=30, pad=20, fontweight='500')
        ax.tick_params(axis='both', which='major', labelsize=20)

        xticks_pos = range(0, len(timeline), 2 if len(timeline) > 20 else 1)
        xticks_labels = timeline[::2 if len(timeline) > 20 else 1]
        ax.set_xticks(xticks_pos)
        ax.set_xticklabels(xticks_labels, rotation=45, ha='right')

        # Scaled up the panel letters (A, B)
        ax.text(-0.06, 1.05, letter, transform=ax.transAxes, fontsize=50, fontweight='bold', va='top', ha='right')

        ax.grid(True, which='major', axis='y', linestyle='-', alpha=0.15)
        for spine in ['top', 'right']: ax.spines[spine].set_visible(False)
        for spine in ['left', 'bottom']: ax.spines[spine].set_color('#555555')

        # Scaled up legend text and title
        ax.legend(bbox_to_anchor=(1.02, 0.5), loc='center left', fontsize=18, ncol=2, frameon=False,
                  labelspacing=0.9, title=f"Tools (Sorted by Total {metric.title()})", title_fontsize=22,
                  handlelength=2.5,
                  alignment='left')
        ax.get_legend().get_title().set_ha("left")

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    file_path = out_path / f"{figure_name_full}.png"

    fig.savefig(
        file_path,
        format='png',
        dpi=600,
        bbox_inches='tight',
        transparent=True
    )
    plt.close(fig)
# def plot_combined_figure(component_stats, aggregated_stats, timeline, color_map, output_dir,
#                          figure_name="usage_statistics_combined",
#                          hits_view_mode="both", uniques_view_mode="both"):
#     """
#     view_mode options:
#     - "aggregated": Shows only the massive parent tools.
#     - "components": Shows only the individual sub-components.
#     - "both": Shows sub-components (dashed) AND the parent total (thick solid line).
#     """
#
#     # FIX 1 & 3: Make the figure taller and use the constrained layout engine
#     fig, (ax2, ax1) = plt.subplots(2, 1, figsize=(18, 24), layout='constrained')
#
#     base_colors = {
#         "drugstone": "#9B5C97",
#         "epistasis-disease-atlas": "#C03830",
#         "digest": "#155289",
#         "nedrex-web": "#489FA7"
#     }
#     line_styles = ['-', '--', '-.', ':']
#
#     def get_view_data(mode):
#         if mode == "aggregated":
#             return aggregated_stats
#         elif mode == "components":
#             return component_stats
#         elif mode == "both":
#             combined = {}
#             for k, v in component_stats.items():
#                 combined[k] = v
#             for k, v in aggregated_stats.items():
#                 combined[f"{k} (TOTAL)"] = v
#             return combined
#         return component_stats
#
#     # ---------------------------------------------------------
#     # PLOT 1 (Bottom): HITS
#     # ---------------------------------------------------------
#     hits_data = get_view_data(hits_view_mode)
#     style_tracker_a = {key: 0 for key in base_colors.keys()}
#
#     sorted_tools_hits = sorted(hits_data.keys(), key=lambda t: sum(hits_data[t]['hits'].values()), reverse=True)
#
#     for tool in sorted_tools_hits:
#         values = [hits_data[tool]['hits'].get(m, 0) for m in timeline]
#         total_val = sum(values)
#         formatted_label = f"{tool} ({total_val:,})"
#
#         is_app = tool.startswith("app-")
#         is_total = "(TOTAL)" in tool
#         clean_tool_name = tool.replace(" (TOTAL)", "")
#
#         plot_color = color_map.get(clean_tool_name, '#CCCCCC')
#         plot_linestyle = '-'
#         lw = 1.0 if is_app else 2.0
#         z_ord = 1 if is_app else 2
#         alpha_val = 0.6 if is_app else 0.9
#
#         if not is_app:
#             for base_app, b_color in base_colors.items():
#                 if base_app in clean_tool_name:
#                     plot_color = b_color
#
#                     if is_total or hits_view_mode == "aggregated":
#                         plot_linestyle = '-'
#                         lw = 3.5 if is_total else 2.5
#                         z_ord = 3
#                         alpha_val = 1.0
#                     else:
#                         plot_linestyle = line_styles[(style_tracker_a[base_app] + 1) % len(line_styles)]
#                         style_tracker_a[base_app] += 1
#                     break
#
#         ax1.plot(
#             timeline, values, label=formatted_label,
#             color=plot_color, linestyle=plot_linestyle,
#             alpha=alpha_val, linewidth=lw,
#             zorder=z_ord, marker='.', markersize=3 if is_app else 5
#         )
#
#     ax1.set_yscale('log')
#     ax1.set_title("Monthly Total Requests (Hits)", fontsize=22, pad=20, fontweight='500')
#     ax1.set_ylabel("Hits per Month (log scale)", fontsize=16)
#     ax1.tick_params(axis='both', which='major', labelsize=14)
#
#     xticks_pos = range(0, len(timeline), 2 if len(timeline) > 20 else 1)
#     xticks_labels = timeline[::2 if len(timeline) > 20 else 1]
#     ax1.set_xticks(xticks_pos)
#     ax1.set_xticklabels(xticks_labels, rotation=45, ha='right')
#
#     ax1.text(-0.06, 1.05, 'B', transform=ax1.transAxes, fontsize=36, fontweight='bold', va='top', ha='right')
#
#     ax1.grid(True, which='major', axis='y', linestyle='-', alpha=0.15)
#     ax1.grid(True, which='minor', axis='y', linestyle=':', alpha=0.10)
#     for spine in ['top', 'right']: ax1.spines[spine].set_visible(False)
#     for spine in ['left', 'bottom']: ax1.spines[spine].set_color('#555555')
#
#     ax1.legend(bbox_to_anchor=(1.02, 0.5), loc='center left', fontsize='small', ncol=2, frameon=False,
#                labelspacing=0.9, title="Tools (Sorted by Total Hits)", title_fontsize='medium', handlelength=2.5,
#                alignment='left')
#     ax1.get_legend().get_title().set_ha("left")
#
#     # ---------------------------------------------------------
#     # PLOT 2 (Top): CUMULATIVE UNIQUE VISITORS
#     # ---------------------------------------------------------
#     uniques_data = get_view_data(uniques_view_mode)
#     style_tracker_b = {key: 0 for key in base_colors.keys()}
#
#     sorted_tools_cum = sorted(uniques_data.keys(), key=lambda t: sum(uniques_data[t]['new_uniques'].values()),
#                               reverse=True)
#
#     for tool in sorted_tools_cum:
#         values = []
#         running_total = 0
#         for m in timeline:
#             running_total += uniques_data[tool]['new_uniques'].get(m, 0)
#             values.append(running_total)
#         total_val = running_total
#
#         formatted_label = f"{tool} ({total_val:,})"
#
#         is_app = tool.startswith("app-")
#         is_total = "(TOTAL)" in tool
#         clean_tool_name = tool.replace(" (TOTAL)", "")
#
#         plot_color = color_map.get(clean_tool_name, '#CCCCCC')
#         plot_linestyle = '-'
#         lw = 1.0 if is_app else 2.0
#         z_ord = 1 if is_app else 2
#         alpha_val = 0.6 if is_app else 0.9
#
#         if not is_app:
#             for base_app, b_color in base_colors.items():
#                 if base_app in clean_tool_name:
#                     plot_color = b_color
#
#                     if is_total or uniques_view_mode == "aggregated":
#                         plot_linestyle = '-'
#                         lw = 3.5 if is_total else 2.5
#                         z_ord = 3
#                         alpha_val = 1.0
#                     else:
#                         plot_linestyle = line_styles[(style_tracker_b[base_app] + 1) % len(line_styles)]
#                         style_tracker_b[base_app] += 1
#                     break
#
#         ax2.plot(
#             timeline, values, label=formatted_label,
#             color=plot_color, linestyle=plot_linestyle,
#             alpha=alpha_val, linewidth=lw,
#             zorder=z_ord, marker='.', markersize=3 if is_app else 5
#         )
#
#     ax2.set_title("Cumulative Unique Visitors", fontsize=22, pad=20, fontweight='500')
#     ax2.set_ylabel("Total Unique IPs", fontsize=16)
#     ax2.tick_params(axis='both', which='major', labelsize=14)
#
#     ax2.set_xticks(xticks_pos)
#     ax2.set_xticklabels(xticks_labels, rotation=45, ha='right')
#
#     ax2.text(-0.06, 1.05, 'A', transform=ax2.transAxes, fontsize=36, fontweight='bold', va='top', ha='right')
#
#     ax2.grid(True, which='major', axis='y', linestyle='-', alpha=0.15)
#     for spine in ['top', 'right']: ax2.spines[spine].set_visible(False)
#     for spine in ['left', 'bottom']: ax2.spines[spine].set_color('#555555')
#
#     ax2.legend(bbox_to_anchor=(1.02, 0.5), loc='center left', fontsize='small', ncol=2, frameon=False,
#                labelspacing=0.9, title="Tools (Sorted by Total Uniques)", title_fontsize='medium', handlelength=2.5,
#                alignment='left')
#     ax2.get_legend().get_title().set_ha("left")
#
#     out_path = Path(output_dir)
#     out_path.mkdir(parents=True, exist_ok=True)
#     file_path = out_path / f"{figure_name}.png"
#
#     plt.savefig(
#         file_path,
#         format='png',
#         dpi=600,
#         bbox_inches='tight',
#         transparent=True
#     )
#     plt.close()

print("Creating summary figure for unique visits and absolute number of requests...")

print("\tReading filtered logs...")
comp_stats, agg_stats, timeline = analyze_everything()
all_tool_names = list(comp_stats.keys()) + list(agg_stats.keys())
colors = get_master_color_map(all_tool_names)
print("\t...Done")

print("\tGenerating Combined Publication Figure...")
# plot_combined_figure(
#     component_stats=comp_stats,
#     aggregated_stats=agg_stats,
#     timeline=timeline,
#     color_map=colors,
#     output_dir=output_dir,
#     figure_name="figure-usage_statistics_combined_both",
#     hits_view_mode="both",  # CHANGE THIS TO "aggregated", "components", or "both"
#     uniques_view_mode="both"  # CHANGE THIS TO "aggregated", "components", or "both"
# )
plot_double_figure_equal_content(
    component_stats=comp_stats,
    aggregated_stats=agg_stats,
    timeline=timeline,
    color_map=colors,
    output_dir=output_dir,
    figure_name="figure-usage_statistics",
    metric="unique"
)
plot_double_figure_equal_content(
    component_stats=comp_stats,
    aggregated_stats=agg_stats,
    timeline=timeline,
    color_map=colors,
    output_dir=output_dir,
    figure_name="figure-usage_statistics",
    metric="requests"
)
print("\t...Done")
print(f"Figures saved as {output_dir}/figure-usage_statistics_*.png")

# Optional: Run again for the unfiltered set if needed.
print("Creating summary figure for unique visits and absolute number of requests for NON-FILTERED logs...")
print("\tReading non-filtered logs...")
comp_stats, agg_stats, timeline = analyze_everything()
all_tool_names = list(comp_stats.keys()) + list(agg_stats.keys())
colors = get_master_color_map(all_tool_names)
print("\t...Done")

print("\tGenerating Combined Publication Figure without filters...")
plot_double_figure_equal_content(
    component_stats=comp_stats,
    aggregated_stats=agg_stats,
    timeline=timeline,
    color_map=colors,
    output_dir=output_dir,
    figure_name="figure-usage_statistics-unfiltered",
    metric="unique"
)
plot_double_figure_equal_content(
    component_stats=comp_stats,
    aggregated_stats=agg_stats,
    timeline=timeline,
    color_map=colors,
    output_dir=output_dir,
    figure_name="figure-usage_statistics-unfiltered",
    metric="requests"
)
print("\t...Done")
print(f"Figures saved as {output_dir}/figure-usage_statistics-unfiltered*.png")