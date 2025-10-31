#!/usr/bin/env python3
import os, json, argparse, base64, random
from datetime import datetime, date
from pathlib import Path
import cairosvg

from config import ROUNDS, ROUND_START_OFFSET, TILE_ID_BY_SLOT, USE_MAX7219
from sensors import GeneBoard

# Optional AI image generation (set OPENAI_API_KEY env var to enable)
_USE_AI = bool(os.getenv("OPENAI_API_KEY"))
if _USE_AI:
    try:
        from openai import OpenAI

        _openai = OpenAI()
    except Exception:
        _USE_AI = False

# Optional MAX7219 7-seg percent
_segdev = None
if USE_MAX7219:
    try:
        from luma.core.interface.serial import spi as lspi
        from luma.led_matrix.device import max7219

        serial = lspi(port=0, device=1)  # CE1
        _segdev = max7219(serial, cascaded=1, block_orientation=0, rotate=0)
    except Exception:
        _segdev = None

OUT = Path("output")
OUT.mkdir(exist_ok=True)
SVG_PATH = OUT / "cat.svg"
PNG_PATH = OUT / "cat.png"
JSON_PATH = OUT / "cat_of_the_day.json"
STATE_PATH = OUT / "game_state.json"
SLOTS = ["A", "B", "C", "D", "E"]


# ---------- Round state ----------
def _round_by_id(rid: int) -> dict:
    for r in ROUNDS:
        if r["id"] == rid:
            return r
    raise SystemExit(f"No round with id={rid}")


def _default_round_for_today() -> dict:
    idx = (date.today().toordinal() + ROUND_START_OFFSET) % len(ROUNDS)
    return ROUNDS[idx]


def _random_target() -> dict:
    return {s: random.choice(["dom", "rec"]) for s in SLOTS}


def _load_state() -> dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            pass
    return {}


def _save_state(state: dict):
    STATE_PATH.write_text(json.dumps(state, indent=2))


def get_or_init_game_state(round_override: int | None) -> dict:
    st = _load_state()
    if round_override:
        r = _round_by_id(round_override)
        st = {"current_round_id": r["id"], "target_genotype": _random_target(), "advance_on_next_run": False}
        _save_state(st)
        return st
    if "current_round_id" not in st or "target_genotype" not in st:
        r = _default_round_for_today()
        st = {"current_round_id": r["id"], "target_genotype": _random_target(), "advance_on_next_run": False}
        _save_state(st)
    return st


def maybe_advance_round(state: dict) -> dict:
    if not state.get("advance_on_next_run"):
        return state
    ids = [r["id"] for r in ROUNDS]
    cur = ids.index(state["current_round_id"])
    nxt = ids[(cur + 1) % len(ids)]
    new = {"current_round_id": nxt, "target_genotype": _random_target(), "advance_on_next_run": False}
    _save_state(new)
    return new


# ---------- Traits & image ----------
def resolve_trait_labels(genotype: dict, round_cfg: dict) -> dict:
    labels = {}
    for t in round_cfg["traits"]:
        slot = t["slot"]
        allele = genotype.get(slot, "rec")
        labels[slot] = t["dominant"] if allele == "dom" else t["recessive"]
    return labels


def prompt_from_traits(labels: dict, round_cfg: dict) -> str:
    desc = ", ".join(labels[s["slot"]] for s in round_cfg["traits"])
    return (
        "Photorealistic studio portrait of a domestic cat, "
        f"{desc}. Neutral white background, soft even lighting, "
        "sharp focus, natural proportions, no accessories."
    )


def try_ai(prompt: str, save_png: Path) -> bool:
    if not _USE_AI:
        return False
    try:
        r = _openai.images.generate(model="gpt-image-1", prompt=prompt, size="1024x1024")
        img_b64 = r.data[0].b64_json
        save_png.write_bytes(base64.b64decode(img_b64))
        return True
    except Exception:
        return False


