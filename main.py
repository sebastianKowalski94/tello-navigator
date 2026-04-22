#!/usr/bin/env python3
import sys
import time
import signal
import json
import yaml
import argparse
import os
from datetime import datetime
from sensors.hcsr04 import DualSensors
from drone.tello_controller import TelloController
from drone.state_manager import StateManager
from mapping.grid_map import RoomMapper


class TelloNavigator:
    def __init__(self, config_path="config/settings.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.sensors = DualSensors(
            front_trig=self.config['sensors']['front_trigger'],
            front_echo=self.config['sensors']['front_echo'],
            right_trig=self.config['sensors']['right_trigger'],
            right_echo=self.config['sensors']['right_echo']
        )
        self.drone = TelloController()
        self.state_mgr = StateManager(save_dir=self.config['paths']['save_dir'])
        self.mapper = RoomMapper(
            cell_size_cm=self.config['mapping']['cell_size_cm'],
            max_room_cm=self.config['mapping']['max_room_cm']
        )

        self.running = True
        self.obstacle_threshold = self.config['sensors']['obstacle_threshold_cm']
        self.max_turn_attempts  = self.config['sensors'].get('max_turn_attempts', 3)
        signal.signal(signal.SIGINT, self.signal_handler)

        self.stats = {
            'steps': 0,
            'walls_found': 0,
            'laps': 0,
            'distance_traveled_cm': 0,
            'start_time': None
        }


    def signal_handler(self, sig, frame):
        print("\nInterrupted by user — landing.")
        self.running = False

    def check_obstacles(self):
        data = self.sensors.get_all()
        front_cm = data['front_cm']
        right_cm = data['right_cm']

        # Fail-safe: treat sensor error (-1) as wall
        front_wall = (front_cm < 0) or (0 < front_cm < self.obstacle_threshold)
        right_wall = (right_cm < 0) or (0 < right_cm < self.obstacle_threshold)

        return {
            'front_wall': front_wall,
            'right_wall': right_wall,
            'front_dist': front_cm,
            'right_dist': right_cm
        }

    def explore_room(self):
        print("\nStarting mapping (right-hand rule)")
        print(f"Obstacle threshold: {self.obstacle_threshold} cm")
        print(f"Max laps:           {self.config['mapping']['max_laps']}")
        print("Press Ctrl+C to abort\n")

        self.stats['start_time'] = time.time()
        last_orientation = self.mapper.orientation

        while self.running:
            self.stats['steps'] += 1
            walls = self.check_obstacles()
            self._print_status(walls)

            if not walls['right_wall']:
                print("No wall on right → turning right")
                self.drone.rotate_right(90)
                self.mapper.update_position(0, 90)
                time.sleep(0.3)

                walls_after = self.check_obstacles()
                if not walls_after['front_wall']:
                    self.drone.move_forward(40)
                    self.mapper.update_position(40)
                    self.stats['distance_traveled_cm'] += 40
                else:
                    print("Wall ahead after right turn — skipping move")

            elif walls['front_wall']:
                print("Wall ahead → turning left")
                turned = 0
                for attempt in range(self.max_turn_attempts):
                    self.drone.rotate_left(90)
                    self.mapper.update_position(0, -90)
                    self.mapper.add_wall("front")
                    self.stats['walls_found'] += 1
                    time.sleep(0.3)
                    turned += 90

                    walls_after = self.check_obstacles()
                    if not walls_after['front_wall']:
                        break
                    print(f"Still blocked after {attempt + 1} left turn(s) — trying again")
                else:
                    print("[!] Stuck after max left turns — aborting mission")
                    self.running = False
                    break

                self.drone.move_forward(40)
                self.mapper.update_position(40)
                self.stats['distance_traveled_cm'] += 40

            else:
                print("Wall on right → moving forward")
                self.drone.move_forward(40)
                self.mapper.update_position(40)
                self.stats['distance_traveled_cm'] += 40

            current_orientation = self.mapper.orientation
            if current_orientation == last_orientation and self.stats['steps'] > 1:
                self.stats['laps'] += 1
                print(f"\n── Lap {self.stats['laps']} complete ──\n")
                if self.stats['laps'] >= self.config['mapping']['max_laps']:
                    print("\nMax laps reached — mapping complete!")
                    break
            last_orientation = current_orientation

            if self.stats['steps'] % 5 == 0:
                self._save_checkpoint()

            flight_time = time.time() - self.stats['start_time']
            if flight_time > self.config['drone']['max_flight_time_sec']:
                print("\nMax flight time reached!")
                break

            time.sleep(0.3)

        return True

    def _print_status(self, walls):
        front_str = f"{walls['front_dist']:5.1f}cm" if walls['front_dist'] > 0 else " ERR "
        right_str = f"{walls['right_dist']:5.1f}cm" if walls['right_dist'] > 0 else " ERR "
        front_marker = "WALL" if walls['front_wall'] else "open"
        right_marker = "WALL" if walls['right_wall'] else "open"

        print(f"[#{self.stats['steps']:3d}]  "
              f"Front: {front_str} {front_marker}  |  "
              f"Right: {right_str} {right_marker}  |  "
              f"Dist: {self.stats['distance_traveled_cm']}cm")

    def _save_checkpoint(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.state_mgr.update_position(self.mapper.x, self.mapper.y)
        self.state_mgr.update_orientation(self.mapper.orientation)
        self.state_mgr.save_state(f"checkpoint_{timestamp}.json")
        self.mapper.save_map(
            os.path.join(self.config['paths']['save_dir'], f"map_progress_{timestamp}.png")
        )


    def run(self, auto_start=True, save_map=None):
        print("\n" + "=" * 60)
        print("TELLO NAVIGATOR — Autonomous Room Mapping")
        print("=" * 60)
        print(f"Output directory: {self.config['paths']['save_dir']}")

        print("\nChecking sensors...")
        if not self.sensors.both_working():
            print("WARNING: One or both sensors are not responding!")
            if not auto_start:
                if input("Continue anyway? (y/n): ").lower() != 'y':
                    print("Mission cancelled.")
                    return
        else:
            print("Sensors OK.")

        print("\nConnecting to drone...")
        if not self.drone.connect():
            print("Connection failed — aborting.")
            return
        print(f"Connected. Battery: {self.drone.get_battery()}%")

        battery = self.drone.get_battery()
        if battery < 20:
            print(f"Low battery: {battery}%")
            if not auto_start:
                if input("Start anyway? (y/n): ").lower() != 'y':
                    return

        print("\nTaking off...")
        self.drone.takeoff()
        time.sleep(2)

        print("\nStarting mapping mission...\n")
        try:
            self.explore_room()

            print("\nSaving final data...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            map_path = save_map if save_map else os.path.join(
                self.config['paths']['save_dir'], f"final_map_{timestamp}.png"
            )
            self.mapper.save_map(map_path)

            self.stats['end_time'] = time.time()
            self.stats['duration_min'] = (
                self.stats['end_time'] - self.stats['start_time']
            ) / 60
            self.stats['completion_percent'] = self.mapper.get_completion_percentage()

            stats_path = os.path.join(
                self.config['paths']['save_dir'], f"stats_{timestamp}.json"
            )
            with open(stats_path, 'w') as f:
                json.dump(self.stats, f, indent=2)

            self._print_summary(map_path, stats_path)

        except Exception as e:
            print(f"\nUnexpected error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            print("\nLanding...")
            self.drone.land()
            print("Mission finished.")

    def _print_summary(self, map_file, stats_file):
        print("\n" + "=" * 60)
        print(f"Flight time : {self.stats['duration_min']:.1f} min")
        print(f"Steps       : {self.stats['steps']}")
        print(f"Laps        : {self.stats['laps']}")
        print(f"Distance    : {self.stats['distance_traveled_cm']} cm  "
              f"({self.stats['distance_traveled_cm'] / 100:.1f} m)")
        print(f"Walls found : {self.stats['walls_found']}")
        print(f"Area covered: {self.stats['completion_percent']:.1f}%")
        print(f"\nMap  → {map_file}")
        print(f"Stats→ {stats_file}")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Tello Navigator — Autonomous Room Mapping'
    )
    parser.add_argument('--auto-start', action='store_true',
                        help='Skip confirmation prompts')
    parser.add_argument('--test-sensors', action='store_true',
                        help='Run sensor test and exit (no drone needed)')
    parser.add_argument('--config', type=str, default='config/settings.yaml',
                        help='Path to settings.yaml')
    parser.add_argument('--save-map', type=str, default=None,
                        help='Custom output path for the final map PNG')
    args = parser.parse_args()

    if args.test_sensors:
        import subprocess
        result = subprocess.run(
            [sys.executable, 'sensors/test_sensors.py', '--config', args.config]
        )
        sys.exit(result.returncode)

    navigator = TelloNavigator(config_path=args.config)
    navigator.run(auto_start=args.auto_start, save_map=args.save_map)


if __name__ == "__main__":
    main()
