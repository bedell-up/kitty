#!/usr/bin/env python3
import os, json, argparse, base64
from datetime import datetime
from pathlib import Path

# --- Optional OpenAI (AI image gen) ---
_USE_AI = bool(os.getenv("OPENAI_API_KEY"))
if _USE_AI:
    try:
        from openai import OpenAI

        _openai_client = OpenAI()  # key read from env
    except Exception:
        _USE_AI = False  # fall back if client import fails

# --- Fallback SVG -> PNG ---
import cairosvg

from config import CUSTOMER_TEMPLATES, TRAITS

# Optional external SVG composer; otherwise we use an internal one.
try:
    from compose_svg import compose_svg as _compose_svg
except Exception:
    _compose_svg = None

# --- Output paths ---
OUT_DIR = Path("output")
SVG_PATH = OUT_DIR / "cat.svg"
PNG_PATH = OUT_DIR / "cat.png"
JSON_PATH = OUT_DIR / "cat_of_the_day.json"
OUT_DIR.mkdir(exist_ok=True)

# -----------------------------------------------------------
# Helpers
# -----------------------------------------------------------


def resolve_trait_labels(state: dict):
    """Convert genotype {'A':'dom'/'rec',...} -> human-readable trait labels using TRAITS."""
    labels = {}
    for trait in TRAITS:
        gene = trait["slot"]
        val = state.get(gene, "rec")
        labels[gene] = trait["dominant"] if val == "dom" else trait["recessive"]
    return labels


