# config.py

# --------------------------
# Round rotation & traits
# --------------------------

ROUNDS = [
    {
        "id": 1,
        "name": "Cat 1 – Classic Morphology",
        "customer": "I demand balance: elegant but a little feral.",
        "traits": [
            {"slot": "A", "name": "Eye Color", "dominant": "green eyes", "recessive": "blue eyes"},
            {"slot": "B", "name": "Fur Length", "dominant": "long fur", "recessive": "short fur"},
            {"slot": "C", "name": "Ear Shape", "dominant": "pointy ears", "recessive": "rounded ears"},
            {"slot": "D", "name": "Tail Length", "dominant": "long tail", "recessive": "short tail"},
            {"slot": "E", "name": "Body Color", "dominant": "orange coat", "recessive": "gray coat"},
        ],
    },
    {
        "id": 2,
        "name": "Cat 2 – Face & Pattern",
        "customer": "I need a cat fit for a magazine cover.",
        "traits": [
            {"slot": "A", "name": "Nose Color", "dominant": "pink nose", "recessive": "black nose"},
            {"slot": "B", "name": "Eye Color", "dominant": "amber eyes", "recessive": "blue eyes"},
            {"slot": "C", "name": "Fur Color", "dominant": "cream fur", "recessive": "charcoal fur"},
            {"slot": "D", "name": "Paw Size", "dominant": "large paws", "recessive": "dainty paws"},
            {"slot": "E", "name": "Pattern", "dominant": "striped tabby pattern", "recessive": "solid coat"},
        ],
    },
    # 3: Sporty
    {
        "id": 3,
        "name": "Cat 3 – Sporty Cat",
        "customer": "I need a cat that looks like it could win the Kitty Olympics!",
        "traits": [
            {"slot": "A", "name": "Build", "dominant": "muscular build", "recessive": "slim build"},
            {"slot": "B", "name": "Fur Texture", "dominant": "sleek short coat", "recessive": "fluffy coat"},
            {"slot": "C", "name": "Eye Expression", "dominant": "focused intense eyes", "recessive": "relaxed eyes"},
            {"slot": "D", "name": "Leg Length", "dominant": "long athletic legs", "recessive": "stubby legs"},
            {"slot": "E", "name": "Tail Shape", "dominant": "straight tail", "recessive": "curved tail"},
        ],
    },
    # 4: Goth
    {
        "id": 4,
        "name": "Cat 4 – Goth Cat",
        "customer": "Give me a cat that listens to The Cure and stares into the void.",
        "traits": [
            {"slot": "A", "name": "Fur Color", "dominant": "black fur", "recessive": "gray fur"},
            {"slot": "B", "name": "Eye Color", "dominant": "deep red eyes", "recessive": "ice blue eyes"},
            {"slot": "C", "name": "Pattern", "dominant": "dark smoky pattern", "recessive": "solid color"},
            {"slot": "D", "name": "Accessory", "dominant": "black spiked collar", "recessive": "plain neck"},
            {"slot": "E", "name": "Aura", "dominant": "moody shadowy look", "recessive": "neutral calm look"},
        ],
    },
    # 5: Precious
    {
        "id": 5,
        "name": "Cat 5 – Precious Cat",
        "customer": "I need a cat so cute it could melt the coldest heart!",
        "traits": [
            {"slot": "A", "name": "Fur Length", "dominant": "extra fluffy fur", "recessive": "short velvety fur"},
            {"slot": "B", "name": "Eye Shape", "dominant": "large round eyes", "recessive": "narrow eyes"},
            {"slot": "C", "name": "Color", "dominant": "soft cream fur", "recessive": "white fur"},
            {"slot": "D", "name": "Ear Shape", "dominant": "tiny rounded ears", "recessive": "tall ears"},
            {"slot": "E", "name": "Tail Type", "dominant": "plume tail", "recessive": "short puff tail"},
        ],
    },
    # 6: Old People's
    {
        "id": 6,
        "name": "Cat 6 – Old People’s Cat",
        "customer": "I want a calm lap cat that naps more than it moves.",
        "traits": [
            {
                "slot": "A",
                "name": "Fur Color",
                "dominant": "white fur with silver streaks",
                "recessive": "solid beige coat",
            },
            {"slot": "B", "name": "Body Size", "dominant": "slightly plump body", "recessive": "slender body"},
            {"slot": "C", "name": "Expression", "dominant": "sleepy half-lidded eyes", "recessive": "gentle eyes"},
            {"slot": "D", "name": "Movement", "dominant": "slow deliberate walk", "recessive": "lively gait"},
            {
                "slot": "E",
                "name": "Personality",
                "dominant": "patient calm demeanor",
                "recessive": "friendly curious look",
            },
        ],
    },
    # 7: Giant
    {
        "id": 7,
        "name": "Cat 7 – Giant Cat",
        "customer": "I need a cat that could double as a body pillow.",
        "traits": [
            {"slot": "A", "name": "Body Size", "dominant": "extra large frame", "recessive": "average build"},
            {"slot": "B", "name": "Fur Length", "dominant": "long shaggy coat", "recessive": "medium coat"},
            {"slot": "C", "name": "Tail Length", "dominant": "very long tail", "recessive": "short tail"},
            {"slot": "D", "name": "Ear Type", "dominant": "tufted lynx ears", "recessive": "plain rounded ears"},
            {"slot": "E", "name": "Eye Color", "dominant": "gold eyes", "recessive": "green eyes"},
        ],
    },
    # 8: Rebel
    {
        "id": 8,
        "name": "Cat 8 – Rebel Cat",
        "customer": "Give me a cat that doesn’t play by the rules.",
        "traits": [
            {
                "slot": "A",
                "name": "Pattern",
                "dominant": "half-and-half split color",
                "recessive": "mismatched patches",
            },
            {"slot": "B", "name": "Fur Style", "dominant": "spiky fur tufts", "recessive": "messy fur"},
            {"slot": "C", "name": "Ear Shape", "dominant": "notched ear tip", "recessive": "normal ear"},
            {"slot": "D", "name": "Expression", "dominant": "mischievous grin", "recessive": "defiant glare"},
            {"slot": "E", "name": "Accessory", "dominant": "red bandana", "recessive": "earring"},
        ],
    },
]

