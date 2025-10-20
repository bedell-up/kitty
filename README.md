# 📁 FILE: README.md
# Quick start, wiring, and nightly job setup.

# Kitty CRISPR (Hall‑sensor edition)

This Pi Zero 2W project reads 10 KY‑003 Hall effect modules (2 per trait, 5 traits),
then generates a cartoon cat from SVG layers every night. The 3.5" screen shows the
most recent “cat of the day” with a comedic customer request.

## Hardware summary
- Pi Zero 2 **WH** (headers installed).
- 10× KY‑003 Hall effect sensor modules (A3144E). Power them from **3.3V**, not 5V.
- 5 gene slots; each slot has **two sensors** (Dominant vs Recessive).
- 3.5" display (commonly 480×320). The code uses 480×320 by default.

> KY‑003 output is usually **HIGH when no magnet**, **LOW when magnet is present**.
> We treat “active when LOW” in software and also enable internal pull‑ups for safety.
> Ensure magnet orientation is consistent across all tiles.

## GPIO wiring (BCM numbering)
Trait A (Fur Length):  DOM → GPIO 5,  REC → GPIO 6  
Trait B (Ears):        DOM → GPIO 12, REC → GPIO 13  
Trait C (Tail):        DOM → GPIO 16, REC → GPIO 19  
Trait D (Pattern):     DOM → GPIO 20, REC → GPIO 21  
Trait E (Eye Color):   DOM → GPIO 22, REC → GPIO 23  

**All sensors:** VCC → 3.3V; GND → GND; OUT → the GPIO listed above.

> TIP: KY‑003 boards typically include a pull‑up; the code also sets internal pull‑ups.
> Do **not** feed 5V into GPIO pins.