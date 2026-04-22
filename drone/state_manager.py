import json
import os
import time

class StateManager:
    def __init__(self, save_dir="/home/pi/tello_data"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
        self.state = {
            "position": {"x": 0, "y": 0},
            "orientation": 0,
            "path": [],
            "walls": [],
            "start_time": time.time()
        }
    
    def update_position(self, x, y):
        self.state["position"]["x"] = x
        self.state["position"]["y"] = y
        self.state["path"].append({"x": x, "y": y, "time": time.time()})
    
    def update_orientation(self, degrees):
        self.state["orientation"] = degrees
    
    def add_wall(self, x, y, direction):
        self.state["walls"].append({
            "x": x, "y": y, 
            "direction": direction,
            "time": time.time()
        })
    
    def save_state(self, filename="flight_state.json"):
        filepath = os.path.join(self.save_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(self.state, f, indent=2)
        print(f"Saved: {filepath}")
        return filepath
    
    def save_map_image(self, grid_map, filename="floor_map.png"):
        filepath = os.path.join(self.save_dir, filename)
        grid_map.save_map(filepath)
        return filepath