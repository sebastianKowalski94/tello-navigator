from gpiozero import DistanceSensor
import time
import math

class HCSR04:
    def __init__(self, trigger_pin: int, echo_pin: int, name: str = "Sensor"):
        self.name = name
        self.trigger = trigger_pin
        self.echo = echo_pin
        self.sensor = None
        self._init_sensor()
        
    def _init_sensor(self):
        try:
            self.sensor = DistanceSensor(
                trigger=self.trigger,
                echo=self.echo,
                max_distance=4.0,
                queue_len=3
            )
            print(f"{self.name}: OK (Trig={self.trigger}, Echo={self.echo})")
            return True
        except Exception as e:
            print(f"{self.name}: FAILED - {e}")
            return False
    
    def get_distance_cm(self, samples: int = 3) -> float:
        if self.sensor is None:
            return -1
            
        distances = []
        for _ in range(samples):
            try:
                raw_dist = self.sensor.distance
                if math.isnan(raw_dist) or math.isinf(raw_dist):
                    continue
                    
                dist_cm = raw_dist * 100

                if 2 < dist_cm < 400:
                    distances.append(dist_cm)
                else:
                    pass
            except Exception:
                pass
            time.sleep(0.05)
        
        if distances:
            return round(sum(distances) / len(distances), 1)
        return -1 


class DualSensors:
    def __init__(self, front_trig=17, front_echo=18, right_trig=27, right_echo=22):
        print("\n" + "="*50)
        print("INITIALIZING SENSORS")
        print("="*50)
        self.front = HCSR04(front_trig, front_echo, "FRONT")
        self.right = HCSR04(right_trig, right_echo, "RIGHT")
        print("="*50 + "\n")

    def get_all(self) -> dict:
        return {
            "front_cm": self.front.get_distance_cm(),
            "right_cm": self.right.get_distance_cm(),
            "timestamp": time.time()
        }
    
    def print_status(self):
        data = self.get_all()
        front_str = f"{data['front_cm']:6.1f} cm" if data['front_cm'] > 0 else "  ERROR "
        right_str = f"{data['right_cm']:6.1f} cm" if data['right_cm'] > 0 else "  ERROR "
        print(f"[{time.strftime('%H:%M:%S')}] Front: {front_str} | Right: {right_str}")
    
    def both_working(self) -> bool:
        front_ok = self.front.get_distance_cm(samples=2) > 0
        right_ok = self.right.get_distance_cm(samples=2) > 0
        return front_ok and right_ok