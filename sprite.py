from __future__ import annotations
from math import pi
from vec2d import vec2d
import pygame, settings

class transformations:
    @staticmethod
    def pivot(sprite, angle):
        #Determine where the center will end up
        center = vec2d.rotate(vec2d(*sprite.rect.center), -angle, sprite.pivotPoint).to_int().list

        new = Sprite(sprite.image, sprite.parent)
        new.rotate(angle * 180 / pi)
        new.set_center(center)

        return new
    
    def pivot_ip(sprite, angle):
        sprite.angle = angle
        center = vec2d.rotate(vec2d(*sprite.base_rect.center), sprite.angle, sprite.pivotPoint).list

        sprite.rotate(-angle * 180 / pi)
        sprite.set_center(center)
    
    def __init__(self):
        self.top = vec2d(self.rect.width / 2, self.rect.topleft[1], int)
        self.bottom = vec2d(self.rect.width / 2, self.rect.bottomleft[1], int)
        self.left = vec2d(self.rect.bottomleft[0], self.rect.height / 2, int)
        self.right = vec2d(self.rect.bottomright[0], self.rect.height / 2, int)

        self.angle = 0
        self.pivotPoint = vec2d(0, 0)

    def rotate(self, angle):
        temp = self.rect.center
        self.image = pygame.transform.rotate(self.base, angle)
        self.im_copy = pygame.transform.rotate(self.base, angle)
        self.rect = self.image.get_rect()

        self.rect.center = temp

        if (self.sprites):
            self.sprites.rotate(angle)
    
    def fit(self):
        fittedRect = self.rect.fit(self.parent.get_rect())
        temp = pygame.transform.scale(self.image.copy(), fittedRect.size)
        self.image = pygame.Surface(fittedRect.size, pygame.SRCALPHA)
        self.im_copy = pygame.Surface(fittedRect.size, pygame.SRCALPHA)

        self.image.blit(temp, (0, 0))
        self.im_copy.blit(temp, (0, 0))

        self.rect = self.image.get_rect()
        self.magnitude = vec2d(self.rect.width, self.rect.height).magnitude()

        self.set_position(vec2d(self.parent.get_width() / 2 - self.image.get_width() / 2, 0))

    def set_center(self, position: vec2d) -> None:
        self.rect.center = position.list
        self.position = vec2d(self.rect.x, self.rect.y)

        self.__calc_sides__()

    def set_position(self, position: vec2d) -> None:
        self.position = position

        self.rect.x = position.x
        self.rect.y = position.y

        self.base_rect.x = position.x
        self.base_rect.y = position.y

        self.__calc_sides__()
    
    def scale(self, scalar):
        temp = self.rect.center
        self.image = pygame.transform.scale_by(self.image, scalar)
        self.im_copy = self.image.copy()
        self.rect = self.image.get_rect()
        self.base_rect = self.rect.copy()

        self.rect.center = temp

        self.__calc_sides__()
        self.magnitude = vec2d(self.rect.width, self.rect.height).magnitude()

        if (self.sprites):
            self.sprites.scale(scalar)
    
    def __calc_sides__(self):
        self.top = vec2d(self.rect.topleft[0] + self.rect.width / 2, self.rect.topleft[1], int)
        self.bottom = vec2d(self.rect.topleft[0] + self.rect.width / 2, self.rect.bottomleft[1], int)
        self.left = vec2d(self.rect.bottomleft[0], self.rect.bottomleft[1] - self.rect.height / 2, int)
        self.right = vec2d(self.rect.bottomright[0], self.rect.bottomleft[1] - self.rect.height / 2, int)

