# 📁 FILE: config.py

CUSTOMER_TEMPLATES = [
    "I demand a cat perfect for intergalactic tea parties.",
    "I require an apex cuddler—sleek yet chaotic.",
    "Fetch me a museum-quality mischief-machine.",
    "I need a cat that screams ‘I read journals but knock over plants.’",
    "Give me a cat optimized for naps and villain monologues.",
]

# Pin map and trait definitions. Adjust names or add new traits here.
TRAITS = [
    {"slot": "A", "name": "Fur Length", "pins": {"dom": 5, "rec": 6}, "alleles": {"dom": "long", "rec": "short"}},
    {"slot": "B", "name": "Ears", "pins": {"dom": 12, "rec": 13}, "alleles": {"dom": "pointy", "rec": "floppy"}},
    {"slot": "C", "name": "Tail", "pins": {"dom": 16, "rec": 19}, "alleles": {"dom": "long", "rec": "bob"}},
    {"slot": "D", "name": "Pattern", "pins": {"dom": 20, "rec": 21}, "alleles": {"dom": "stripes", "rec": "spots"}},
    {"slot": "E", "name": "Eyes", "pins": {"dom": 22, "rec": 23}, "alleles": {"dom": "green", "rec": "blue"}},
]

# Display size (pixels) – typical 3.5" SPI TFT is 480x320.
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

# Output paths
OUT_DIR = "output"
SVG_PATH = f"{OUT_DIR}/cat.svg"
PNG_PATH = f"{OUT_DIR}/cat.png"
JSON_PATH = f"{OUT_DIR}/cat_of_the_day.json"
