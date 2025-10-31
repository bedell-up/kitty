# sensors.py
import time
import spidev
import RPi.GPIO as GPIO
from statistics import mean
from config import HALL_PINS, LED_PINS, ADC_CHANNEL, ADC_ID_THRESHOLDS

SLOTS = ["A", "B", "C", "D", "E"]


class GeneBoard:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        # Hall sensors
        for slot, pins in HALL_PINS.items():
            GPIO.setup(pins["dom"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(pins["rec"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # LEDs
        for slot, pins in LED_PINS.items():
            GPIO.setup(pins["green"], GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(pins["red"], GPIO.OUT, initial=GPIO.LOW)
        # Default LED state: show "needs tile" (red ON)
        for slot, pins in LED_PINS.items():
            GPIO.output(pins["green"], GPIO.LOW)
            GPIO.output(pins["red"], GPIO.HIGH)

        # SPI for MCP3008 on CE0
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 1_000_000

    def close(self):
        try:
            self.spi.close()
        finally:
            GPIO.cleanup()

    # ----- ADC helpers -----
    def _read_adc_raw(self, ch: int) -> int:
        r = self.spi.xfer2([1, (8 + ch) << 4, 0])
        return ((r[1] & 3) << 8) | r[2]  # 0..1023

    def _adc_to_volts(self, raw: int) -> float:
        return 3.3 * raw / 1023.0

    def read_slot_voltage(self, slot: str, samples: int = 5) -> float:
        ch = ADC_CHANNEL[slot]
        vals = [self._adc_to_volts(self._read_adc_raw(ch)) for _ in range(samples)]
        return round(mean(vals), 3)

    def decode_tile_id(self, slot: str, volts: float) -> str | None:
        table = sorted(ADC_ID_THRESHOLDS.get(slot, []), key=lambda x: x[0])
        for max_v, label in table:
            if volts <= (max_v + 0.03):  # small hysteresis
                return label
        return None

    # ----- Hall sensors -----
    def read_allele(self, slot: str) -> str | None:
        pins = HALL_PINS[slot]
        dom_active = GPIO.input(pins["dom"]) == GPIO.LOW
        rec_active = GPIO.input(pins["rec"]) == GPIO.LOW
        if dom_active and not rec_active:
            return "dom"
        if rec_active and not dom_active:
            return "rec"
        if not dom_active and not rec_active:
            return None
        return "invalid"

    # ----- One-shot read of all slots -----
    def snapshot(self) -> dict:
        data = {}
        for slot in SLOTS:
            allele = self.read_allele(slot)
            # Only sample ADC if a tile is present (dom/rec)
            volts = self.read_slot_voltage(slot) if allele in ("dom", "rec") else 0.0
            tile_id = self.decode_tile_id(slot, volts) if allele in ("dom", "rec") else None
            data[slot] = {"allele": allele, "volts": volts, "tile_id": tile_id}
        return data

    # ----- Presence-only LEDs -----
    def update_leds_presence(self, live: dict):
        """
        Green ON if a tile is present and properly seated (allele == dom/rec).
        Red ON otherwise (empty or invalid).
        """
        for slot, info in live.items():
            g = LED_PINS[slot]["green"]
            r = LED_PINS[slot]["red"]
            allele = info.get("allele")
            if allele in ("dom", "rec"):
                GPIO.output(g, GPIO.HIGH)
                GPIO.output(r, GPIO.LOW)
            else:
                GPIO.output(g, GPIO.LOW)
                GPIO.output(r, GPIO.HIGH)

    # ----- Simple calibration helper -----
    def calibrate_adc(self, slot: str, seconds: int = 3):
        print(f"[Calibrate] Hold the tile for slot {slot} in place for {seconds}s …")
        vals = []
        t0 = time.time()
        while time.time() - t0 < seconds:
            vals.append(self.read_slot_voltage(slot, samples=3))
            time.sleep(0.05)
        print(f"Slot {slot}: avg={mean(vals):.3f} V  min={min(vals):.3f}  max={max(vals):.3f}")
