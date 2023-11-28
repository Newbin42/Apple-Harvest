from __future__ import annotations
import pygame, sprite, menu, settings, sys, asyncio
import background as bg
from vec2d import vec2d
from random import randint

pygame.init()
screen = pygame.display.set_mode([720, 512])
pygame.display.set_caption("Hungry For Apples?")
pygame.display.set_icon(pygame.image.load("./assets/icon.png"))
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.NOEVENT])

font = pygame.font.Font(size = 36)
background = bg.Background("./assets/img/Tree.png", screen)

class Splash(list):
    leftAlign = 1
    middleAlign = 2
    rightAlign = 4

    def __init__(self, parent: pygame.Surface, fontObject: pygame.font.Font, *args: str):
        super().__init__(args)
        self.parent = parent
        self.fontObject = fontObject
        self.rendered = False

        self.align(Splash.middleAlign)

    def append(self: Splash, text: str, justification: int = None) -> None:
        super().append(text)
        self.justifications.append(justification if justification else Splash.middleAlign)

    def render(self):
        fonts: list[pygame.Surface] = []

        for line in self:
            fonts.append(self.fontObject.render(line, False, (255, 255, 255)))
        
        self.renderedFonts = fonts
        self.rendered = True
    
    def unload(self):
        self.renderedFonts = []
        self.rendered = False

    def align_left(self):
        self.align(Splash.leftAlign)

    def align_right(self):
        self.align(Splash.rightAlign)

    def align_middle(self):
        self.align(Splash.middleAlign)

    def align(self, justification: int = None) -> None:
        if (not justification): justification = Splash.middleAlign
        self.justifications = [justification for x in range(len(self))]

    def draw(self):
        if (not self.rendered):
            return None
        
        for i in range(len(self)):
            match (self.justifications[i]):
                case Splash.leftAlign: position = (0, i * self.renderedFonts[i].get_height())
                case Splash.middleAlign: position = (int((self.parent.get_width() / 2) - (self.renderedFonts[i].get_width() / 2)), i * self.renderedFonts[i].get_height())
                case Splash.rightAlign: position = (self.parent.get_width() - self.renderedFonts[i].get_width(), i * self.renderedFonts[i].get_height())
            
            self.parent.blit(self.renderedFonts[i], position)

class assets:
    """Asset Container"""
    appleSpriteSheet = sprite.Spritesheet.parse_file("./assets/img/Apple-Animated.png", (128, 128))

    mainMenu = menu.Menu(screen, ("start", "./assets/img/Button-Start.png", (256, 128)), ("settings", "./assets/img/Button-Settings.png", (256, 128)), ("credits", "./assets/img/Button-Credits.png", (256, 128)), ("quit", "./assets/img/Button-Quit.png", (256, 128)))
    gameOverMenu = menu.Menu(screen, ("retry", "./assets/img/Button-Retry.png", (256, 128)), ("menu", "./assets/img/Button-Menu.png", (256, 128)))
    menuPause = menu.Button("./assets/img/Gui-Pause.png", (512, 128), screen)

    menuSettings = menu.AdvancedMenu(screen)
    center_x = screen.get_width() / 2 - 128
    menuSettings.add("plus", "./assets/img/Button-Plus.png", (center_x - 128, 0, 128, 128))
    menuSettings.add("volume", "./assets/img/Button-Volume.png", (center_x, 0, 256, 128))
    menuSettings.add("minus", "./assets/img/Button-Minus.png", (center_x + 256, 0, 128, 128))
    menuSettings.add("menu", "./assets/img/Button-Menu.png", (center_x, 128, 256, 128))

    splashText = Splash(screen, font, "Thank you for playing my game.")
    splashText.append("It's not much but I'm quite proud")
    splashText.append("of being able to design a full game.")
    splashText.append("Click apples to shake them off the tree,")
    splashText.append("")
    splashText.append("you win the level when all the apples hit the ground.")
    splashText.append("Press any key or click to continue.")

    gameOverText = Splash(screen, font, "You left the apples on the tree too long.")
    gameOverText.append("Now you get nothing.")
    gameOverText.append("")
    gameOverText.append("You completed 0 levels.")
    gameOverText.append("Press any key or click to continue.")

    creditText = Splash(screen, pygame.font.Font(size=28), "CREDITS")
    creditText.append("")
    creditText.append("---MUSIC---")
    creditText.append("'Getting it Done' by Kevin Macleod (incompetech.com)")
    creditText.append("Released under CC-BY 4.0. http://creativecommons.org/licenses/by/4.0/")
    creditText.append("")
    creditText.append("---GRAPHICS---")
    creditText.append("Jackste")
    creditText.append("")
    creditText.append("---SOUND EFFECTS---")
    creditText.append("Jackste")
    creditText.append("")
    creditText.append("---SANITY---")
    creditText.append("Blk12345")
    creditText.append("")
    creditText.append("---You---")
    creditText.append("For playing my game.")

    sounds = {
        "click": pygame.mixer.Sound("./assets/sfx/click.ogg"),
        "game_over": pygame.mixer.Sound("./assets/sfx/game-over.ogg"),
        "bg_music": pygame.mixer.Sound("./assets/sfx/Getting-it-Done.ogg"),
    }

