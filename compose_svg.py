# 📁 FILE: compose_svg.py
# Build a simple layered SVG cat from selected alleles.
from typing import Dict
from config import DISPLAY_WIDTH, DISPLAY_HEIGHT

SVG_HEADER = f"""
<svg xmlns='http://www.w3.org/2000/svg' width='{DISPLAY_WIDTH}' height='{DISPLAY_HEIGHT}' viewBox='0 0 {DISPLAY_WIDTH} {DISPLAY_HEIGHT}'>
  <defs>
    <filter id='shadow' x='-20%' y='-20%' width='140%' height='140%'>
      <feDropShadow dx='0' dy='2' stdDeviation='3' flood-opacity='0.25'/>
    </filter>
  </defs>
  <rect width='100%' height='100%' fill='#f5efe6'/>
"""

SVG_FOOTER = "</svg>\n"

# Utility to add a group with optional shadow


def g(content: str, shadow=False) -> str:
    return f"<g{' filter=\"url(#shadow)\"' if shadow else ''}>{content}</g>\n"


# Base body layer (neutral)


def layer_body():
    cx, cy = DISPLAY_WIDTH // 2, int(DISPLAY_HEIGHT * 0.58)
    body = f"""
    <ellipse cx='{cx}' cy='{cy}' rx='{int(DISPLAY_WIDTH*0.26)}' ry='{int(DISPLAY_HEIGHT*0.22)}' fill='#f1d3b3' stroke='#8f775f' stroke-width='3'/>
    """
    head = f"""
    <ellipse cx='{cx}' cy='{int(DISPLAY_HEIGHT*0.33)}' rx='{int(DISPLAY_WIDTH*0.20)}' ry='{int(DISPLAY_HEIGHT*0.16)}' fill='#f1d3b3' stroke='#8f775f' stroke-width='3'/>
    """
    return g(body + head, shadow=True)


# Ears: pointy vs floppy


def layer_ears(allele: str):
    cx, y = DISPLAY_WIDTH // 2, int(DISPLAY_HEIGHT * 0.19)
    if allele == "pointy":
        ears = f"""
        <polygon points='{cx-90},{y+20} {cx-40},{y-40} {cx-10},{y+10}' fill='#f1d3b3' stroke='#8f775f' stroke-width='3'/>
        <polygon points='{cx+90},{y+20} {cx+40},{y-40} {cx+10},{y+10}' fill='#f1d3b3' stroke='#8f775f' stroke-width='3'/>
        """
    else:  # floppy
        ears = f"""
        <path d='M {cx-80},{y-5} q -30,40 10,70' fill='none' stroke='#8f775f' stroke-width='12' stroke-linecap='round'/>
        <path d='M {cx+80},{y-5} q 30,40 -10,70'  fill='none' stroke='#8f775f' stroke-width='12' stroke-linecap='round'/>
        """
    return g(ears)


# Fur length: long vs short → mane/ruff


def layer_fur(allele: str):
    cx, cy = DISPLAY_WIDTH // 2, int(DISPLAY_HEIGHT * 0.33)
    if allele == "long":
        ruff = f"<path d='M {cx-120},{cy+30} q 40,40 80,0 q 40,-40 80,0' fill='none' stroke='#b88c66' stroke-width='8' stroke-linecap='round'/>"
    else:
        ruff = f"<path d='M {cx-90},{cy+30} q 30,20 60,0 q 30,-20 60,0' fill='none' stroke='#b88c66' stroke-width='5' stroke-linecap='round'/>"
    return g(ruff)


# Tail: long vs bob


def layer_tail(allele: str):
    base_x, base_y = int(DISPLAY_WIDTH * 0.7), int(DISPLAY_HEIGHT * 0.55)
    if allele == "long":
        tail = f"<path d='M {base_x},{base_y} q 80,-80 40,-140 q -20,-50 -60,-10' fill='none' stroke='#8f775f' stroke-width='16' stroke-linecap='round'/>"
    else:
        tail = f"<path d='M {base_x},{base_y} q 30,-10 10,-40' fill='none' stroke='#8f775f' stroke-width='16' stroke-linecap='round'/>"
    return g(tail, shadow=True)


# Pattern: stripes vs spots


def layer_pattern(allele: str):
    cx, cy = DISPLAY_WIDTH // 2, int(DISPLAY_HEIGHT * 0.58)
    if allele == "stripes":
        pats = []
        for dx in (-80, -40, 0, 40, 80):
            pats.append(f"<path d='M {cx+dx},{cy-60} q 10,30 -10,60' stroke='#8f775f' stroke-width='8' fill='none'/>")
        return g("".join(pats))
    else:  # spots
        pats = []
        for dx, dy, r in [(-70, -30, 14), (-10, -10, 18), (50, 0, 12), (80, -40, 10)]:
            pats.append(f"<circle cx='{cx+dx}' cy='{cy+dy}' r='{r}' fill='#8f775f' opacity='0.8'/>")
        return g("".join(pats))


# Eyes: green vs blue


def layer_eyes(allele: str):
    cx, cy = DISPLAY_WIDTH // 2, int(DISPLAY_HEIGHT * 0.33)
    iris = "#3dbb6f" if allele == "green" else "#4aa3ff"
    eyes = f"""
      <ellipse cx='{cx-38}' cy='{cy}' rx='20' ry='14' fill='white' stroke='#333' stroke-width='3'/>
      <ellipse cx='{cx+38}' cy='{cy}' rx='20' ry='14' fill='white' stroke='#333' stroke-width='3'/>
      <circle cx='{cx-38}' cy='{cy}' r='8' fill='{iris}'/>
      <circle cx='{cx+38}' cy='{cy}' r='8' fill='{iris}'/>
      <circle cx='{cx-38}' cy='{cy}' r='3' fill='black'/>
      <circle cx='{cx+38}' cy='{cy}' r='3' fill='black'/>
    """
    return g(eyes)


# Caption


def layer_caption(text: str):
    return f"<text x='50%' y='{int(DISPLAY_HEIGHT*0.08)}' text-anchor='middle' font-size='22' font-family='Verdana' fill='#333'>{text}</text>\n"


def build_cat_svg(trait_values: Dict[str, str], caption: str) -> str:
    # trait_values: {'A':'long','B':'pointy', ...} resolved to labels
    parts = [SVG_HEADER]
    parts.append(layer_caption(caption))
    parts.append(layer_body())
    parts.append(layer_tail(trait_values.get("C", "long")))
    parts.append(layer_fur(trait_values.get("A", "short")))
    parts.append(layer_ears(trait_values.get("B", "pointy")))
    parts.append(layer_pattern(trait_values.get("D", "stripes")))
    parts.append(layer_eyes(trait_values.get("E", "green")))
    parts.append(SVG_FOOTER)
    return "".join(parts)
