import pygame,os.path

from pygame.locals import *

#constants
FRAMES_PER_SEC = 40
PLAYER_SPEED = 12

SCREENRECT = Rect(0, 0, 640, 480)

update_img = []
class Img : pass

main_dir = os.path.split(os.path.abspath(__file__))[0]  # Program's diretory


def load_image(file, transparent):
    file = os.path.join(main_dir, 'images', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s' %
                         (file, pygame.get_error()))
    if transparent:
        corner = surface.get_at((0, 0))
        surface.set_colorkey(corner, RLEACCEL)
    return surface.convert()


class GameException(Exception):
    pass

class Settings(object):
    def __init__(self):
            self.background = (48,121,4)
            self.title = "BOMBERMAN"

class Actor:
    def __init__(self, image):
        self.image = image
        self.rect = image.get_rect()

    def update(self):
        pass

    def draw(self, screen):
        r = screen.blit(self.image, self.rect)
        update_img.append(r)

    def erase(self, screen, background):
        r = screen.blit(background, self.rect, self.rect)
        update_img.append(r)

class Bomberman(Actor):
    def __init__(self):
        Actor.__init__(self, Img.player)
        self.rect.move_ip(48,48)

    def move(self, direction):
        if direction == 0:
            self.rect = self.rect
        elif direction == 1:
            self.rect = self.rect.move(0,PLAYER_SPEED).clamp(SCREENRECT)
        elif direction == 2:
            self.rect = self.rect.move(PLAYER_SPEED,0).clamp(SCREENRECT)
        elif direction == 3:
            self.rect = self.rect.move(0,-PLAYER_SPEED).clamp(SCREENRECT)
        else:
            self.rect = self.rect.move(-PLAYER_SPEED,0).clamp(SCREENRECT)

class Unbreakable(Actor):
    def __init__(self,x,y):
        Actor.__init__(self,Img.unbreakable_wall)
        self.rect.move_ip(x,y)

class Breakable(Actor):
    def __init__(self,x,y):
        Actor.__init__(self,Img.breakable_wall)
        self.rect.move_ip(x,y)

class Bomb(Actor):
    def __init__(self,x,y):
        Actor.__init__(self,Img.bomb)
        self.rect.move_ip(x,y)
        self.ttl = 5

class Game(object):
    global update_img

    def __init__(self,settings = Settings()):
            pygame.init() 
            self.map = [[1,1,1,1,1,1,1,1,1,1],
                        [1,0,0,2,2,2,2,2,0,1],
                        [1,0,1,2,1,2,1,0,0,1],
                        [1,0,2,2,2,2,2,2,2,1],
                        [1,2,2,2,2,2,2,2,2,1],
                        [1,2,2,2,2,2,2,2,2,1],
                        [1,2,2,2,2,2,2,2,2,1],
                        [1,2,2,2,2,2,2,2,2,1],
                        [1,2,2,2,2,2,2,2,2,2],
                        [1,1,1,1,1,1,1,1,1,1]]
            self.init_from_settings(settings)
            self.clock = pygame.time.Clock()

    def init_from_settings(self,settings):

        #init screen
        self.screen = pygame.display.set_mode(SCREENRECT.size, 0)
        pygame.display.set_caption(settings.title)
        pygame.key.set_repeat(10,10)
        #init background
        background = pygame.Surface(self.screen.get_size())
        self.background = background.convert()
        self.background.fill(settings.background)
         
        #load images
        Img.player = load_image('om.png', 1)
        Img.unbreakable_wall = load_image('zidind.png',1)
        Img.breakable_wall = load_image('ziddes.png',1)
        Img.bomb = load_image('bomba.png',1)
        self.walls = []
        size = 10
        for i in range(size):
            for j in range(size):
                if self.map[j][i] == 1:
                    wall = Unbreakable(i*48,j*48)
                    wall.draw(self.screen)
                    self.walls.append(wall)
                elif self.map[j][i] == 2:
                    wall = Breakable(i*48,j*48)
                    wall.draw(self.screen)
                    self.walls.append(wall)

        self.screen.blit(self.background, (0,0))
        pygame.display.flip()

        self.player = Bomberman()
        self.player_x = self.player.rect.top/48;
        self.player_y = self.player.rect.left/48;

    def run(self):
        while True:
            try:
                self.game_tick()
            except GameException:
                return

    def game_tick(self):
        global update_img 
        self.clock.tick(FRAMES_PER_SEC)
        #for elem in self.walls:
        #    elem.erase(self.screen, self.background)
        #    elem.update()
        self.player.erase(self.screen, self.background)
        self.player.update()
        direction = 0
        top = self.player.rect.top
        bottom = self.player.rect.bottom
        left = self.player.rect.left
        right = self.player.rect.right
        for event in pygame.event.get():
            if event.type == QUIT:
                raise GameException
            elif event.type == pygame.KEYDOWN:
                if event.key == K_UP and self.map[(top-12)/48][left/48] == 0 and self.map[(top-12)/48][(right-1)/48] == 0:
                    direction = 3
                elif event.key == K_DOWN and self.map[(bottom+11)/48][left/48] == 0 and self.map[(bottom+11)/48][(right-1)/48] == 0:
                    direction = 1
                elif event.key == K_RIGHT and self.map[top/48][(right+11)/48] == 0 and self.map[(bottom-1)/48][(right+11)/48] == 0:
                    direction = 2
                elif event.key == K_LEFT and self.map[top/48][(left-12)/48] == 0 and self.map[(bottom-1)/48][(left-12)/48] == 0:
                    direction = 4
    
        self.player.move(direction)
        self.player_x = self.player.rect.centerx/48
        self.player_y = self.player.rect.centery/48
        for elem in self.walls:
            elem.draw(self.screen) 
        self.player.draw(self.screen)             
        pygame.display.update(update_img)
        update_img = [] 
