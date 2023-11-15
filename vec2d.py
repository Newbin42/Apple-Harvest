from __future__ import annotations
from pygame import Vector2

class vec2d(Vector2):
    @staticmethod
    def slope(a: vec2d, b: vec2d, vectorize: bool = True) -> vec2d | float:
         out = (b.y - a.y, b.x - a.x)
         if vectorize: return vec2d(out)
         if (out[1] == 0): return out[0]
         
         return out[0] / out[1]

    def __init__(self: vec2d, x: float, y: float, dtype=float) -> None:
        super().__init__(dtype(x), dtype(y))

    def unpack(self) -> list[float, float]:
        return [self.x, self.y]

    def to_int(self) -> vec2d:
        return vec2d(self.x, self.y, int)
    
    def to_float(self) -> vec2d:
        return vec2d(self.x, self.y)
    
    def as_Vector2(self):
        return Vector2(self.x, self.y)
    
    def __getitem__(self, i):
        return self.unpack()[i]
    
    def __setitem__(self, i, item):
        self.list[i] = item