import numpy as np
from PIL import Image, ImageDraw
import time

class RoomMapper:
    def __init__(self, cell_size_cm=20, max_room_cm=800):

        self.cell_size = cell_size_cm
        self.grid_size = max_room_cm // cell_size_cm
        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=int)
        self.visited = np.zeros((self.grid_size, self.grid_size), dtype=bool)
 
        self.x = self.grid_size // 2
        self.y = self.grid_size // 2
        self.orientation = 0 
        
        self.visited[self.x][self.y] = True
        self.grid[self.x][self.y] = 1
        
        self.start_time = time.time()

    def get_completion_percentage(self):
        total = self.grid_size * self.grid_size
        visited_count = np.sum(self.visited)
        return (visited_count / total) * 100
        
    def update_position(self, moved_cm, turned_degrees=0):
        self.orientation = (self.orientation + turned_degrees // 90) % 4
        
        cells_moved = moved_cm // self.cell_size
        
        if self.orientation == 0:
            self.y -= cells_moved
        elif self.orientation == 1: 
            self.x += cells_moved
        elif self.orientation == 2:
            self.y += cells_moved
        elif self.orientation == 3:
            self.x -= cells_moved
        
        self.x = max(0, min(self.x, self.grid_size - 1))
        self.y = max(0, min(self.y, self.grid_size - 1))

        self.visited[self.x][self.y] = True
        self.grid[self.x][self.y] = 2  
        
    def add_wall(self, direction):
        orient = self.orientation if direction == "front" else (self.orientation + 1) % 4

        if orient == 0 and self.y - 1 >= 0:
            self.grid[self.x][self.y - 1] = 3
        elif orient == 1 and self.x + 1 < self.grid_size:
            self.grid[self.x + 1][self.y] = 3
        elif orient == 2 and self.y + 1 < self.grid_size:
            self.grid[self.x][self.y + 1] = 3
        elif orient == 3 and self.x - 1 >= 0:
            self.grid[self.x - 1][self.y] = 3
    
    def is_mapping_complete(self, threshold=0.95):
        total = self.grid_size * self.grid_size
        visited_count = np.sum(self.visited)
        return (visited_count / total) >= threshold
    
    def save_map(self, filename="room_map.png"):
        img_size = self.grid_size * 20
        img = Image.new('RGB', (img_size, img_size), color='white')
        draw = ImageDraw.Draw(img)

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x1, y1 = i*20, j*20
                x2, y2 = x1+20, y1+20
                
                cell_type = self.grid[i][j]
                if cell_type == 0:  
                    draw.rectangle([x1, y1, x2, y2], fill='#eeeeee', outline='#cccccc')
                elif cell_type == 1:
                    draw.rectangle([x1, y1, x2, y2], fill='#00ff00', outline='black')
                    draw.text((x1+5, y1+5), "S", fill='black')
                elif cell_type == 2: 
                    draw.rectangle([x1, y1, x2, y2], fill='#aaffaa', outline='black')
                elif cell_type == 3:
                    draw.rectangle([x1, y1, x2, y2], fill='#333333', outline='black')

        x_pos = self.x * 20
        y_pos = self.y * 20
        draw.ellipse([x_pos+5, y_pos+5, x_pos+15, y_pos+15], fill='red', outline='black')
        
        elapsed = time.time() - self.start_time
        visited_pct = (np.sum(self.visited) / (self.grid_size * self.grid_size)) * 100
        
        img.save(filename)
        print(f"Map saved: {filename}")
        print(f"Visited: {visited_pct:.1f}% cells")
        print(f"Time: {elapsed/60:.1f} min")
        
        return filename