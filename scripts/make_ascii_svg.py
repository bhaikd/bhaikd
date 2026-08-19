import os
import sys
import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"  # Bright (sparse/space) -> dark (dense/@)

def image_to_ascii(img_path, target_width=100):
    if not os.path.exists(img_path):
        print(f"Error: Input image '{img_path}' not found.")
        sys.exit(1)

    img = Image.open(img_path).convert("L")
    w, h = img.size
    
    # Monospace font aspect ratio adjustment (~0.5 aspect ratio: width/height)
    aspect_ratio = h / float(w)
    target_height = int(target_width * aspect_ratio * 0.52)
    
    img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    arr = np.array(img_resized)

    ascii_lines = []
    ramp_len = len(RAMP)
    
    for row in arr:
        line_chars = []
        for pixel in row:
            # 255 is white -> space (RAMP[0]), 0 is black -> @ (RAMP[-1])
            idx = int((255 - pixel) / 255.0 * (ramp_len - 1))
            idx = max(0, min(ramp_len - 1, idx))
            line_chars.append(RAMP[idx])
        ascii_lines.append("".join(line_chars))

    return ascii_lines, target_width, target_height

def generate_ascii_svg(ascii_lines, cols, rows, output_svg="rik-ascii.svg"):
    char_w = 6.2
    char_h = 11.5
    svg_w = int(cols * char_w + 30)
    svg_h = int(rows * char_h + 30)

    total_anim_duration = 3.5  # total seconds for whole portrait typing
    row_dur = total_anim_duration / rows

    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    svg_parts.append('  <style>')
    svg_parts.append('    .bg { fill: #0d1117; rx: 10px; ry: 10px; }')
    svg_parts.append('    .ascii-text { font-family: "Fira Code", "Cascadia Code", "Courier New", monospace; font-size: 9.5px; fill: #8b949e; white-space: pre; }')
    svg_parts.append('    .cursor { fill: #58a6ff; }')
    svg_parts.append('  </style>')
    
    # Background card
    svg_parts.append(f'  <rect class="bg" width="{svg_w}" height="{svg_h}" />')

    # Definitions for row clip-paths and animations
    svg_parts.append('  <defs>')
    for r in range(rows):
        y_pos = r * char_h + 15
        start_delay = r * row_dur
        svg_parts.append(f'    <clipPath id="clip-row-{r}">')
        svg_parts.append(f'      <rect x="15" y="{y_pos:.1f}" width="0" height="{char_h:.1f}">')
        svg_parts.append(f'        <animate attributeName="width" from="0" to="{cols * char_w:.1f}" begin="{start_delay:.2f}s" dur="{row_dur:.2f}s" fill="freeze" />')
        svg_parts.append('      </rect>')
        svg_parts.append('    </clipPath>')
    svg_parts.append('  </defs>')

    # Render text lines with clip-path
    svg_parts.append('  <g class="ascii-text">')
    for r, line in enumerate(ascii_lines):
        y_pos = r * char_h + 23  # text baseline
        # Escape XML special chars
        escaped_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        svg_parts.append(f'    <text x="15" y="{y_pos:.1f}" clip-path="url(#clip-row-{r})">{escaped_line}</text>')
    
    # Typing cursor that moves down the portrait
    for r in range(rows):
        y_pos = r * char_h + 15
        start_delay = r * row_dur
        svg_parts.append(f'    <rect class="cursor" y="{y_pos:.1f}" height="{char_h:.1f}" width="7">')
        svg_parts.append(f'      <animate attributeName="x" from="15" to="{15 + cols * char_w:.1f}" begin="{start_delay:.2f}s" dur="{row_dur:.2f}s" fill="freeze" />')
        svg_parts.append(f'      <animate attributeName="opacity" values="1;1;0" keyTimes="0;0.95;1" begin="{start_delay:.2f}s" dur="{row_dur:.2f}s" fill="freeze" />')
        svg_parts.append('    </rect>')
    
    svg_parts.append('  </g>')
    svg_parts.append('</svg>')

    svg_content = "\n".join(svg_parts)
    with open(output_svg, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print(f"ASCII SVG art generated successfully -> '{output_svg}' ({cols}x{rows})")

if __name__ == "__main__":
    img_file = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
    out_svg = sys.argv[2] if len(sys.argv) > 2 else "rik-ascii.svg"
    
    if not os.path.exists(img_file):
        print(f"File '{img_file}' not found. Generating a default test ASCII SVG...")
        # Create a dummy image if source photo does not exist yet
        dummy_img = Image.new("L", (100, 100), color=255)
        # Draw a simple circle in dummy image
        from PIL import ImageDraw
        draw = ImageDraw.Draw(dummy_img)
        draw.ellipse((20, 20, 80, 80), fill=50)
        dummy_img.save("source-prepped.png")
        img_file = "source-prepped.png"
        
    lines, w, h = image_to_ascii(img_file, target_width=52)
    generate_ascii_svg(lines, w, h, output_svg=out_svg)
