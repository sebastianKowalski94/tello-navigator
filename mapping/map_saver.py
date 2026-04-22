# Convenience wrapper — actual save logic lives in RoomMapper.save_map()
# This module exists for potential future export formats (SVG, JSON, etc.)

import os
from mapping.grid_map import RoomMapper


def save_png(mapper: RoomMapper, directory: str, filename: str) -> str:
    """Save map as PNG to a given directory. Returns full file path."""
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    mapper.save_map(filepath)
    return filepath