class Spritesheet(list):
    @staticmethod
    def parse(image: pygame.Surface, spriteDimensions: tuple[int], totalSprites: int = None) -> Spritesheet:
        newsheet = []
        
        for y in range(image.get_height() // spriteDimensions[1]):
            for x in range(image.get_width() // spriteDimensions[0]):
                temp = pygame.Surface(spriteDimensions)
                temp.blit(image, (-spriteDimensions[0] * x, -spriteDimensions[1] * y))
                newsheet.append(temp.copy())
        
        if (totalSprites):
            newsheet = newsheet[:totalSprites]

        return Spritesheet(*newsheet)

    @staticmethod
    def parse_file(file: str, spriteDimensions: tuple[int], totalSprites: int = None) -> Spritesheet:
        #Remove any alpha channel added by aseprite
        image = pygame.image.load(file).convert()

        #Don't render [insert color here]
        image.set_colorkey((0, 0, 0))

        return Spritesheet.parse(image, spriteDimensions, totalSprites)

    def __init__(self, *inputs) -> None:
        list.__init__(self)

        for input in inputs:
            self.append(input)

        self.currentSprite = 0
    
    def scale(self, scalar: float) -> None:
        for i in range(len(self)):
            self[i] = pygame.transform.scale_by(self[i], scalar)
    
    def rotate(self, angle: float) -> None:
        return None

    def unpack(self) -> list[pygame.Surface]:
        return [x for x in self]
    
    def copy(self):
        images = [im.copy() for im in self.unpack()]
        return Spritesheet(*images)

class Sprite(pygame.sprite.Sprite, transformations):
    def __init__(self: Sprite, file: str, parent: pygame.Surface = None) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.sprites: Spritesheet = None

        try:
            #Remove any alpha channel added by aseprite
            self.image = pygame.image.load(file).convert()

            #Don't render [insert color here]
            self.image.set_colorkey((0, 0, 0))

        except (TypeError, RuntimeError):
            if (type(file) == Spritesheet):
                self.sprites = file
                self.image = file[0]

            else:
                #Remove any alpha channel added by aseprite
                self.image = file.convert()

                #Don't render [insert color here]
                self.image.set_colorkey((0, 0, 0))

        self.im_copy = self.image.copy()
        self.base = self.image.copy()
        self.rect = self.image.get_rect()
        self.base_rect = self.base.get_rect()
        self.parent = parent
        transformations.__init__(self)
        
        self.magnitude = vec2d(self.rect.width, self.rect.height).magnitude()
        self.gravity = self.magnitude / 20 * settings.gravity
        self.friction = -0.12

        self.position = vec2d(0, 0)
        self.velocity = vec2d(0, 0)
        self.acceleration = vec2d(0, self.gravity)

        self.isAffectedByGravity = False

        self.onGround = False
        self.timer = 100

        self.tick = 60

    def new(self):
        return Sprite(self.sprites, self.parent)

    def mouse_over(self: Sprite, mouse: vec2d | tuple[int]) -> bool:
        if (mouse[0] < self.rect.left or mouse[0] > self.rect.right):
            return False
        
        if (mouse[1] > self.rect.bottom or mouse[1] < self.rect.top):
            return False
        
        return True

    def draw(self, parent: pygame.Surface = None) -> None:
        self.__draw_debug__(self.image)

        try:
            if (not self.parent):
                parent.blit(self.image, (self.rect.x, self.rect.y))
            
            else:
                self.parent.blit(self.image, (self.rect.x, self.rect.y))

        except AttributeError:
            if (not self.parent):
                parent.clear()
                parent.image.blit(self.image, self.rect)
            
            else:
                self.parent.clear()
                self.parent.image.blit(self.image, self.rect)
    
    def limit_velocity(self, maxVel):
        self.velocity.x = min(-maxVel, max(self.velocity.x, maxVel))
        if (abs(self.velocity.x) < 0.01): self.velocity.x = 0

    def move_horizontal(self, timeDelta: float) -> None:
        self.acceleration.x = 0
        
        self.acceleration.x += self.velocity.x * self.friction
        self.velocity.x += self.acceleration.x * timeDelta

        self.position.x += self.velocity.x * timeDelta + (self.acceleration.x * 0.5) * timeDelta**2

        self.rect.x = self.position.x
        self.base_rect.x = self.position.x

    def move_vertical(self, timeDelta: float) -> None:
        if (self.onGround or not self.isAffectedByGravity):
            return
        
        self.acceleration.y += 0.3
        
        self.velocity.y += self.acceleration.y * timeDelta
        if (self.velocity.y > 7): self.velocity.y = 7
        
        self.position.y += self.velocity.y * timeDelta + (self.acceleration.y * 0.5) * timeDelta**2

        self.rect.bottom = self.position.y
        self.base_rect.bottom = self.position.y

        if (self.rect.bottom > self.parent.get_height()):
            self.rect.bottom = self.parent.get_height()
            self.onGround = True

    def launch(self, x_vel, y_vel):
        self.velocity.x = x_vel
        self.velocity.y = y_vel

    def set_timer(self, timer):
        self.timer = timer * 60
        self.originalTimer = timer * 60
    
    def toggle(self):
        if (not self.sprites):
            return None
        
        self.image.fill((0, 0, 0))
        if (self.sprites.currentSprite == 0): self.sprites.currentSprite = 1
        else: self.sprites.currentSprite = 0

        self.image.blit(self.sprites[self.sprites.currentSprite], (0, 0))
        self.image.set_colorkey((0, 0, 0))
        self.im_copy = self.image.copy()
        
    def flash(self, timeDelta):
        if (self.timer / 60 < self.originalTimer / 60 * 0.4):
            self.tick -= (timeDelta * 2.5)
            if (self.tick <= 0):
                self.tick = 60
                self.toggle()

    def update(self: Sprite, timeDelta: float) -> None:
        self.move_horizontal(timeDelta)
        self.move_vertical(timeDelta)

        if (self.sprites):
            self.flash(timeDelta)

        self.timer -= timeDelta

    def __draw_debug__(self, surf):
        if (settings.settings.debug):
            pygame.draw.rect(surf, (0, 255, 0), surf.get_rect(), 1)

class Group(pygame.sprite.Group):
    def deaths(self):
        totalDeaths = 0

        for surface in self.sprites():
            if (surface.onGround):
                totalDeaths += 1
                surface.kill()
            
            if (surface.timer <= 0):
                totalDeaths -= 1
                surface.kill()
        
        return totalDeaths


    def mouseOver(self, mouse):
        #Start from top to bottom
        for surface in self.sprites()[::-1]:
            truth = surface.mouse_over(mouse)
            if (truth): return truth, surface
        
        return False, None

    def draw(self, *args, **kwargs):
        for surface in self.sprites():
            surface.draw(*args, **kwargs)