class modes:
    M_SPLASH = 1
    M_MAIN = 2
    M_SETTINGS = 4
    M_GAME = 8
    M_PAUSE = 16
    M_GAMEOVERSPLASH = 32
    M_GAMEOVER = 64
    M_CREDITS = 128

class buttons:
    B_START = "start"
    B_SETTINGS = "settings"
    B_CREDITS = "credits"
    B_QUIT = "quit"
    B_MENU = "menu"
    B_RETRY = "retry"
    B_VOLUME = "volume"
    B_PLUS = "plus"
    B_MINUS = "minus"

class gameState:
    inGameTimer = 0
    levelTimer = 0
    level = 0
    apples = None

    renderedLevel = None
    renderedTimer = None

    def update():
        gameState.renderedTimer = font.render(f'Time Remaining: {round(gameState.levelTimer/60 - 1, 2)}', False, (255, 255, 255))

    def updateLevel():
        gameState.renderedLevel = font.render(f'Level: {gameState.level}', False, (255, 255, 255))

    def draw():
        screen.blit(gameState.renderedTimer, (0, 0))
        screen.blit(gameState.renderedLevel, (screen.get_width() - gameState.renderedLevel.get_size()[0], 0))

    def init(framerate):
        gameState.inGameTimer = 11 #Must be one more than actual due to math issues
        gameState.levelTimer = gameState.inGameTimer * framerate
        gameState.renderedLevel = font.render(f'Level: {gameState.level}', False, (255, 255, 255))
        gameState.renderedTimer = font.render(f'Time Remaining: {int(gameState.levelTimer/60)}', False, (255, 255, 255))

        gameState.level = 1
        gameState.apples = generateLevel(gameState.inGameTimer, gameState.level, y_limits = (gameState.renderedTimer.get_height(), 0))

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

def spawnApple(x_limits: tuple[int] = (0, 0), y_limits: tuple[int] = (0, 0)) -> None:
    apple = sprite.Sprite(assets.appleSpriteSheet.copy(), screen)
    apple.scale(randint(15, 35) / 100)

    x_pos = randint(background.rect.x + x_limits[0], background.rect.topright[0] - apple.rect.width - x_limits[1])
    y_pos = randint(background.rect.y + y_limits[0], int(background.rect.bottomleft[1] / 2) - apple.rect.height - y_limits[0])
    
    apple.set_position(vec2d(x_pos, y_pos))
    apple.pivotPoint = apple.top

    return apple

def generateLevel(timer, level, x_limits: tuple[int] = (0, 0), y_limits: tuple[int] = (0, 0)) -> sprite.Group:
        apples = sprite.Group()

        for x in range(10 + int(level * 1.5)):
            apple = spawnApple(x_limits, y_limits)
            apple.set_timer(timer)
            apples.add(apple)

        return apples

def update(asset, *args, **kwargs) -> None:
    asset.update(*args, **kwargs)
    asset.draw()

def setVolume():
    for _, sound in assets.sounds.items():
        if (sound.get_volume() != settings.get_volume()):
            sound.set_volume(settings.get_volume())