def fallback_svg(labels: dict, caption: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="480">
      <rect width="100%" height="100%" fill="#111"/>
      <text x="400" y="60" font-size="28" text-anchor="middle" fill="#fff">{caption}</text>
      <text x="400" y="120" font-size="18" text-anchor="middle" fill="#ddd">
        {" • ".join(labels.values())}
      </text>
      <rect x="200" y="180" rx="20" ry="20" width="400" height="240" fill="#333" />
      <text x="400" y="300" font-size="24" text-anchor="middle" fill="#bbb">Photo placeholder</text>
    </svg>"""


def save_svg_png(svg: str):
    SVG_PATH.write_text(svg, encoding="utf-8")
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(PNG_PATH))


# ---------- Progress ----------
def compute_matches(live: dict, target: dict) -> tuple[int, dict]:
    """
    live: {'A': {'allele': 'dom/rec/invalid/None', 'tile_id': 'A_DOM'/'A_REC'/None, ...}, ...}
    target: {'A':'dom', ...}
    """
    matches = {}
    correct = 0
    for slot in SLOTS:
        allele = live[slot]["allele"]
        tileid = live[slot]["tile_id"]
        if allele not in ("dom", "rec"):
            matches[slot] = None
            continue
        allele_ok = allele == target[slot]
        expected_id = TILE_ID_BY_SLOT[slot].get(target[slot])
        id_ok = tileid == expected_id
        ok = bool(allele_ok and id_ok)
        matches[slot] = {"allele_ok": allele_ok, "id_ok": id_ok, "ok": ok}
        if ok:
            correct += 1
    percent = int(round(100 * correct / len(SLOTS)))
    return percent, matches


def sevenseg_show(percent: int):
    if not _segdev:
        return
    try:
        from luma.core.render import canvas

        with canvas(_segdev) as draw:
            draw.text((1, -1), f"{percent:3d}", fill="white")
    except Exception:
        pass


# ---------- Main ----------
def main():
    ap = argparse.ArgumentParser(description="Kitty CRISPR – sensors + LEDs + % + image")
    ap.add_argument("--test", nargs="*", help="Mock alleles/tile_ids, e.g. --test A=dom B=rec C=dom")
    ap.add_argument("--round", type=int, help="Override round id (resets target)")
    ap.add_argument("--advance-now", action="store_true", help="Advance to next round immediately")
    args = ap.parse_args()

    state = get_or_init_game_state(args.round)
    state = (
        maybe_advance_round(state)
        if not args.advance_now
        else maybe_advance_round({"current_round_id": state["current_round_id"], "advance_on_next_run": True})
    )
    current_round = _round_by_id(state["current_round_id"])

    gb = GeneBoard()
    try:
        # Read board (or test)
        if args.test:
            live = {}
            for kv in args.test:
                k, v = kv.split("=")
                k = k.upper()
                v = v.lower()
                live[k] = {"allele": v, "tile_id": f"{k}_{v.upper()}", "volts": 0.0}
            for s in SLOTS:
                live.setdefault(s, {"allele": None, "tile_id": None, "volts": 0.0})
        else:
            live = gb.snapshot()

        # Presence-only LEDs
        gb.update_leds_presence(live)

        # Progress (allele + tile ID vs hidden target)
        percent, matches = compute_matches(live, state["target_genotype"])

        # 7-seg percent (optional)
        sevenseg_show(percent)

        # Build cat image (alleles-only → phenotype)
        allele_only = {s: (live[s]["allele"] or "rec") for s in SLOTS}
        labels = resolve_trait_labels(allele_only, current_round)
        caption = f"Customer: {current_round['customer']}"
        used = "ai" if try_ai(prompt_from_traits(labels, current_round), PNG_PATH) else "svg"
        if used == "svg":
            svg = fallback_svg(labels, caption)
            save_svg_png(svg)

        # If solved, schedule advance-on-next-run
        if percent == 100:
            st = _load_state()
            st["current_round_id"] = current_round["id"]
            st["target_genotype"] = state["target_genotype"]
            st["advance_on_next_run"] = True
            _save_state(st)

        # Save summary
        now = datetime.now()
        payload = {
            "timestamp": now.isoformat(),
            "round_id": current_round["id"],
            "round_name": current_round["name"],
            "customer": current_round["customer"],
            "genotype_live": {s: live[s]["allele"] for s in SLOTS},
            "tile_ids": {s: live[s]["tile_id"] for s in SLOTS},
            "phenotype": labels,
            "png": str(PNG_PATH),
            "svg": str(SVG_PATH) if SVG_PATH.exists() else None,
            "method": used,
            "progress_percent": percent,
            "matches_by_slot": matches,
            "advance_on_next_run": _load_state().get("advance_on_next_run", False),
        }
        JSON_PATH.write_text(json.dumps(payload, indent=2))
        print(f"🏁 Progress: {percent}%")
        print(f"✅ Saved → {JSON_PATH}")

    finally:
        gb.close()


if __name__ == "__main__":
    main()
