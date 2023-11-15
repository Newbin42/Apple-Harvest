from __future__ import annotations
from vec2d import vec2d
import pygame, settings

class Background(pygame.Surface):
    def __init__(self: Background, file: str, parent: pygame.Surface = None) -> None:
        try:
            #Remove any alpha channel added by aseprite
            self.image = pygame.image.load(file).convert()

        except TypeError:
            #Remove any alpha channel added by aseprite
            self.image = file.convert()

        self.im_copy = self.image.copy()
        self.rect = self.image.get_rect()
        self.parent = parent

        pygame.Surface.__init__(self, self.rect.size)
        self.blit(self.image, (0, 0))

        self.position = vec2d(0, 0)

    def clear(self):
        self.image.fill((0, 0, 0))
        self.image.blit(self.im_copy, (0, 0))

    def fit(self):
            fittedRect = self.rect.fit(self.parent.get_rect())
            temp = pygame.transform.scale(self.image.copy(), fittedRect.size)
            self.image = pygame.Surface(fittedRect.size, pygame.SRCALPHA)
            self.im_copy = pygame.Surface(fittedRect.size, pygame.SRCALPHA)

            pygame.Surface.__init__(self, fittedRect.size)

            self.image.blit(temp, (0, 0))
            self.blit(self.image, (0, 0))

            self.im_copy.blit(temp, (0, 0))
            self.rect = self.image.get_rect()

            self.set_position(vec2d(self.parent.get_width() / 2 - self.image.get_width() / 2, self.parent.get_height() / 2 - self.image.get_height() / 2))
    
    def set_position(self, position: vec2d) -> None:
        self.position = position

        self.rect.x = position.x
        self.rect.y = position.y

    def draw(self, parent: pygame.Surface = None, debug = False) -> None:
        self.__draw_debug__(self, debug)

        try:
            if (not self.parent): parent.blit(self, self.rect.topleft)
            else: self.parent.blit(self, self.rect.topleft)

        except AttributeError:
            if (not self.parent):
                parent.clear()
                parent.image.blit(self, self.rect.topleft)
            
            else:
                self.parent.clear()
                self.parent.image.blit(self, self.rect.topleft)
    
    def __draw_debug__(self, surf, debug):
        if (settings.settings.debug):
            pygame.draw.rect(surf, (0, 255, 0), surf.get_rect(), 1)