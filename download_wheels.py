#!/usr/bin/env python3
"""
Run this script on your PC (Windows/Mac/Linux) to download all .whl files
for Raspberry Pi Zero 2W (aarch64, Python 3.9, Bullseye 64-bit).

Usage:
    python download_wheels.py

Output:
    wheels/ folder with all .whl files — copy it to your USB drive.
"""

import subprocess
import sys
import os

WHEELS_DIR = os.path.join(os.path.dirname(__file__), "wheels")

PACKAGES = [
    "djitellopy>=2.4.0",
    "gpiozero>=1.6.2",
    "RPi.GPIO>=0.7.1",
    "numpy>=1.21.0,<2.0.0",
    "Pillow>=9.0.0",
    "PyYAML>=6.0",
]

def main():
    os.makedirs(WHEELS_DIR, exist_ok=True)
    print(f"Downloading wheels to: {os.path.abspath(WHEELS_DIR)}")
    print(f"Target: linux_aarch64 / cp39 / Raspberry Pi Zero 2W\n")

    cmd = [
        sys.executable, "-m", "pip", "download",
        "--platform", "linux_aarch64",
        "--python-version", "3.9",
        "--implementation", "cp",
        "--abi", "cp39",
        "--only-binary=:all:",
        "--dest", WHEELS_DIR,
    ] + PACKAGES

    result = subprocess.run(cmd, capture_output=False)

    if result.returncode != 0:
        print("\n[!] Some packages failed with --only-binary.")
        print("    Retrying without --only-binary for missing packages...\n")

        cmd_fallback = [
            sys.executable, "-m", "pip", "download",
            "--platform", "linux_aarch64",
            "--python-version", "3.9",
            "--implementation", "cp",
            "--abi", "cp39",
            "--dest", WHEELS_DIR,
        ] + PACKAGES

        subprocess.run(cmd_fallback)

    wheels = os.listdir(WHEELS_DIR)
    print(f"\nDone! {len(wheels)} file(s) in '{WHEELS_DIR}':")
    for w in sorted(wheels):
        print(f"  {w}")

    print("\nNext step: copy the entire project folder to your USB drive.")

if __name__ == "__main__":
    main()
