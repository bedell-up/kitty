def g(content: str, shadow=False) -> str:
    """Wrap an SVG element group, with optional drop shadow filter."""
    if shadow:
        return '<g filter="url(#shadow)">' + content + "</g>\n"
    else:
        return "<g>" + content + "</g>\n"


def build_cat_svg(traits, caption="Custom Kitty") -> str:
    """
    traits: dict like {"A": "long", "B": "floppy", "C": "bob", "D": "spots", "E": "green"}
    caption: string displayed at the top
    Returns full SVG string.
    """

    svg = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="320" viewBox="0 0 480 320">',
        "<defs>",
        '<filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">'
        '<feDropShadow dx="3" dy="3" stdDeviation="3" flood-color="#444" flood-opacity="0.4"/>'
        "</filter>",
        "</defs>",
        '<rect width="100%" height="100%" fill="#f5efe6"/>',
    ]

    # --- Title / caption ---
    svg.append(
        f'<text x="50%" y="35" font-size="18" text-anchor="middle" '
        f'font-family="Verdana" fill="#333">{caption}</text>'
    )

    # --- Base body ---
    body = '<ellipse cx="240" cy="200" rx="90" ry="60" fill="#f1d3b3" stroke="#7b5c3e" stroke-width="3"/>'
    head = '<circle cx="240" cy="120" r="45" fill="#f1d3b3" stroke="#7b5c3e" stroke-width="3"/>'
    svg.append(g(body + head, shadow=True))

    # --- Ears ---
    ear_type = traits.get("B", "pointed")
    if ear_type == "floppy":
        ears = (
            '<path d="M200 70 Q180 90 200 110" fill="none" stroke="#7b5c3e" stroke-width="6"/>'
            '<path d="M280 70 Q300 90 280 110" fill="none" stroke="#7b5c3e" stroke-width="6"/>'
        )
    else:
        ears = (
            '<polygon points="200,70 180,100 220,95" fill="#f1d3b3" stroke="#7b5c3e" stroke-width="3"/>'
            '<polygon points="280,70 300,100 260,95" fill="#f1d3b3" stroke="#7b5c3e" stroke-width="3"/>'
        )
    svg.append(g(ears))

    # --- Eyes ---
    eye_color = traits.get("E", "green")
    eye_fill = "#6cc24a" if "green" in eye_color else "#4aa3f1"
    eyes = (
        f'<ellipse cx="225" cy="120" rx="8" ry="10" fill="{eye_fill}" stroke="#000"/>'
        f'<ellipse cx="255" cy="120" rx="8" ry="10" fill="{eye_fill}" stroke="#000"/>'
    )
    svg.append(g(eyes))

    # --- Tail ---
    tail_type = traits.get("C", "long")
    if tail_type == "bob":
        tail = '<circle cx="330" cy="210" r="15" fill="#f1d3b3" stroke="#7b5c3e" stroke-width="3"/>'
    else:
        tail = (
            '<path d="M320 210 q40 -10 60 20" fill="none" stroke="#7b5c3e" stroke-width="10" stroke-linecap="round"/>'
        )
    svg.append(g(tail, shadow=True))

    # --- Fur length (mane) ---
    fur = traits.get("A", "short")
    if fur == "long":
        mane = (
            '<path d="M195 130 q45 30 90 0" fill="none" stroke="#7b5c3e" stroke-width="5"/>'
            '<path d="M190 140 q50 35 100 0" fill="none" stroke="#7b5c3e" stroke-width="4"/>'
        )
        svg.append(g(mane))

    # --- Pattern ---
    pattern = traits.get("D", "none")
    if "spot" in pattern:
        spots = (
            '<circle cx="230" cy="200" r="8" fill="#7b5c3e"/>'
            '<circle cx="255" cy="215" r="6" fill="#7b5c3e"/>'
            '<circle cx="245" cy="185" r="5" fill="#7b5c3e"/>'
        )
        svg.append(g(spots))
    elif "stripe" in pattern:
        stripes = "".join([f'<rect x="{200 + i*15}" y="160" width="6" height="60" fill="#7b5c3e"/>' for i in range(4)])
        svg.append(g(stripes))

    # --- Nose & mouth ---
    face = (
        '<circle cx="240" cy="135" r="3" fill="#000"/>'
        '<path d="M240 138 q-5 8 -10 10" stroke="#000" fill="none" stroke-width="1.5"/>'
        '<path d="M240 138 q5 8 10 10" stroke="#000" fill="none" stroke-width="1.5"/>'
    )
    svg.append(g(face))

    # --- Closing ---
    svg.append("</svg>")
    return "\n".join(svg)