def _fallback_build_svg(trait_values: dict, caption: str) -> str:
    """Simple built-in SVG (used if compose_svg.py not present)."""
    body_color = "orange" if trait_values.get("A") == "Striped" else "gray"
    eye_color = "green" if trait_values.get("B") == "Green Eyes" else "blue"
    tail_shape = "long" if trait_values.get("C") == "Long Tail" else "stubby"
    ear_type = "pointy" if trait_values.get("D") == "Pointy Ears" else "rounded"
    pattern = "spots" if trait_values.get("E") == "Spotted" else "solid"

    ear_left = (
        "<polygon points='360,160 380,130 390,160' fill='{color}'/>"
        if ear_type == "pointy"
        else "<ellipse cx='370' cy='145' rx='10' ry='15' fill='{color}'/>"
    ).format(color=body_color)
    ear_right = (
        "<polygon points='440,160 420,130 410,160' fill='{color}'/>"
        if ear_type == "pointy"
        else "<ellipse cx='430' cy='145' rx='10' ry='15' fill='{color}'/>"
    ).format(color=body_color)
    tail = (
        "<rect x='515' y='270' width='70' height='15' rx='7' ry='7' fill='{color}'/>"
        if tail_shape == "long"
        else "<rect x='515' y='270' width='30' height='15' rx='7' ry='7' fill='{color}'/>"
    ).format(color=body_color)

    pattern_layer = ""
    if pattern == "spots":
        dots = [(360, 300), (385, 320), (410, 305), (395, 340), (430, 330)]
        pattern_layer = "".join(f"<circle cx='{x}' cy='{y}' r='8' fill='rgba(0,0,0,0.25)'/>" for x, y in dots)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="480">
      <rect width="100%" height="100%" fill="#222"/>
      <text x="400" y="50" font-size="28" text-anchor="middle" fill="white">{caption}</text>
      <ellipse cx="400" cy="300" rx="120" ry="70" fill="{body_color}"/>
      <circle cx="400" cy="200" r="50" fill="{body_color}"/>
      <circle cx="380" cy="190" r="8" fill="{eye_color}"/>
      <circle cx="420" cy="190" r="8" fill="{eye_color}"/>
      {ear_left}{ear_right}{tail}{pattern_layer}
      <rect y="400" width="100%" height="80" fill="#333"/>
    </svg>"""


def compose_svg(trait_values: dict, caption: str) -> str:
    """Use external compose_svg if available; else fallback."""
    if _compose_svg:
        return _compose_svg(trait_values, caption)
    return _fallback_build_svg(trait_values, caption)


def prompt_from_traits(trait_values: dict) -> str:
    """Turn trait labels into a clear, photoreal prompt."""
    # Safely pull with defaults
    A = trait_values.get("A", "").lower()  # body color/pattern
    B = trait_values.get("B", "").lower()  # eye color
    C = trait_values.get("C", "").lower()  # tail length
    D = trait_values.get("D", "").lower()  # ear shape
    E = trait_values.get("E", "").lower()  # pattern/coat

    # Build a consistent, style-stable prompt
    details = ", ".join(
        filter(
            None,
            [
                A or None,
                E or None,
                f"{B}" if B else None,
                f"{D}" if D else None,
                f"{C}" if C else None,
            ],
        )
    )

    # Add style guidance for consistency
    return (
        f"Photorealistic studio portrait of a domestic cat, {details}. "
        f"Neutral white background, soft even lighting, sharp focus, natural proportions, no accessories."
    )


def try_generate_ai_image(prompt: str, save_path: Path) -> bool:
    """Return True if an AI image was generated & saved, else False."""
    if not _USE_AI:
        return False
    try:
        print(f"🖼️ AI image request → {prompt}")
        resp = _openai_client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
        )
        b64 = resp.data[0].b64_json
        save_path.write_bytes(base64.b64decode(b64))
        print(f"✅ AI image saved → {save_path}")
        return True
    except Exception as e:
        print(f"⚠️ AI image generation failed, falling back to SVG: {e}")
        return False


def save_svg_png(trait_values: dict, caption: str) -> None:
    """Create SVG fallback and render to PNG."""
    svg = compose_svg(trait_values, caption)
    SVG_PATH.write_text(svg, encoding="utf-8")
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(PNG_PATH))
    print(f"✅ Fallback SVG→PNG saved → {PNG_PATH}")


def read_live_state_or_test(args) -> dict:
    """Get genotype from sensors (live) or test args."""
    if args.test:
        print("🧪 Test mode active")
        return {pair.split("=")[0].upper(): pair.split("=")[1].lower() for pair in args.test}
    # Live sensors
    try:
        from sensors import GeneBoard

        print("🧭 Reading from sensors...")
        gb = GeneBoard()
        return gb.read_and_light()  # {'A':'dom', ...}
    except Exception as e:
        print(f"⚠️ Sensors unavailable, defaulting to TEST-like random: {e}")
        genes = ["A", "B", "C", "D", "E"]
        import random

        return {g: random.choice(["dom", "rec"]) for g in genes}


# -----------------------------------------------------------
# Main
# -----------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Kitty CRISPR Generator")
    parser.add_argument("--test", nargs="*", help="e.g. --test A=dom B=rec C=dom D=rec E=dom")
    args = parser.parse_args()

    state = read_live_state_or_test(args)
    trait_values = resolve_trait_labels(state)

    now = datetime.now()
    code = "".join([state.get(t["slot"], "?")[0].upper() for t in TRAITS])
    customer = CUSTOMER_TEMPLATES[now.day % len(CUSTOMER_TEMPLATES)]
    caption = f"Customer: {customer}"

    # Try AI → fallback to SVG
    used_method = "ai" if try_generate_ai_image(prompt_from_traits(trait_values), PNG_PATH) else "svg"
    if used_method == "svg":
        save_svg_png(trait_values, caption)

    # Write JSON summary
    payload = {
        "timestamp": now.isoformat(),
        "genotype": state,
        "phenotype": trait_values,
        "caption": caption,
        "code": code,
        "png": str(PNG_PATH),
        "svg": str(SVG_PATH) if SVG_PATH.exists() else None,
        "method": used_method,
    }
    JSON_PATH.write_text(json.dumps(payload, indent=2))
    print(f"✅ Saved summary → {JSON_PATH}")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
