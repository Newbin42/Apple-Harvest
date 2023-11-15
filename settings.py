class settings:
    debug = False
    volume = 1

#Unseen Settings
gravity = 0.35

def toggle_debug():
    debug = not debug

def set_volume(newVolume: float) -> None:
    settings.volume = clamp(newVolume, 0, 1)

def get_volume() -> float:
    return settings.volume

def clamp(value: float, min: float, max: float) -> None:
    if (value > max): return max
    if (value < min): return min

    return value