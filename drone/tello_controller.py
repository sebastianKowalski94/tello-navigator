# drone/tello_controller.py
from djitellopy import Tello
import time
import logging

logger = logging.getLogger(__name__)


class TelloController:
    def __init__(self):
        self.tello = Tello()
        self.is_flying = False
        self.battery = 0

    def connect(self):
        print("Connecting to drone...")
        try:
            self.tello.connect()
            self.battery = self.tello.get_battery()
            print(f"Connected! Battery: {self.battery}%")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def takeoff(self):
        if not self.is_flying:
            self.tello.takeoff()
            self.is_flying = True
            print("Airborne.")
            time.sleep(2)

    def land(self):
        if self.is_flying:
            self.tello.land()
            self.is_flying = False
            print("Landed.")

    def move_forward(self, distance_cm=30):
        dist = max(20, min(distance_cm, 500))   # Tello SDK min is 20 cm
        self.tello.move_forward(dist)
        logger.debug(f"Forward {dist} cm")
        time.sleep(0.5)

    def move_backward(self, distance_cm=30):
        dist = max(20, min(distance_cm, 500))
        self.tello.move_back(dist)
        logger.debug(f"Backward {dist} cm")
        time.sleep(0.5)

    def rotate_right(self, degrees=90):
        deg = min(degrees, 360)
        self.tello.rotate_clockwise(deg)
        logger.debug(f"Rotate CW {deg}°")
        time.sleep(0.5)

    def rotate_left(self, degrees=90):
        deg = min(degrees, 360)
        self.tello.rotate_counter_clockwise(deg)
        logger.debug(f"Rotate CCW {deg}°")
        time.sleep(0.5)

    def get_battery(self):
        self.battery = self.tello.get_battery()
        return self.battery
