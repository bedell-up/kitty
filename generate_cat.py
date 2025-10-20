# 📁 FILE: generate_cat.py
# Nightly job: read sensors → resolve alleles → compose SVG → export PNG + JSON
import os, json
from datetime import datetime
from sensors import GeneBoard, serialize_board_state
from config import TRAITS, OUT_DIR, SVG_PATH, PNG_PATH, JSON_PATH
from compose_svg import build_cat_svg
import cairosvg

os.makedirs(OUT_DIR, exist_ok=True)

CUSTOMER_TEMPLATES = [
    "I demand a cat perfect for intergalactic tea parties.",
    "I require an apex cuddler—sleek yet chaotic.",
    "Fetch me a museum‑quality mischief‑machine.",
    "I need a cat that screams ‘I read journals but knock over plants.’",
    "Give me a cat optimized for naps and villain monologues.",
]


def resolve_trait_labels(enriched_state):
    # Map A..E to concrete labels used by the renderer
    mapping = {}
    for t in TRAITS:
        slot = t["slot"]
        allele = enriched_state[slot]["allele"]
        if allele in ("dom", "rec"):
            mapping[slot] = t["alleles"][allele]
        else:
            # default safe fallback
            mapping[slot] = list(t["alleles"].values())[0]
    return mapping


if __name__ == "__main__":
    gb = GeneBoard()
    state = gb.read_with_retries()
    enriched = serialize_board_state(state)

    # Build caption and cat name
    now = datetime.now()
    code = "".join([state.get(t["slot"], "?")[0].upper() for t in TRAITS])
    customer = CUSTOMER_TEMPLATES[now.day % len(CUSTOMER_TEMPLATES)]
    caption = f"Customer: {customer}"

    trait_values = resolve_trait_labels(enriched)
    svg = build_cat_svg(trait_values, caption)

    with open(SVG_PATH, "w") as f:
        f.write(svg)

    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=PNG_PATH)

    payload = {
        "timestamp": now.isoformat(),
        "genotype": state,  # e.g., {'A':'dom','B':'rec',...}
        "phenotype": trait_values,  # e.g., {'A':'long','B':'floppy',...}
        "caption": caption,
        "code": code,
        "png": PNG_PATH,
        "svg": SVG_PATH,
    }
    with open(JSON_PATH, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"Saved {PNG_PATH} and {JSON_PATH}")