async def main():
    clock = pygame.time.Clock()

    settings.set_volume(0.35)
    setVolume()

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
    muteVol = settings.get_volume()

    #Fonts
    assets.splashText.render()

    #Allow for loading times
    mode = modes.M_SPLASH
    while True:
        cleanup(screen, padding)
        background.draw()

        #Update Pass
        match (mode):
            case modes.M_SPLASH:
                screen.fill((0, 0, 0))
                assets.splashText.draw()
            case modes.M_MAIN: update(assets.mainMenu, timeDelta)
            case modes.M_SETTINGS: update(assets.menuSettings, timeDelta)
            case modes.M_GAME:
                update(gameState)
                update(gameState.apples, timeDelta)

                gameState.apples.deaths()
                if (len(gameState.apples) == 0):
                    gameState.level += 1
                    assets.gameOverText[3] = f'You completed {gameState.level} levels.'
                    if ((gameState.level - 1) % 10 == 0):
                        gameState.inGameTimer += 1
                    
                    gameState.levelTimer = gameState.inGameTimer * 60
                    
                    gameState.updateLevel()
                    gameState.apples = generateLevel(gameState.inGameTimer, gameState.level, y_limits = (gameState.renderedTimer.get_height(), 0))

                gameState.levelTimer -= timeDelta
                tick -= timeDelta

                if (len(gameState.apples) != 0 and int(gameState.levelTimer / 60) <= 0):
                    assets.sounds["game_over"].play()
                    assets.gameOverText.render()
                    mode <<= 2
            case modes.M_PAUSE: update(assets.menuPause, timeDelta, flashing = True)
            case modes.M_GAMEOVERSPLASH:
                screen.fill((0, 0, 0))
                assets.gameOverText.draw()
            case modes.M_GAMEOVER: update(assets.gameOverMenu, timeDelta)
            case modes.M_CREDITS:
                screen.fill((0, 0, 0))
                assets.creditText.draw()

        #Event Pass
        mouse = vec2d(*pygame.mouse.get_pos())
        event = pygame.event.poll()
        match (event.type):
            case pygame.NOEVENT:
                pass
            case pygame.QUIT:
                assets.sounds["bg_music"].stop()
                pygame.quit()
                sys.exit()
            case pygame.KEYDOWN if event.key == pygame.K_SPACE:
                match (mode):
                    case modes.M_SPLASH: #Splash Screen
                        mode <<= 1
                        assets.splashText.unload()
                        assets.sounds["bg_music"].play(-1)
                    case modes.M_GAME: #Game
                        mode <<= 1
                    case modes.M_CREDITS:
                        assets.creditText.unload()
                        mode >>= 6
                    case modes.M_PAUSE: #Pause Menu
                        screen.fill((0, 0, 0))
                        mode >>= 1
                    case modes.M_GAMEOVERSPLASH: #Game Over Splash
                        mode <<= 1
                        assets.gameOverText.unload()
            case pygame.MOUSEBUTTONDOWN if not event.button in [pygame.BUTTON_WHEELDOWN, pygame.BUTTON_WHEELUP]:
                match (mode):
                    case modes.M_SPLASH:
                        mode <<= 1
                        assets.splashText.unload()
                        assets.sounds["bg_music"].play(-1)
                    case modes.M_MAIN:
                        mouseOver = assets.mainMenu.get_mouse_over(mouse)
                        if (mouseOver in [buttons.B_START, buttons.B_SETTINGS, buttons.B_QUIT]):
                            assets.sounds["click"].play()

                        match (mouseOver):
                            case buttons.B_START: mode <<= 2
                            case buttons.B_SETTINGS: mode <<= 1
                            case buttons.B_CREDITS:
                                assets.creditText.render()
                                mode <<= 6
                            case buttons.B_QUIT:
                                assets.sounds["bg_music"].stop()
                                pygame.quit()
                                sys.exit()
                    case modes.M_CREDITS:
                        assets.creditText.unload()
                        mode >>= 6
                    case modes.M_GAME:
                        over, apple = gameState.apples.mouseOver(mouse)
                        if (over):
                            assets.sounds["click"].play()
                            apple.isAffectedByGravity = True
                            apple.launch(randint(-60, 60), randint(-60, 60))
                    case modes.M_SETTINGS:
                        mouseOver = assets.menuSettings.get_mouse_over(mouse)
                        if (mouseOver in [buttons.B_PLUS, buttons.B_MINUS, buttons.B_MENU]):
                            assets.sounds["click"].play()

                        match(mouseOver):
                            case buttons.B_PLUS: settings.set_volume(settings.get_volume() + 0.05)
                            case buttons.B_VOLUME:
                                if (settings.get_volume() != 0):
                                    muteVol = settings.get_volume()
                                    settings.set_volume(0.0)
                                else:
                                    settings.set_volume(muteVol)

                            case buttons.B_MINUS: settings.set_volume(settings.get_volume() - 0.05)
                            case buttons.B_MENU: mode >>= 1
                        
                        setVolume()
                    case modes.M_GAMEOVER:
                        gameState.init(framerate)

                        mouseOver = assets.gameOverMenu.get_mouse_over(mouse)
                        if (mouseOver in [buttons.B_MENU, buttons.B_RETRY]):
                            assets.sounds["click"].play()

                        match (mouseOver):
                            case buttons.B_RETRY: mode >>= 3
                            case buttons.B_MENU: mode >>= 5
                    case modes.M_GAMEOVERSPLASH: mode <<= 1
            case pygame.MOUSEMOTION:
                match (mode):
                    case modes.M_MAIN: assets.mainMenu.hover(mouse) #Main Menu
                    case modes.M_SETTINGS: assets.menuSettings.hover(mouse) #Settings
                    case modes.M_GAMEOVER: assets.gameOverMenu.hover(mouse) #Game Over Menu
        
        pygame.display.update()
        await asyncio.sleep(0)
        clock.tick(framerate)

asyncio.run(main())