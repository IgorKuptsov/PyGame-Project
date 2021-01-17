import pygame as pg
from pygame.locals import *
import os
from config import *
import sys
from pygame import gfxdraw, K_w, K_a, K_d, K_UP, K_LEFT, K_RIGHT, K_ESCAPE, K_F4, K_p, K_RALT, K_LALT, K_SPACE, \
    MOUSEBUTTONDOWN, QUIT, KEYUP, KEYDOWN, K_TAB, K_v, K_h, K_BACKSPACE, K_q, K_m, K_r


def button(text, x, y, w, h, click, inactive_colour=BLUE, active_colour=LIGHT_BLUE, text_colour=WHITE):
    mouse = pg.mouse.get_pos()
    return_value = False
    if x < mouse[0] < x + w and y < mouse[1] < y + h:  # if mouse is hovering the button
        pg.draw.rect(screen, active_colour, (x, y, w, h))
        if click and pg.time.get_ticks() > 100: return_value = True
    else: pg.draw.rect(screen, inactive_colour, (x, y, w, h))

    text_surf, text_rect = text_objects(text, small_text, colour=text_colour)
    text_rect.center = (int(x + w / 2), int(y + h / 2))
    screen.blit(text_surf, text_rect)
    return return_value

def text_objects(text, font, colour=BLACK):
    text_surface = font.render(text, True, colour)
    return text_surface, text_surface.get_rect()

