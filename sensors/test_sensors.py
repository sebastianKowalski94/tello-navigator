#!/usr/bin/env python3
"""
Standalone sensor test — run this BEFORE connecting to Tello Wi-Fi
to verify both HC-SR04 sensors are wired and working correctly.

Usage (from project root):
    python3 sensors/test_sensors.py
    python3 sensors/test_sensors.py --config config/settings.yaml
    python3 sensors/test_sensors.py --continuous
"""

import sys
import os
import time
import argparse


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from sensors.hcsr04 import DualSensors


def load_pins(config_path):
    try:
        with open(config_path, 'r') as f:
            cfg = yaml.safe_load(f)
        s = cfg['sensors']
        return s['front_trigger'], s['front_echo'], s['right_trigger'], s['right_echo']
    except Exception as e:
        print(f"[!] Could not load config ({e}), using default pins.")
        return 23, 24, 25, 22


def run_test(sensors, rounds=10, delay=0.5):
    print(f"\n{'='*65}")
    print("HC-SR04 SENSOR TEST")
    print(f"{'='*65}")
    print(f"Running {rounds} readings (press Ctrl+C to stop early)...\n")

    ok_count = 0

    for i in range(1, rounds + 1):
        data = sensors.get_all()
        f_cm = data['front_cm']
        r_cm = data['right_cm']

        f_ok = f_cm > 0
        r_ok = r_cm > 0
        if f_ok and r_ok:
            ok_count += 1

        f_str = f"{f_cm:6.1f} cm" if f_ok else "  ERROR  "
        r_str = f"{r_cm:6.1f} cm" if r_ok else "  ERROR  "
        marker = "OK" if (f_ok and r_ok) else "!!"

        print(f"  [{i:2d}/{rounds}]  Front: {f_str}  |  Right: {r_str}  {marker}")
        time.sleep(delay)

    print(f"\n{'='*65}")
    passed = ok_count >= rounds * 0.6
    if passed:
        print(f"RESULT: PASSED  ({ok_count}/{rounds} readings valid)")
    else:
        print(f"RESULT: FAILED  ({ok_count}/{rounds} readings valid)")
        print("  Check wiring — TRIG/ECHO pins and 5V/GND connections.")
    print(f"{'='*65}\n")
    return passed


def run_continuous(sensors):
    print(f"\n{'='*65}")
    print("HC-SR04 CONTINUOUS MODE  (Ctrl+C to quit)")
    print(f"{'='*65}\n")
    while True:
        sensors.print_status()
        time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description='HC-SR04 sensor test')
    parser.add_argument('--config', type=str, default='config/settings.yaml',
                        help='Path to settings.yaml (default: config/settings.yaml)')
    parser.add_argument('--continuous', action='store_true',
                        help='Stream readings continuously instead of fixed test')
    parser.add_argument('--rounds', type=int, default=10,
                        help='Number of test readings (default: 10)')
    args = parser.parse_args()

    ft, fe, rt, re = load_pins(args.config)
    print(f"\nPins loaded — Front: TRIG={ft} ECHO={fe} | Right: TRIG={rt} ECHO={re}")

    sensors = DualSensors(front_trig=ft, front_echo=fe,
                          right_trig=rt, right_echo=re)

    try:
        if args.continuous:
            run_continuous(sensors)
        else:
            success = run_test(sensors, rounds=args.rounds)
            sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest stopped by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
