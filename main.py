import pygame as pg
from pygame.locals import *
import os

FPS = 60
PLAYER_SIZE = 75
PLATFORM_THICKNESS = 10
LADDER_WIDTH = 30
WIN_SIZE = pg.Rect(0, 0, 500, 500)
g = 2
thickness = 2


def window_init():
    # получаем размеры монитора
    # в pygame неудобно получать размер монитора, поэтому воспользуемся
    # другой библиотекой
    from tkinter import Tk
    temp = Tk()
    MONITOR_SIZE = temp.winfo_screenwidth(), temp.winfo_screenheight()
    temp.destroy()
    del temp

    # помещаем окно в верхний правый угол экрана
    # это нужно сделать до того, как вы создадите окно
    screen_coords = (MONITOR_SIZE[0] - WIN_SIZE.w - 50, 50)
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{screen_coords[0]}, {screen_coords[1]}"

    screen = pg.display.set_mode(WIN_SIZE.size)

    return screen


def load_image(name, color_key=None, w=WIN_SIZE.width, h=WIN_SIZE.height):
    fullname = os.path.join('data', name)
    try:
        image = pg.image.load(fullname).convert()
    except pg.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    image = pg.transform.scale(image, (w, h))
    return image


################################
def crossing_lines(a, b, c, d):
    return a <= c <= b or c <= a <= d


def collided_rects(rect1, rect2):
    return crossing_lines(rect1.x, rect1.right, rect2.x, rect2.right) and crossing_lines(rect1.y, rect1.bottom, rect2.y,
                                                                                         rect2.bottom)


def collided(sprite1, sprite2):
    return pg.sprite.collide_rect(sprite1, sprite2) or collided_rects(sprite1.rect, sprite2.rect)


###############################
class Game:
    BG_COLOR = pg.Color('blue')

    def __init__(self):
        pg.init()
        self.is_running = True
        self.screen = window_init()
        self.screen_bg = load_image('bg_test.jpg')
        self.all_sprites = pg.sprite.Group()
        # Creating the player
        self.player = pg.sprite.Group()
        Player.player = self.player
        Player(load_image('animated_player_test.png', -1))
        # Creating the borders
        self.borders_hor = pg.sprite.Group()
        self.borders_vert = pg.sprite.Group()
        self.balls = pg.sprite.Group()
        Border.all_sprites = self.all_sprites
        Border.borders_hor = self.borders_hor
        Border.borders_vert = self.borders_vert
        Border.bottom = Border(WIN_SIZE.width - thickness, 0, thickness, WIN_SIZE.height)
        Border(0, 0,
               WIN_SIZE.width, thickness)
        Border(0, WIN_SIZE.height - thickness,
               WIN_SIZE.width, thickness)
        Border(0, 0,
               thickness, WIN_SIZE.height)
        self.clock = pg.time.Clock()

        self.platforms = pg.sprite.Group()
        Platform.platforms = self.platforms
        Platform.all_sprites = self.all_sprites
        Platform(350, 300, 100)
        Platform(250, 300, 100)
        Platform(350, 450, 50)
        Platform(150, 500 - thickness - PLATFORM_THICKNESS, 100)
        Platform(100, 450, 100, h=100)

        self.ladders = pg.sprite.Group()
        Ladder.ladders = self.ladders
        Ladder.all_sprites = self.all_sprites
        Ladder(450, 300, LADDER_WIDTH, 200 - thickness)
        # Ladder(250, 300, LADDER_WIDTH, 200 - thickness)

    def run(self):
        while self.is_running:
            self.events()
            self.update()
            self.render()
        self.quit()

    def events(self):
        for event in pg.event.get():
            if event.type == QUIT:
                self.is_running = False
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    self.is_running = False

    def update(self):
        self.player.update()
        self.clock.tick_busy_loop(FPS)

    def render(self):
        self.screen.blit(self.screen_bg, (0, 0))
        self.all_sprites.draw(self.screen)
        self.player.draw(self.screen)
        pg.display.update()

    def quit(self):
        pg.quit()


