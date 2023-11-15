from __future__ import annotations
import pygame, sprite, menu, settings, sys
import background as bg
from vec2d import vec2d
from random import randint
from os import path

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', path.dirname(path.abspath(__file__)))
    return path.join(base_path, relative_path)

pygame.init()
screen = pygame.display.set_mode([720, 512])
pygame.display.set_icon(pygame.image.load(resource_path("./assets/img/Apple.png")))
pygame.display.set_caption("Hungry For Apples?")

font = pygame.font.Font(size = 24)
background = bg.Background(resource_path("./assets/img/Tree.png"), screen)

class Splash(list):
    def __init__(self, parent: pygame.Surface, fontObject: pygame.font.Font, *args: str):
        super().__init__(args)
        self.parent = parent
        self.fontObject = fontObject

    def render(self):
        fonts = []

        for line in self:
            fonts.append(self.fontObject.render(line, False, (255, 255, 255)))
        
        self.renderedFonts = fonts

    def draw(self):
        for i in range(len(self)):
            position = (int((self.parent.get_width() / 2) - (self.renderedFonts[i].get_width() / 2)), i * self.renderedFonts[i].get_height() + 100)
            self.parent.blit(self.renderedFonts[i], position)

class assets:
    """Asset Container"""
    appleSpriteSheet = sprite.Spritesheet.parse_file(resource_path("./assets/img/Apple-Animated.png"), (128, 128))

    mainMenu = menu.Menu(screen, (resource_path("./assets/img/Button-Start.png"), (256, 128)), (resource_path("./assets/img/Button-Settings.png"), (256, 128)), (resource_path("./assets/img/Button-Quit.png"), (256, 128)))
    gameOverMenu = menu.Menu(screen, (resource_path("./assets/img/Button-Retry.png"), (256, 128)), (resource_path("./assets/img/Button-Menu.png"), (256, 128)))
    menuPause = menu.Button(resource_path("./assets/img/Gui-Pause.png"), (512, 128), screen)

    menuSettings = menu.AdvancedMenu(screen)
    menuSettings.add(resource_path("./assets/img/Button-Debug.png"), (0, 0, 256, 128))
    menuSettings.add(resource_path("./assets/img/Button-Volume.png"), (0, 129, 256, 128))
    menuSettings.add(resource_path("./assets/img/Button-Plus.png"), (257, 129, 128, 128))
    menuSettings.add(resource_path("./assets/img/Button-Minus.png"), (257+128, 129, 128, 128))
    menuSettings.add(resource_path("./assets/img/Button-Menu.png"), (0, 129+128, 256, 128))

    splashText = Splash(screen, font, "Thank you for playing my game.")
    splashText.append("It's not much but I'm quite proud")
    splashText.append("of being able to design a full game.")
    splashText.append("Click apples to shake them off the tree,")
    splashText.append("you win the level when all the apples hit the ground.")
    splashText.append("Press any key to continue.")

class gameState:
    inGameTimer = 0
    levelTimer = 0
    level = 0
    apples = None

    def init(framerate):
        gameState.inGameTimer = 11 #Must be one more than actual due to math issues
        gameState.levelTimer = gameState.inGameTimer * framerate
        gameState.level = 1
        gameState.apples = generateLevel(gameState.inGameTimer, gameState.level)

def getPadding(surface):
    paddingRects = [None, None]
    if (surface.get_width() < surface.get_height()):
        paddingRects[0] = (0, 0, surface.get_width(), background.rect.top)
        paddingRects[1] = (0, background.rect.bottom, surface.get_width(), background.rect.top)
    
    elif (surface.get_width() > surface.get_height()):
        paddingRects[0] = (0, 0, background.rect.left, surface.get_height())
        paddingRects[1] = (background.rect.right, 0, background.rect.x, surface.get_height())
    
    return paddingRects

def cleanup(surface, padding):
    for rect in padding:
        if (rect):
            surface.fill((0, 0, 0), rect)

def spawnApple():
    apple = sprite.Sprite(assets.appleSpriteSheet.copy(), screen)
    apple.scale(randint(15, 35) / 100)

    x_pos = randint(background.rect.x, background.rect.topright[0] - apple.rect.width)
    y_pos = randint(background.rect.y, int(background.rect.bottomleft[1] / 2) - apple.rect.height)
    apple.set_position(vec2d(x_pos, y_pos))
    apple.pivotPoint = apple.top

    return apple

def generateLevel(timer, level) -> sprite.Group:
        apples = sprite.Group()

        for x in range(10 + int(level * 1.25)):
            apple = spawnApple()
            apple.set_timer(timer)
            apples.add(apple)

        return apples

