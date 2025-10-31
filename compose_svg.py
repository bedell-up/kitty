#!/usr/bin/env python3
"""
compose_svg.py — builds the SVG representation of the Kitty CRISPR cat
based on its trait values.

Called by generate_cat.py
"""

from pathlib import Path

CANVAS_W, CANVAS_H = 800, 480

# Basic color + shape libraries for each trait
COLORS = {
    "body": {"Striped": "#d68a39", "Gray": "#999999"},
    "eyes": {"Green Eyes": "#54ff75", "Blue Eyes": "#3a7bff"},
    "pattern": {"Spotted": "spots", "Solid": "solid"},
}

TAILS = {
    "Long Tail": "<rect x='515' y='270' width='70' height='15' rx='7' ry='7' fill='{color}'/>",
    "Short Tail": "<rect x='515' y='270' width='30' height='15' rx='7' ry='7' fill='{color}'/>",
}

EARS = {
    "Pointy Ears": """
        <polygon points='360,160 380,130 390,160' fill='{color}'/>
        <polygon points='440,160 420,130 410,160' fill='{color}'/>""",
    "Rounded Ears": """
        <ellipse cx='370' cy='145' rx='10' ry='15' fill='{color}'/>
        <ellipse cx='430' cy='145' rx='10' ry='15' fill='{color}'/>""",
}


def compose_svg(trait_values: dict, caption: str) -> str:
    """Return a full SVG string for the cat based on resolved traits."""

    body_color = COLORS["body"].get(trait_values.get("A"), "#aaaaaa")
    eye_color = COLORS["eyes"].get(trait_values.get("B"), "#66ccff")
    tail_shape = TAILS.get(trait_values.get("C"), TAILS["Short Tail"])
    ear_shape = EARS.get(trait_values.get("D"), EARS["Pointy Ears"])
    pattern_type = COLORS["pattern"].get(trait_values.get("E"), "solid")

    # Simple pattern overlay (optional spots)
    pattern_layer = ""
    if pattern_type == "spots":
        pattern_layer = "".join(
            f"<circle cx='{x}' cy='{y}' r='8' fill='rgba(0,0,0,0.2)'/>"
            for x, y in [(370, 310), (420, 320), (390, 340), (410, 285)]
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}">
      <rect width="100%" height="100%" fill="#222"/>
      <text x="{CANVAS_W/2}" y="50" font-size="28" text-anchor="middle" fill="white">{caption}</text>

      <!-- Body -->
      <ellipse cx="400" cy="300" rx="120" ry="70" fill="{body_color}"/>

      <!-- Head -->
      <circle cx="400" cy="200" r="50" fill="{body_color}"/>
      <circle cx="380" cy="190" r="8" fill="{eye_color}"/>
      <circle cx="420" cy="190" r="8" fill="{eye_color}"/>

      <!-- Ears -->
      {ear_shape.format(color=body_color)}

      <!-- Tail -->
      {tail_shape.format(color=body_color)}

      <!-- Pattern -->
      {pattern_layer}

      <!-- Ground -->
      <rect y="400" width="100%" height="80" fill="#333"/>
    </svg>"""

    return svg


if __name__ == "__main__":
    # Example standalone test
    traits = {
        "A": "Striped",
        "B": "Green Eyes",
        "C": "Long Tail",
        "D": "Pointy Ears",
        "E": "Spotted",
    }
    svg_str = compose_svg(traits, "Test Cat — Manual Compose")
    Path("output/test_cat.svg").write_text(svg_str)
    print("✅ Wrote output/test_cat.svg")