class AnimatedSprite(pg.sprite.Sprite):
    def __init__(self, sheet, columns=7, rows=4, x=thickness, y=WIN_SIZE.height - thickness):
        super().__init__()
        self.climb_frames = []
        self.idle_frames = []
        self.run_frames = []
        self.jump_frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.idle_frames[self.cur_frame]
        self.rect = self.image.get_rect().move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pg.Rect(0, 0, sheet.get_width() // columns,
                            sheet.get_height() // rows)
        # climb row = 0, columns = 1
        frame = sheet.subsurface(pg.Rect((0, 0), self.rect.size))
        frame = pg.transform.scale(frame, (PLAYER_SIZE, PLAYER_SIZE))
        self.climb_frames.append(frame)
        # idle row = 1, columns = 4
        for i in range(4):
            frame_location = (self.rect.w * i, self.rect.h * 1)
            frame = sheet.subsurface(pg.Rect(frame_location, self.rect.size))
            frame = pg.transform.scale(frame, (PLAYER_SIZE, PLAYER_SIZE))
            self.idle_frames.append(frame)
        # run_frames row = 2, columns = 4
        for i in range(4):
            frame_location = (self.rect.w * i, self.rect.h * 2)
            frame = sheet.subsurface(pg.Rect(frame_location, self.rect.size))
            frame = pg.transform.scale(frame, (PLAYER_SIZE, PLAYER_SIZE))
            self.run_frames.append(frame)
        # jump_frames row = 3, columns = 7
        for i in range(7):
            frame_location = (self.rect.w * i, self.rect.h * 3)
            frame = sheet.subsurface(pg.Rect(frame_location, self.rect.size))
            frame = pg.transform.scale(frame, (PLAYER_SIZE, PLAYER_SIZE))
            self.jump_frames.append(frame)

    def update(self, state):
        frames = getattr(self, f'{state}_frames')
        self.cur_frame = (self.cur_frame + 1) % len(frames)
        self.image = frames[self.cur_frame]


class Player(AnimatedSprite):
    player = None

    # hard_blocks = None
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.add(Player.player)
        self.speed = 7
        self.is_jumping = False
        self.is_climbing = False, None
        self.jumping_frames = 15
        self.counter = 0
        self.count = 0

    def update(self, *args):
        # defining keys
        keys = pg.key.get_pressed()
        left = keys[K_a] or keys[K_LEFT]
        right = keys[K_d] or keys[K_RIGHT]
        up = keys[K_w] or keys[K_UP]
        down = keys[K_s] or keys[K_DOWN]
        space = keys[K_SPACE]
        state = 'idle'
        speed_y = 0
        speed_x = 0
        directions = {'right': True, 'left': True}
        standing_on_platform = False
        standing_on_border = self.rect.bottom >= Border.bottom.rect.x
        # Colliding with platforms
        sprites = pg.sprite.spritecollide(self, Platform.platforms, False, collided=collided)
        for sprite in sprites:
            if sprite.rect.y <= self.rect.bottom <= sprite.rect.y + PLATFORM_THICKNESS and not self.is_jumping and not self.is_climbing[0]:
                standing_on_platform = True
                self.rect.bottom = sprite.rect.top
            elif right and sprite.rect.x <= self.rect.right <= sprite.rect.right and not self.is_climbing[0]:
                directions['right'] = False
            elif left and sprite.rect.x <= self.rect.left <= sprite.rect.right and not self.is_climbing[0]:
                directions['left'] = False
            if sprite.rect.top <= self.rect.top <= sprite.rect.bottom and self.is_jumping:
                self.rect.top = sprite.rect.bottom

        # Colliding with ladders
        sprites = pg.sprite.spritecollide(self, Ladder.ladders, False, collided=collided)
        for sprite in sprites:
            if sprite.rect.x - PLAYER_SIZE <= self.rect.x <= sprite.rect.right:
                self.is_climbing = True, sprite
                state = 'climb'
        if self.is_climbing[0]:
            if self.rect.y + PLAYER_SIZE < self.is_climbing[1].rect.y or self.is_climbing[1].rect.right < self.rect.x or self.rect.x < self.is_climbing[1].rect.x - PLAYER_SIZE:
                self.is_climbing = False, None
        # x speed
        if left == right:
            speed_x = 0
        elif left and directions['left']:
            speed_x = -self.speed
            state = 'run'
        elif right and directions['right']:
            speed_x = self.speed
            state = 'run'
        self.rect.x += speed_x
        # y speed
        if self.is_jumping:
            speed_y -= self.count
            self.count -= 1
            if not self.count:
                self.is_jumping = False
        if standing_on_border or standing_on_platform:
            self.is_jumping = False
            if space and not self.is_climbing[0]:
                self.is_jumping = True
                self.count = self.jumping_frames
                state = 'jump'
        elif not self.is_climbing[0]:
            state = 'jump'
            speed_y += g

        if self.is_climbing[0]:
            if up and down:
                speed_y = 0
            # If the player is on the top of the ladder he can not climb up
            elif up and abs(self.is_climbing[1].rect.y - (self.rect.y + PLAYER_SIZE)) >= self.speed:
                speed_y = -self.speed
            elif up and abs(self.is_climbing[1].rect.y - (self.rect.y + PLAYER_SIZE)) < self.speed:
                speed_y = self.is_climbing[1].rect.y - self.rect.y - PLAYER_SIZE
            elif down:
                speed_y = self.speed

        self.rect.y += speed_y
        # Colliding with vertical borders
        if self.rect.x <= thickness:
            self.rect.x = thickness
        elif self.rect.x + PLAYER_SIZE >= WIN_SIZE.width - thickness:
            self.rect.x = WIN_SIZE.width - PLAYER_SIZE - thickness
        # Colliding with horizontal borders
        if self.rect.y + PLAYER_SIZE >= WIN_SIZE.height:
            self.rect.y = WIN_SIZE.height - PLAYER_SIZE - thickness
        elif self.rect.y <= thickness:
            self.rect.y = thickness
        if self.counter % 5 == 0:
            super().update(state)
        self.counter += 1


class Platform(pg.sprite.Sprite):
    all_sprites = None
    platforms = None

    def __init__(self, x, y, w, h=PLATFORM_THICKNESS):
        super().__init__()
        self.image = load_image('platform.png', -1, w, h)
        self.rect = self.image.get_rect().move(x, y)
        self.add(self.all_sprites)
        self.add(self.platforms)


class Ladder(pg.sprite.Sprite):
    all_sprites = None
    ladders = None

    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = load_image('ladder.png', None, w, h)
        self.rect = self.image.get_rect().move(x, y)
        self.add(self.all_sprites)
        self.add(self.ladders)


class Border(pg.sprite.Sprite):
    all_sprites = None
    borders_hor = None
    borders_vert = None
    bottom = None

    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pg.Surface((w, h))
        self.rect = self.image.get_rect().move(x, y)
        self.add(Border.all_sprites)
        if h > w:
            self.add(Border.borders_vert)
        else:
            self.add(Border.borders_hor)


if __name__ == '__main__':
    Game().run()
