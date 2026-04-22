# Custom Frame — Hardware Notes

The `dron.stl` file is a fully custom replacement frame for the DJI Tello.
The original Tello motors, main PCB, and battery are transferred into this frame.

## What the frame includes

- Motor mounts (×4) — compatible with original Tello brushless motors
- Main PCB mount — fits Tello flight controller board
- Battery slot — holds original Tello 1100 mAh battery
- Front sensor bracket — holds HC-SR04 facing forward
- Right sensor bracket — holds HC-SR04 facing right (90° from front)
- Raspberry Pi Zero 2W mount — positioned above the PCB

## Print settings (recommended)

| Parameter | Value |
|-----------|-------|
| Material | PETG or PLA+ |
| Infill | 30–40% |
| Layer height | 0.15–0.20 mm |
| Supports | Yes (Tree) |
| Perimeters | 3 |

## Dimensions

| Axis | Size |
|------|------|
| X    | 120.5 mm |
| Y    | 120.0 mm |
| Z    |  56.0 mm |

## Assembly order

1. Print the frame
2. Transfer motors from original Tello frame (unscrew, desolder if needed)
3. Mount Tello main PCB
4. Slot in battery
5. Mount RPi Zero 2W
6. Insert HC-SR04 sensors into front and right brackets
7. Wire sensors to RPi GPIO (see main README for pin mapping)
