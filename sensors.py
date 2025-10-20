# Kitty CRISPR – Pi Zero 2W with KY‑003 Hall sensors + LED feedback + test mode

import os, json, argparse
from datetime import datetime
from gpiozero import Button, LED
from time import sleep
from config import TRAITS, DISPLAY_WIDTH, DISPLAY_HEIGHT, OUT_DIR, SVG_PATH, PNG_PATH, JSON_PATH
from compose_svg import build_cat_svg
import cairosvg

# LED pin mapping (adjust as needed)
LED_PINS = {
    "A": {"green": 26, "red": 27},
    "B": {"green": 17, "red": 18},
    "C": {"green": 24, "red": 25},
    "D": {"green": 8, "red": 7},
    "E": {"green": 9, "red": 10},
}

CUSTOMER_TEMPLATES = [
    "I demand a cat perfect for intergalactic tea parties.",
    "I require an apex cuddler—sleek yet chaotic.",
    "Fetch me a museum‑quality mischief‑machine.",
    "I need a cat that screams ‘I read journals but knock over plants.’",
    "Give me a cat optimized for naps and villain monologues.",
]


class GeneBoard:
    def __init__(self):
        self.sensors = {}
        for t in TRAITS:
            slot = t["slot"]
            dom_pin = t["pins"]["dom"]
            rec_pin = t["pins"]["rec"]
            self.sensors[slot] = {
                "dom": Button(dom_pin, pull_up=True, bounce_time=0.02),
                "rec": Button(rec_pin, pull_up=True, bounce_time=0.02),
                "led_g": LED(LED_PINS[slot]["green"]),
                "led_r": LED(LED_PINS[slot]["red"]),
            }

    def read_and_light(self):
        state = {}
        for slot, parts in self.sensors.items():
            dom_active = not parts["dom"].is_pressed
            rec_active = not parts["rec"].is_pressed
            if dom_active ^ rec_active:
                state[slot] = "dom" if dom_active else "rec"
                parts["led_g"].on()
                parts["led_r"].off()
            else:
                state[slot] = "unknown"
                parts["led_g"].off()
                parts["led_r"].on()
        return state


def resolve_trait_labels(state):
    mapping = {}
    for t in TRAITS:
        slot = t["slot"]
        allele = state.get(slot, "unknown")
        if allele in ("dom", "rec"):
            mapping[slot] = t["alleles"][allele]
        else:
            mapping[slot] = list(t["alleles"].values())[0]
    return mapping


def main():
    parser = argparse.ArgumentParser(description="Kitty CRISPR Cat Generator")
    parser.add_argument("--test", nargs="*", help="Manual test mode: e.g. --test A=dom B=rec C=dom")
    args = parser.parse_args()

    if args.test:
        # Manual test mode
        state = {pair.split("=")[0].upper(): pair.split("=")[1].lower() for pair in args.test}
        print(f"[TEST MODE] Using manual gene combo: {state}")
    else:
        # Live mode
        gb = GeneBoard()
        print("Reading sensors and lighting LEDs...")
        sleep(1)
        state = gb.read_and_light()

    enriched = {}
    for t in TRAITS:
        slot = t["slot"]
        allele = state.get(slot, "unknown")
        label = t["alleles"].get(allele, "unknown") if allele in ("dom", "rec") else "unknown"
        enriched[slot] = {"allele": allele, "label": label, "trait": t["name"]}

    trait_values = resolve_trait_labels(state)

    now = datetime.now()
    code = "".join([state.get(t["slot"], "?")[0].upper() for t in TRAITS])
    customer = CUSTOMER_TEMPLATES[now.day % len(CUSTOMER_TEMPLATES)]
    caption = f"Customer: {customer}"

    svg = build_cat_svg(trait_values, caption)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(SVG_PATH, "w") as f:
        f.write(svg)

    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=PNG_PATH)

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

    print(f"Generated {PNG_PATH} and {JSON_PATH}")


if __name__ == "__main__":
    main()
