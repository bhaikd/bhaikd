import os
import sys
import json
from datetime import datetime, timedelta

PALETTE = [
    "#161b22",  # Level 0 (None)
    "#0e4429",  # Level 1
    "#006d32",  # Level 2
    "#26a641",  # Level 3
    "#39d353",  # Level 4
    "#69f0a0"   # Level 5 (Neon top end)
]

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

def render_heatmap_svg(json_path="data/contributions.json", output_path="contrib-heatmap.svg"):
    if not os.path.exists(json_path):
        print(f"Error: JSON data file '{json_path}' not found.")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    days = data.get("days", [])
    total_contributions = data.get("total_contributions", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)
    username = data.get("username", "bhaikd")

    svg_w = 860
    svg_h = 205

    cell_size = 10.5
    cell_gap = 3.2
    step = cell_size + cell_gap # ~13.7px per column

    grid_x = 42
    grid_y = 48

    # Process days into 53 weeks x 7 rows
    # We group by week columns (col 0 to 52)
    weeks = [[] for _ in range(53)]
    
    # Organize days into columns
    if days:
        # Determine day of week for first date
        first_date = datetime.strptime(days[0]["date"], "%Y-%m-%d")
        # Python weekday: Mon=0..Sun=6. Standard GitHub grid: Sun=0..Sat=6
        # Convert: (weekday + 1) % 7 -> Sun=0, Mon=1...
        start_wday = (first_date.weekday() + 1) % 7
        
        current_col = 0
        current_wday = start_wday
        
        for d in days:
            if current_wday > 6:
                current_wday = 0
                current_col += 1
            
            if current_col < 53:
                weeks[current_col].append((current_wday, d))
            
            current_wday += 1

    # Find month label positions
    month_labels = []
    last_month = None
    for c, week in enumerate(weeks):
        for wday, d in week:
            dt = datetime.strptime(d["date"], "%Y-%m-%d")
            if dt.month != last_month and d["date"][-2:] in ["01", "02", "03", "04", "05", "06", "07"]:
                month_labels.append((c, MONTH_NAMES[dt.month - 1]))
                last_month = dt.month
                break

    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    svg_parts.append('  <style>')
    svg_parts.append('    .bg { fill: #0d1117; stroke: #30363d; stroke-width: 1px; rx: 10px; ry: 10px; }')
    svg_parts.append('    .title { font-family: "Fira Code", monospace; font-size: 13px; fill: #58a6ff; font-weight: bold; }')
    svg_parts.append('    .subtitle { font-family: "Fira Code", monospace; font-size: 12px; fill: #8b949e; }')
    svg_parts.append('    .lbl { font-family: "Fira Code", monospace; font-size: 10px; fill: #7d8590; }')
    svg_parts.append('    .stats-txt { font-family: "Fira Code", monospace; font-size: 11px; fill: #c9d1d9; font-weight: 500; }')
    svg_parts.append('    .highlight { fill: #39d353; font-weight: bold; }')
    svg_parts.append('    .cell { rx: 2px; ry: 2px; opacity: 0; animation: slideDown 0.35s ease-out forwards; }')
    svg_parts.append('    @keyframes slideDown {')
    svg_parts.append('      from { opacity: 0; transform: translateY(-6px); }')
    svg_parts.append('      to { opacity: 1; transform: translateY(0); }')
    svg_parts.append('    }')
    svg_parts.append('  </style>')

    # Background card
    svg_parts.append(f'  <rect class="bg" width="{svg_w}" height="{svg_h}" />')

    # Card Title
    svg_parts.append(f'  <text x="20" y="26" class="title">bhaikd<tspan class="subtitle"> / contribution-graph</tspan></text>')

    # Month Labels
    for col_idx, m_name in month_labels:
        x = grid_x + col_idx * step
        svg_parts.append(f'  <text x="{x:.1f}" y="{grid_y - 8}" class="lbl">{m_name}</text>')

    # Day of week labels (Mon, Wed, Fri)
    for wday_idx, name in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = grid_y + wday_idx * step + cell_size - 2
        svg_parts.append(f'  <text x="18" y="{y:.1f}" class="lbl">{name}</text>')

    # Render Grid Cells
    for c, week in enumerate(weeks):
        for wday, d in week:
            x = grid_x + c * step
            y = grid_y + wday * step
            lvl = max(0, min(5, d.get("level", 0)))
            fill_color = PALETTE[lvl]
            cnt = d.get("count", 0)
            date_str = d.get("date", "")
            
            # Staggered animation delay based on diagonal (col + row)
            delay = (c + wday) * 0.015
            
            tooltip = f"{cnt} contributions on {date_str}"
            svg_parts.append(f'  <rect class="cell" x="{x:.1f}" y="{y:.1f}" width="{cell_size}" height="{cell_size}" fill="{fill_color}" style="animation-delay: {delay:.3f}s;">')
            svg_parts.append(f'    <title>{tooltip}</title>')
            svg_parts.append('  </rect>')

    # Stats Footer Bar (Left)
    footer_y = grid_y + 7 * step + 22
    stats_str = f"{total_contributions:,} contributions in the last year | Current Streak: {current_streak} days | Longest: {longest_streak} days"
    svg_parts.append(f'  <text x="20" y="{footer_y}" class="stats-txt">{stats_str}</text>')

    # Less -> More Legend (Right)
    legend_x = svg_w - 170
    svg_parts.append(f'  <g transform="translate({legend_x}, {footer_y - 10})">')
    svg_parts.append('    <text x="0" y="9" class="lbl">Less</text>')
    for idx, color in enumerate(PALETTE):
        lx = 28 + idx * 14
        svg_parts.append(f'    <rect x="{lx}" y="0" width="10" height="10" rx="2" ry="2" fill="{color}" />')
    svg_parts.append(f'    <text x="{28 + len(PALETTE) * 14 + 4}" y="9" class="lbl">More</text>')
    svg_parts.append('  </g>')

    svg_parts.append('</svg>')

    svg_out = "\n".join(svg_parts)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_out)

    print(f"Heatmap SVG rendered successfully -> '{output_path}'")

if __name__ == "__main__":
    jpath = sys.argv[1] if len(sys.argv) > 1 else "data/contributions.json"
    opath = sys.argv[2] if len(sys.argv) > 2 else "contrib-heatmap.svg"
    render_heatmap_svg(jpath, opath)