ROUND_START_OFFSET = 0  # usually 0


# --------------------------
# Hardware mapping
# --------------------------

# Hall inputs (BCM)
HALL_PINS = {
    "A": {"dom": 5, "rec": 6},
    "B": {"dom": 13, "rec": 19},
    "C": {"dom": 26, "rec": 17},
    "D": {"dom": 23, "rec": 24},
    "E": {"dom": 4, "rec": 7},
}

# LEDs (BCM) per slot
LED_PINS = {
    "A": {"green": 12, "red": 16},
    "B": {"green": 20, "red": 21},
    "C": {"green": 22, "red": 27},
    "D": {"green": 25, "red": 18},
    "E": {"green": 14, "red": 15},
}

# MCP3008 analog channels for pogo ID
ADC_CHANNEL = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4}

# Expected tile IDs (labels are arbitrary strings you define)
TILE_ID_BY_SLOT = {
    "A": {"dom": "A_DOM", "rec": "A_REC"},
    "B": {"dom": "B_DOM", "rec": "B_REC"},
    "C": {"dom": "C_DOM", "rec": "C_REC"},
    "D": {"dom": "D_DOM", "rec": "D_REC"},
    "E": {"dom": "E_DOM", "rec": "E_REC"},
}

# TEMP thresholds — calibrate and update!
ADC_ID_THRESHOLDS = {
    "A": [(0.40, "A_DOM"), (0.85, "A_REC")],
    "B": [(0.45, "B_DOM"), (0.90, "B_REC")],
    "C": [(0.50, "C_DOM"), (0.95, "C_REC")],
    "D": [(0.55, "D_DOM"), (1.00, "D_REC")],
    "E": [(0.60, "E_DOM"), (1.05, "E_REC")],
}

# 7-segment via MAX7219 (optional)
USE_MAX7219 = True  # flip to True when you add the module
