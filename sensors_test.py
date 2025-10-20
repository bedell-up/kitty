# 📁 FILE: sensors_test.py
# Quick CLI to verify wiring and sensor logic.
from sensors import GeneBoard, serialize_board_state
from time import sleep
import os

if __name__ == "__main__":
    print("\nKitty CRISPR – Sensors test (Ctrl+C to quit)\n")
    gb = GeneBoard()
    while True:
        state = gb.read_with_retries()
        enriched = serialize_board_state(state)
        line = []
        for slot in sorted(enriched.keys()):
            a = enriched[slot]
            line.append(f"{slot}:{a['allele'][:1].upper()}({a['label']})")

        print(" ".join(line), end="\r", flush=True)
        sleep(0.2)
