from __future__ import annotations
from sprite import Spritesheet
from vec2d import vec2d
import pygame

class Button:
    def __init__(self, file: str | pygame.Surface, dimensions: tuple[int], parent: pygame.Surface, totalSprites: int = None) -> None:
        self.sprites = Spritesheet.parse_file(file, dimensions, totalSprites)

        self.image: pygame.Surface = self.sprites[0].copy()
        self.rect = self.image.get_rect()

        self.parent = parent
        self.hovered = False

        self.tick = 60*60

    def mouse_over(self: Button, mouse: tuple[int]) -> bool:
        if (mouse[0] < self.rect.left or mouse[0] > self.rect.right):
            return False
        
        if (mouse[1] > self.rect.bottom or mouse[1] < self.rect.top):
            return False

        return True
    
    def toggle(self: Button, hovermode: bool = True) -> None:
        if (len(self.sprites) < 2):
            return None

        if (not hovermode):
            if (self.sprites.currentSprite == 0): self.sprites.currentSprite = 1
            else: self.sprites.currentSprite = 0

            self.image.blit(self.sprites[self.sprites.currentSprite].copy(), (0, 0))
            return None
        
        self.hovered = not self.hovered
        if (self.hovered): self.image.blit(self.sprites[1].copy(), (0, 0))
        else: self.image.blit(self.sprites[0].copy(), (0, 0))

    def fit_x(self: Button) -> None:
        self.rect.center = (int(self.parent.get_width() / 2), self.rect.center[1])
    
    def fit_y(self: Button) -> None:
        self.rect.center = (self.rect.center[0], int(self.parent.get_height() / 2))
    
    def fit(self: Button) -> None:
        self.fit_x()
        self.fit_y()
    
    def set_position(self: Button, position: vec2d | pygame.Vector2) -> None:
        self.rect.topleft = (position.x, position.y)
    
    def position(self: Button) -> tuple[int, int]:
        return self.rect.topleft
    
    def scale(self, scalar):
        temp = self.rect.center
        self.image = pygame.transform.scale_by(self.image, scalar)
        self.rect = self.image.get_rect()
        self.rect.center = temp

    def draw(self: Button) -> None:
        self.parent.blit(self.image, (self.rect.topleft))
    
    def update(self: Button, timeDelta: float, flashing: bool = False) -> None:
        if (not flashing):
            return None
        
        if (self.tick <= 0):
            self.toggle(hovermode=False)
            self.tick = 60*60
        
        self.tick -= (timeDelta * 10)
    
class Menu:
    def __init__(self: Menu, parent: pygame.Surface, *files: tuple[str, tuple[int]]):
        self.buttons: list[Button] = []
        for file in files:
            self.buttons.append(Button(file[0], file[1], parent=parent))

        self.position = vec2d(0, 0)
        self.rect = pygame.Rect(*self.position, self.__width__(), self.__height__())
        self.parent = parent

        self.__place_buttons__()

    def __place_buttons__(self: Menu) -> None:
        for y in range(len(self.buttons)):
            self.buttons[y].set_position(vec2d(self.rect.x, y * self.buttons[y].rect.height + int(self.buttons[1].rect.height / len(self.buttons))))

    def set_position(self: Menu, position: vec2d | pygame.Vector2):
        self.position = position
        self.rect.topleft = position

        self.__place_buttons__()
    
    def set_center(self: Menu, position: tuple[float, float] | pygame.Vector2) -> None:
        self.rect.center = position
        self.position = self.rect.topleft

        self.__place_buttons__()

    def hover(self: Menu, mouse: tuple[float, float] | pygame.Vector2) -> bool:
        for button in self.buttons:
            if (button.mouse_over(mouse)):
                if (button.hovered == False):
                    button.toggle()
                
            else:
                if (button.hovered == True):
                    button.toggle()
    
    def fit_x(self):
        self.rect.center = (int(self.parent.get_width() / 2), self.rect.center[1])
        self.__place_buttons__()

    def fit_y(self):
        self.rect.center = (self.rect.center[0], int(self.parent.get_height() / 2))
        self.__place_buttons__()

    def fit(self):
        self.fit_x()
        self.fit_y()

    def update(self, timeDelta):
        for button in self.buttons:
            button.update(timeDelta)

    def draw(self):
        for button in self.buttons:
            button.draw()
    
    def __width__(self: Menu) -> float:
        return self.buttons[0].rect.width
    
    def __height__(self: Menu) -> float:
        return len(self.buttons) * self.buttons[0].rect.height

class AdvancedMenu(Menu):
    def __init__(self: AdvancedMenu, parent: pygame.Surface) -> None:
        self.buttons: list[Button] = []

        self.position = vec2d(0, 0)
        self.parent = parent

    def add(self: AdvancedMenu, file: str, rect: tuple[int, int, int, int]) -> None:
        button = Button(file, rect[2:], parent=self.parent)
        button.set_position(vec2d(*rect[:2], int))
        self.buttons.append(button)

    def fit_x(self: AdvancedMenu) -> None:
        for button in self.buttons:
            button.fit_x()

    def fit_y(self: AdvancedMenu) -> None:
        for button in self.buttons:
            button.fit_x()

    def fit(self: AdvancedMenu) -> None:
        self.fit_x()
        self.fit_y()