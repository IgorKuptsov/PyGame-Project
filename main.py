import pygame as pg
from pygame.locals import *
import os

FPS = 60
PLAYER_SIZE = 32
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


# def load_image(name, color_key=None, bg=False):
#     fullname = os.path.join('data', name)
#     try:
#         image = pg.image.load(fullname).convert()
#     except pg.error as message:
#         # print('Cannot load image:', name)
#         raise SystemExit(message)
#     if color_key is not None:
#         if color_key == -1:
#             color_key = image.get_at((0, 0))
#         image.set_colorkey(color_key)
#     else:
#         image = image.convert_alpha()
#     if bg:
#         image = pg.transform.scale(image, WIN_SIZE.size)
#     else:
#         image = pg.transform.scale(image, (TILE_SIZE, TILE_SIZE))
#     return image


def load_image(name, color_key=None, size='bg'):
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
    if size == 'bg':
        image = pg.transform.scale(image, WIN_SIZE.size)
    elif size == 'player':
        image = pg.transform.scale(image, (PLAYER_SIZE, PLAYER_SIZE))
    return image


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
        Border(0, 0,
               WIN_SIZE.width, thickness)
        Border(0, WIN_SIZE.height - thickness,
               WIN_SIZE.width, thickness)
        Border(0, 0,
               thickness, WIN_SIZE.height)
        Border(WIN_SIZE.width - thickness, 0,
               thickness, WIN_SIZE.height)
        #
        # Player.hard_blocks = self.borders_vert
        #
        # self.screen = pg.display.set_mode(WIN_SIZE.size)
        self.clock = pg.time.Clock()

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
        # self.screen.fill(self.BG_COLOR)
        self.screen.blit(self.screen_bg, (0, 0))
        self.all_sprites.draw(self.screen)
        self.player.draw(self.screen)
        pg.display.update()

    def quit(self):
        pg.quit()


class Player(pg.sprite.Sprite):
    player = None

    # hard_blocks = None
    def __init__(self, img='player_test', x=5, y=WIN_SIZE.height - PLAYER_SIZE):
        super().__init__()
        self.idle_frames = []
        self.run_frames = []
        self.jump_frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.idle_frames[self.cur_frame]
        self.rect = self.image.get_rect().move(x, y)
        # self.rect = self.image.get_rect().move(0, 0)

        self.add(Player.player)
        self.speed = 5
        self.is_jumping = False
        # self.y = 5
        self.jump_frames = 15

    def update(self):
        speed_y = 0
        # defining keys
        keys = pg.key.get_pressed()
        left = keys[K_a] or keys[K_LEFT]
        right = keys[K_d] or keys[K_RIGHT]
        space = keys[K_SPACE]
        # x speed
        if left == right:
            speed_x = 0
        elif left:
            speed_x = -self.speed
        else:
            speed_x = self.speed
        self.rect.x += speed_x
        # y speed
        if self.is_jumping:
            self.count -= 1
            speed_y -= self.count
            if not self.count:
                self.is_jumping = False
        # TODO: в условие ниже добавить столкновение с платформами
        #  (or pg.sprite.spritecollideany(self, Platform.platforms))
        if pg.sprite.spritecollideany(self, Border.borders_hor):
            self.is_jumping = False
            if space:
                self.is_jumping = True
                self.count = self.jump_frames
        else:
            speed_y += g
        self.rect.y += speed_y
        # Colliding with vertical borders
        if self.rect.x < 0:
            self.rect.x = thickness
        elif self.rect.x + PLAYER_SIZE > WIN_SIZE.width:
            self.rect.x = WIN_SIZE.width - PLAYER_SIZE - thickness
        # Colliding with horizontal borders
        if self.rect.y + PLAYER_SIZE > WIN_SIZE.height:
            self.rect.y = WIN_SIZE.height - PLAYER_SIZE - thickness
        elif self.rect.y < 0:
            self.rect.y = thickness


class Border(pg.sprite.Sprite):
    all_sprites = None
    borders_hor = None
    borders_vert = None

    def __init__(self, x, y, w, h):
        super().__init__()
        # print(w, h)
        self.image = pg.Surface((w, h))
        self.rect = self.image.get_rect().move(x, y)
        self.add(Border.all_sprites)
        if h > w:
            self.add(Border.borders_vert)
        else:
            self.add(Border.borders_hor)


if __name__ == '__main__':
    Game().run()
