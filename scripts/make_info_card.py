import os
import sys

def generate_info_card(output_path="info-card.svg"):
    is_static = os.environ.get("STATIC") == "1"
    
    width = 490
    height = 360

    # Custom Info Card data from user
    info_rows = [
        ("Name", "Kishalay Das"),
        ("Role", "Developer & Open-Source Contributor"),
        ("Focus", "Architecting MVPs & Rapid Execution"),
        ("Languages", "C++, Python, JS/TS, Java, Kotlin, C#"),
        ("Frameworks", "React, React Native, Node.js, PyTorch"),
        ("Databases", "MongoDB, Supabase, MySQL")
    ]

    css_anim = ""
    if not is_static:
        css_anim = """
    .animate-row {
      opacity: 0;
      animation: fadeInUp 0.5s ease-out forwards;
    }
    @keyframes fadeInUp {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    """

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <style>
    .bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1px; rx: 10px; ry: 10px; }}
    .dot-red {{ fill: #ff5f56; }}
    .dot-yellow {{ fill: #ffbd2e; }}
    .dot-green {{ fill: #27c93f; }}
    .window-title {{ font-family: "Fira Code", "Cascadia Code", monospace; font-size: 12px; fill: #8b949e; font-weight: 600; }}
    .header-name {{ font-family: "Fira Code", "Cascadia Code", monospace; font-size: 16px; fill: #58a6ff; font-weight: bold; }}
    .header-host {{ font-family: "Fira Code", "Cascadia Code", monospace; font-size: 16px; fill: #8b949e; }}
    .separator {{ font-family: "Fira Code", "Cascadia Code", monospace; font-size: 13px; fill: #30363d; }}
    .label {{ font-family: "Fira Code", "Cascadia Code", monospace; font-size: 12px; fill: #79c0ff; font-weight: bold; }}
    .val {{ font-family: "Fira Code", "Cascadia Code", monospace; font-size: 12px; fill: #c9d1d9; }}
    {css_anim}
  </style>

  <!-- Background Card -->
  <rect class="bg" width="{width}" height="{height}" />

  <!-- Top Title Bar -->
  <path d="M 0,10 A 10,10 0 0,1 10,0 L {width-10},0 A 10,10 0 0,1 {width},10 L {width},36 L 0,36 Z" fill="#161b22" />
  <line x1="0" y1="36" x2="{width}" y2="36" stroke="#30363d" stroke-width="1" />
  
  <!-- Window Control Buttons -->
  <circle cx="20" cy="18" r="6" class="dot-red" />
  <circle cx="40" cy="18" r="6" class="dot-yellow" />
  <circle cx="60" cy="18" r="6" class="dot-green" />
  
  <!-- Window Title -->
  <text x="{width // 2}" y="22" text-anchor="middle" class="window-title">bhaikd@github ~ whoami</text>

  <!-- Content Rows -->
  <g transform="translate(22, 65)">
    <!-- Header row -->
    <g class="{'' if is_static else 'animate-row'}" style="animation-delay: 0.1s;">
      <text x="0" y="0">
        <tspan class="header-name">Kishalay Das</tspan><tspan class="header-host"> (bhaikd)</tspan>
      </text>
    </g>

    <!-- Separator -->
    <g class="{'' if is_static else 'animate-row'}" style="animation-delay: 0.2s;">
      <text x="0" y="18" class="separator">------------------------------------------</text>
    </g>

    <!-- Key/Value Rows -->
"""

    y_offset = 44
    delay = 0.3
    for key, val in info_rows:
        escaped_val = val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        anim_class = "" if is_static else "animate-row"
        delay_str = f'style="animation-delay: {delay:.2f}s;"' if not is_static else ""
        svg_content += f"""    <g class="{anim_class}" {delay_str}>
      <text x="0" y="{y_offset}">
        <tspan class="label">{key:11s}</tspan> <tspan class="val">{escaped_val}</tspan>
      </text>
    </g>
"""
        y_offset += 32
        delay += 0.15

    # Color palette footer blocks like neofetch
    anim_class = "" if is_static else "animate-row"
    delay_str = f'style="animation-delay: {delay:.2f}s;"' if not is_static else ""
    svg_content += f"""    <g class="{anim_class}" {delay_str}>
      <g transform="translate(0, {y_offset + 5})">
        <rect x="0" y="0" width="22" height="14" fill="#484f58" rx="3" />
        <rect x="28" y="0" width="22" height="14" fill="#ff7b72" rx="3" />
        <rect x="56" y="0" width="22" height="14" fill="#3fb950" rx="3" />
        <rect x="84" y="0" width="22" height="14" fill="#d29922" rx="3" />
        <rect x="112" y="0" width="22" height="14" fill="#58a6ff" rx="3" />
        <rect x="140" y="0" width="22" height="14" fill="#bc8cff" rx="3" />
        <rect x="168" y="0" width="22" height="14" fill="#39c5cf" rx="3" />
        <rect x="196" y="0" width="22" height="14" fill="#b1bac4" rx="3" />
      </g>
    </g>
  </g>
</svg>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print(f"Neofetch Info Card SVG generated -> '{output_path}' (static={is_static})")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "info-card.svg"
    generate_info_card(out_file)