def main():
    clock = pygame.time.Clock()

    #Set Positions
    background.fit()
    assets.mainMenu.fit()
    assets.gameOverMenu.fit()
    assets.menuPause.fit()

    padding = getPadding(screen)

    #Declarations
    framerate = 60
    timeDelta = clock.tick(60) * 0.001 * framerate

    gameState.init(framerate)

    tick = framerate

    #Fonts
    renderedLevel = font.render(f'Level: {gameState.level}', False, (255, 255, 255))
    renderedTimer = font.render(f'Time Remaining: {int(gameState.levelTimer/60)}', False, (255, 255, 255))
    assets.splashText.render()

    mode = 0
    while True:
        cleanup(screen, padding)
        background.draw()

        #Render Pass
        if (mode == 0): #Splash Screen
            screen.fill((0, 0, 0))
            assets.splashText.draw()

        elif (mode == 1): #Main Menu
            assets.mainMenu.draw()
            assets.mainMenu.update(timeDelta)

        elif (mode == 2): #Game
            renderedTimer = font.render(f'Time Remaining: {round(gameState.levelTimer/60 - 1, 2)}', False, (255, 255, 255))
            screen.blit(renderedTimer, (0, 0))
            screen.blit(renderedLevel, (screen.get_width() - renderedLevel.get_size()[0], 0))

            gameState.apples.update(timeDelta)
            gameState.apples.draw()

        elif (mode == 3): #Settings
            assets.menuSettings.update(timeDelta)
            assets.menuSettings.draw()

        elif (mode == 4): #Game Over
            assets.gameOverMenu.update(timeDelta)
            assets.gameOverMenu.draw()
            
        elif (mode == 5): #Paused
            assets.menuPause.update(timeDelta, flashing=True)
            assets.menuPause.draw()

        pygame.display.update()

        #Event Pass
        mouse = vec2d(*pygame.mouse.get_pos())
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                pygame.quit()
                sys.exit()

            elif (event.type == pygame.KEYDOWN and pygame.key.get_pressed()[pygame.K_SPACE]):
                if (mode == 0): #Splash Screen
                    mode = 1

                elif (mode == 2): #Game
                    mode = 5
                
                elif (mode == 5): #Pause Menu
                    screen.fill((0, 0, 0))
                    mode = 2

            elif (event.type == pygame.MOUSEBUTTONDOWN):
                if (mode == 1): #Main Menu
                    if (assets.mainMenu.buttons[0].mouse_over(mouse)):
                        mode = 2

                    elif (assets.mainMenu.buttons[1].mouse_over(mouse)):
                        mode = 3

                    elif (assets.mainMenu.buttons[2].mouse_over(mouse)):
                        pygame.quit()
                        sys.exit()
                    
                elif (mode == 2): #Game
                    over, apple = gameState.apples.mouseOver(mouse)

                    if (over):
                        apple.isAffectedByGravity = True
                        apple.launch(randint(-60, 60), randint(-60, 60))

                elif (mode == 3): #Settings
                    if (assets.menuSettings.buttons[0].mouse_over(mouse)):
                        settings.settings.debug = not settings.settings.debug
                        assets.menuSettings.buttons[0].toggle()

                    elif (assets.menuSettings.buttons[2].mouse_over(mouse)):
                        settings.set_volume(settings.get_volume() + 0.05)
                    
                    elif (assets.menuSettings.buttons[3].mouse_over(mouse)):
                        settings.set_volume(settings.get_volume() - 0.05)
                    
                    elif (assets.menuSettings.buttons[4].mouse_over(mouse)):
                        mode = 1

                elif (mode == 4): #Game Over
                    if (assets.gameOverMenu.buttons[0].mouse_over(mouse)):
                        gameState.init(framerate)
                        mode = 2

                    elif (assets.gameOverMenu.buttons[1].mouse_over(mouse)):
                        mode = 1

            elif (event.type == pygame.MOUSEMOTION):
                if (mode == 1): #Main Menu
                    assets.mainMenu.hover(mouse)

                elif (mode == 3): #Settings
                    assets.menuSettings.hover(mouse)

                elif (mode == 4): #Game Over
                    assets.gameOverMenu.hover(mouse)

        #In-Game Updates
        if (mode == 2):
            gameState.apples.deaths()
            if (len(gameState.apples) == 0):
                gameState.level += 1
                if ((gameState.level - 1) % 2 == 0):
                    gameState.inGameTimer -= 1
                
                gameState.levelTimer = gameState.inGameTimer * 60
                
                renderedLevel = font.render(f'Level: {gameState.level}', False, (255, 255, 255))
                gameState.apples = generateLevel(gameState.inGameTimer, gameState.level)

            gameState.levelTimer -= timeDelta
            tick -= timeDelta

            if (len(gameState.apples) != 0 and int(gameState.levelTimer / 60) <= 0):
                mode = 4
        
        clock.tick(framerate)

main()