def window_init():
    # получаем размеры монитора
    # в pygame неудобно получать размер монитора, поэтому воспользуемся
    # другой библиотекой
    from tkinter import Tk
    temp = Tk()
    MONITOR_SIZE = temp.winfo_screenwidth(), temp.winfo_screenheight()
    temp.destroy()
    del temp

    # помещаем окно в центр экрана
    # это нужно сделать до того, как вы создадите окно
    screen_coords = ((MONITOR_SIZE[0] - WIN_SIZE.w) // 2, (MONITOR_SIZE[1] - WIN_SIZE.h) // 2)
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

    def __init__(self):
        pg.init()
        global screen
        self.is_running = True
        self.screen_bg = load_image('bg_test.jpg')
        self.all_sprites = pg.sprite.Group()
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
        # Creating objects, loading the level

    def load_level(self, level):
        #creating level
        exec(f'from levels.level{level} import *', globals())
        self.ladders = pg.sprite.Group()
        Ladder.ladders = self.ladders
        Ladder.all_sprites = self.all_sprites
        self.platforms = pg.sprite.Group()
        Platform.platforms = self.platforms
        Platform.all_sprites = self.all_sprites
        for obj, value in objects.items():
            if obj == 'Player':
                self.player = pg.sprite.Group()
                Player.player = self.player
                # TODO: get the current skin of the player from the file
                Player(load_image('animated_player_test.png', -1), *value)
            elif "Platform" in obj:
                Platform(*value)
            elif 'Ladder' in obj:
                Ladder(*value)
            elif 'Portal' in obj:
                Portal.all_sprites = self.all_sprites
                self.portal = Portal(*value)
                Portal.portal = self.portal
            # TODO: add enemies
            '''
            elif "Enemy" in obj:
                
            '''

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


def main_menu_setup():
    screen.fill(WHITE)
    text_surf, text_rect = text_objects('Название игры', menu_text)
    text_rect.center = (int(screen_width / 2), int(screen_height / 4))
    screen.blit(text_surf, text_rect)
    text_surf, text_rect = text_objects(f'v{VERSION}', small_text)
    text_rect.center = (int(screen_width * 0.98), int(screen_height * 0.98))
    screen.blit(text_surf, text_rect)
    pg.display.update()


def main_menu():
    main_menu_setup()
    start_game = view_hs = False
    while True:
        click = False
        pressed_keys = pg.key.get_pressed()
        for event in pg.event.get():
            alt_f4 = (event.type == KEYDOWN and (event.key == K_F4
                      and (pressed_keys[K_LALT] or pressed_keys[K_RALT])
                      or event.key == K_q or event.key == K_ESCAPE))
            if event.type == QUIT or alt_f4: sys.exit()
            elif event.type == KEYDOWN and event.key == K_SPACE: start_game = True
            elif event.type == KEYDOWN and (event.key == K_v or event.key == K_h): view_hs = True
            elif event.type == MOUSEBUTTONDOWN: click = True

        if button('Н А Ч А Т Ь  И Г Р У', *button_layout_4[0], click): start_game = True
        elif button('Р Е З У Л Ь Т А Т Ы', *button_layout_4[1], click) or view_hs:
            view_high_scores()
            view_hs = False
            main_menu_setup()
        elif button('Н А С Т Р О Й К И', *button_layout_4[2], click):
            settings_menu()
            main_menu_setup()
        elif button('В Ы Х О Д  И З  И Г Р Ы', *button_layout_4[3], click): sys.exit()
        if start_game:
            while start_game: start_game = Game().run() == 'Restart'
            main_menu_setup()
        pg.display.update(button_layout_4)
        clock.tick(60)


class AnimatedSprite(pg.sprite.Sprite):
    # TODO: set different animations for running right/left
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
        self.jumping_frames = 20
        self.counter = 0
        self.count = 0
        self.falling_acceleration = 1

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
        platform_above = False
        # Colliding with platforms
        sprites = pg.sprite.spritecollide(self, Platform.platforms, False, collided=collided)
        for sprite in sprites:
            if sprite.rect.y <= self.rect.bottom <= sprite.rect.y + PLATFORM_THICKNESS and not self.is_jumping and not \
                    self.is_climbing[0]:
                standing_on_platform = True
                self.rect.bottom = sprite.rect.top
            elif right and sprite.rect.x <= self.rect.right <= sprite.rect.right and not self.is_climbing[0]:
                directions['right'] = False
            elif left and sprite.rect.x <= self.rect.left <= sprite.rect.right and not self.is_climbing[0]:
                directions['left'] = False
            if sprite.rect.top <= self.rect.top <= sprite.rect.bottom and self.is_jumping:
                platform_above = True

        # Colliding with ladders
        sprites = pg.sprite.spritecollide(self, Ladder.ladders, False, collided=collided)
        for sprite in sprites:
            if sprite.rect.x - PLAYER_SIZE <= self.rect.x <= sprite.rect.right:
                self.is_climbing = True, sprite
                state = 'climb'
        if self.is_climbing[0]:
            if self.rect.y + PLAYER_SIZE < self.is_climbing[1].rect.y or self.is_climbing[1].rect.right < self.rect.x \
                    or self.rect.x < self.is_climbing[1].rect.x - PLAYER_SIZE:
                self.is_climbing = False, None
        # Colliding with portal
        if pg.sprite.collide_rect(self, Portal.portal):
            # TODO: смена уровня
            pass
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
        if self.is_jumping and not platform_above:
            speed_y -= self.count
            self.count -= 1
            if not self.count:
                self.is_jumping = False
        elif self.is_jumping and platform_above:
            self.is_jumping = False
            self.count = 0
        if standing_on_border or standing_on_platform:
            self.is_jumping = False
            if space and not self.is_climbing[0]:
                self.is_jumping = True
                self.count = self.jumping_frames
                state = 'jump'
        elif not self.is_climbing[0]:
            state = 'jump'
            speed_y += self.falling_acceleration
            if self.falling_acceleration == 1:
                self.falling_acceleration = 2
            elif self.falling_acceleration < 4:
                self.falling_acceleration = self.falling_acceleration ** 2
            else:
                self.falling_acceleration = 8

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


class Portal(pg.sprite.Sprite):
    all_sprites = None
    portal = None

    def __init__(self, x, y, w=PORTAL_SIZE[0], h=PORTAL_SIZE[1]):
        super().__init__()
        self.image = load_image('portal.jpg', None, w, h)
        self.rect = self.image.get_rect().move(x, y)
        self.add(self.all_sprites)
        # self.portal = self
        # self.add(self.portal)


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
    pg.init()
    screen = window_init()
    screen_width, screen_height = screen.get_size()
    BUTTON_WIDTH = int(screen_width * 0.625 // 3)
    BUTTON_HEIGHT = int(screen_height * 5 // 81)
    button_x_start = (screen_width - BUTTON_WIDTH) // 2
    button_layout_4 = [(button_x_start, screen_height * 5 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                       (button_x_start, screen_height * 6 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                       (button_x_start, screen_height * 7 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                       (button_x_start, screen_height * 8 // 13, BUTTON_WIDTH, BUTTON_HEIGHT)]
    clock = pg.time.Clock()
    menu_text = pg.font.SysFont('arial', int(110 / 1080 * screen_height))
    large_text = pg.font.SysFont('arial', int(40 / 1080 * screen_height))
    medium_text = pg.font.SysFont('arial', int(35 / 1440 * screen_height))
    small_text = pg.font.SysFont('arial', int(25 / 1440 * screen_height))
    hud_text = pg.font.SysFont('arial', int(40 / 1440 * screen_height)) 
    main_menu()
