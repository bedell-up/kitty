import os
import json
import cairosvg
from datetime import datetime
from time import sleep
from config import TRAITS, OUT_DIR, SVG_PATH, PNG_PATH, JSON_PATH, CUSTOMER_TEMPLATES
from compose_svg import build_cat_svg


def resolve_trait_labels(state):
    """Map A..E to concrete labels used by the renderer"""
    mapping = {}
    for t in TRAITS:
        slot = t["slot"]
        allele = state.get(slot, "unknown")
        if allele in ("dom", "rec"):
            mapping[slot] = t["alleles"][allele]
        else:
            # Default safe fallback
            mapping[slot] = list(t["alleles"].values())[0]
    return mapping


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kitty CRISPR Cat Generator")
    parser.add_argument(
        "--test",
        nargs="*",
        help="Run in test mode: e.g. --test A=dom B=rec C=dom D=rec E=dom",
    )
    args = parser.parse_args()

    # 🧪 TEST MODE
    if args.test:
        state = {pair.split("=")[0].upper(): pair.split("=")[1].lower() for pair in args.test}
        print(f"[TEST MODE] Using manual gene combo: {state}")

    # 🧭 LIVE SENSOR MODE
    else:
        from sensors import GeneBoard  # only load GPIO if needed

        gb = GeneBoard()
        print("Reading sensors and lighting LEDs...")
        sleep(1)
        state = gb.read_and_light()

    # 🧠 Map allele codes to visible trait labels
    trait_values = resolve_trait_labels(state)

    # 🐱 Build caption and cat image
    now = datetime.now()
    code = "".join([state.get(t["slot"], "?")[0].upper() for t in TRAITS])
    customer = CUSTOMER_TEMPLATES[now.day % len(CUSTOMER_TEMPLATES)]
    caption = f"Customer: {customer}"

    svg = build_cat_svg(trait_values, caption)
    os.makedirs(OUT_DIR, exist_ok=True)

    # 💾 Save SVG + PNG
    with open(SVG_PATH, "w") as f:
        f.write(svg)

    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=PNG_PATH)

    # 💾 Save JSON summary
    payload = {
        "timestamp": now.isoformat(),
        "genotype": state,
        "phenotype": trait_values,
        "caption": caption,
        "code": code,
        "png": PNG_PATH,
        "svg": SVG_PATH,
    }

    with open(JSON_PATH, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"✅ Saved {PNG_PATH} and {JSON_PATH}")
