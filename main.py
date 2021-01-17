import pygame as pg
from pygame.locals import *
import os

FPS = 60
PLAYER_SIZE = 50
PLATFORM_THICKNESS = 10
LADDER_WIDTH = 30
PORTAL_SIZE = 50, 100
BULLET_SIZE = 15, 7
WIN_SIZE = pg.Rect(0, 0, 500, 500)
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
    BG_COLOR = pg.Color('blue')

    def __init__(self):
        pg.init()
        self.is_running = True
        self.screen = window_init()
        self.screen_bg = load_image('bg_test.jpg')
        self.all_sprites = pg.sprite.Group()
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

        self.ladders = pg.sprite.Group()
        Ladder.ladders = self.ladders
        Ladder.all_sprites = self.all_sprites
        Ladder(100 - LADDER_WIDTH, 310, LADDER_WIDTH, 498 - 310)

        Portal.all_sprites = self.all_sprites
        self.portal = Portal(200 - PORTAL_SIZE[0], 310 - PORTAL_SIZE[1])
        Portal.portal = self.portal

        # Platform(200, 400 - thickness - PLATFORM_THICKNESS, 200)
        # Platform(200, 500 - thickness - 100, 200, h=100)
        Platform(100, 310, 100, h=100)
        Platform(200, 400, 100)
        Platform(200, 310, 100)
        # Platform(400, 500 - thickness - 100, 100, h=100)
        Platform(500 - 200 - thickness, 423, 200)

        # Creating the player
        self.player_sprite = pg.sprite.Group()
        Player.player = self.player_sprite
        # self.player = Player(load_image('animated_player_test2.png', -1), x=200, y=320)
        self.player = Player(load_image('player14.png', -1), x=200, y=320)

        self.enemies = pg.sprite.Group()
        Enemy.enemies = self.enemies
        Enemy.all_sprites = self.all_sprites
        Enemy(load_image('enemy2.png', -1), x=500 - 100 - 2, y=423 - PLAYER_SIZE,
              movement_type='idle')
        Enemy.player = self.player

        self.bullets = pg.sprite.Group()
        Bullet.bullets = self.bullets
        Bullet.all_sprites = self.all_sprites
        Bullet(10, 10)

        self.transparency = 0
        self.black_surface = pg.Surface(self.screen.get_size())
        self.black_surface.fill((0, 0, 0))
        self.death_image = pg.Surface((350, 200), pg.SRCALPHA)
        self.death_image.blit(load_image('dead_text.png', -1, 350, 100), (0, 100))
        self.death_image.blit(load_image('you_died.png', -1, 350, 75), (0, 0))

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
                if event.key == K_ESCAPE and not self.player.is_alive:
                    # TODO: выйти в меню выбора уровней
                    print('menu')
                    # self.is_running = False
                if event.key == K_RETURN:
                    # TODO: Загрузить текущий уровень
                    print('reloading current level')

    def update(self):
        if self.player.is_alive:
            self.player_sprite.update()
            self.enemies.update()
        self.clock.tick_busy_loop(FPS)

    def render(self):
        self.screen.blit(self.screen_bg, (0, 0))
        self.all_sprites.draw(self.screen)
        self.player_sprite.draw(self.screen)
        if not self.player.is_alive:
            self.black_surface.set_alpha(self.transparency)
            self.death_image.set_alpha(self.transparency + 50)
            self.screen.blit(self.black_surface, (0, 0))
            self.screen.blit(self.death_image, (WIN_SIZE.width // 2 - self.death_image.get_width() // 2,
                                                WIN_SIZE.height // 2 - self.death_image.get_height() // 2))
            if self.transparency <= 200:
                self.transparency += 1
        pg.display.update()

    def quit(self):
        pg.quit()


class AnimatedSprite(pg.sprite.Sprite):
    def __init__(self, sheet, columns=7, rows=7, x=thickness, y=WIN_SIZE.height - thickness):
        super().__init__()
        # self.climb_frames = []
        self.climb_right_frames = []
        self.climb_left_frames = []
        # self.idle_frames = []
        self.idle_right_frames = []
        self.idle_left_frames = []
        self.run_left_frames = []
        self.run_right_frames = []
        # self.jump_frames = []
        self.jump_right_frames = []
        self.jump_left_frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.idle_right_frames[self.cur_frame]
        self.rect = self.image.get_rect().move(x, y)
        self.watching_dir = 'right'
        # self.watching_right, self.watching_left = True, False

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pg.Rect(0, 0, sheet.get_width() // columns,
                            sheet.get_height() // rows)
        # climb_right_frames
        frame = sheet.subsurface(pg.Rect((0, 0), self.rect.size))
        rect = frame.get_bounding_rect()
        frame = frame.subsurface(rect)
        frame = pg.transform.scale(frame, (PLAYER_SIZE, PLAYER_SIZE))
        self.climb_right_frames.append(frame)
        # climb_left_frames
        frame = sheet.subsurface(pg.Rect((self.rect.width, 0), self.rect.size))
        rect = frame.get_bounding_rect()
        frame = frame.subsurface(rect)
        frame = pg.transform.scale(frame, (PLAYER_SIZE, PLAYER_SIZE))
        self.climb_left_frames.append(frame)
        # idle_right row = 1, columns = 4
        for i in range(4):
            frame_location = (self.rect.w * i, self.rect.h * 1)
            frame = sheet.subsurface(pg.Rect(frame_location, self.rect.size))
            rect = frame.get_bounding_rect()
            frame = frame.subsurface(rect)
            frame = pg.transform.scale(frame, (PLAYER_SIZE, PLAYER_SIZE))
            self.idle_right_frames.append(frame)
        # run_right_frames row = 2, columns = 4
        for i in range(4):
            frame_location = (self.rect.w * i, self.rect.h * 2)
            frame = sheet.subsurface(pg.Rect(frame_location, self.rect.size))
            rect = frame.get_bounding_rect()
            frame = frame.subsurface(rect)
            frame = pg.transform.scale(frame, (PLAYER_SIZE, PLAYER_SIZE))
            self.run_right_frames.append(frame)
        # jump_right_frames row = 3, columns = 7
        for i in range(7):
            frame_location = (self.rect.w * i, self.rect.h * 3)
            frame = sheet.subsurface(pg.Rect(frame_location, self.rect.size))
            rect = frame.get_bounding_rect()
            frame = frame.subsurface(rect)
            frame = pg.transform.scale(frame, (PLAYER_SIZE, PLAYER_SIZE))
            self.jump_right_frames.append(frame)
        # run_left_frames row = 4, columns = 4
        for i in range(4):
            frame_location = (self.rect.w * i, self.rect.h * 4)
            frame = sheet.subsurface(pg.Rect(frame_location, self.rect.size))
            rect = frame.get_bounding_rect()
            frame = frame.subsurface(rect)
            frame = pg.transform.scale(frame, (PLAYER_SIZE, PLAYER_SIZE))
            self.run_left_frames.append(frame)
        # idle_left row = 5, columns = 4
        for i in range(4):
            frame_location = (self.rect.w * i, self.rect.h * 5)
            frame = sheet.subsurface(pg.Rect(frame_location, self.rect.size))
            rect = frame.get_bounding_rect()
            frame = frame.subsurface(rect)
            frame = pg.transform.scale(frame, (PLAYER_SIZE, PLAYER_SIZE))
            self.idle_left_frames.append(frame)
        # jump_left_frames row = 6, columns = 7
        for i in range(7):
            frame_location = (self.rect.w * i, self.rect.h * 6)
            frame = sheet.subsurface(pg.Rect(frame_location, self.rect.size))
            rect = frame.get_bounding_rect()
            frame = frame.subsurface(rect)
            frame = pg.transform.scale(frame, (PLAYER_SIZE, PLAYER_SIZE))
            self.jump_left_frames.append(frame)

    def update(self, state):
        frames = getattr(self, f'{state}_frames')
        self.cur_frame = (self.cur_frame + 1) % len(frames)
        self.image = frames[self.cur_frame]
        # this is showing sprite's rect for debugging
        # rect = pg.Surface(self.rect.size, pg.SRCALPHA)
        # rect.set_alpha(10)
        # pg.draw.rect(rect, (255, 0, 0), (0, 0, rect.get_width(), rect.get_height()), 1)
        # self.image.blit(rect, (0, 0))


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
        self.is_alive = True

    def die(self):
        # return 1
        self.is_alive = False

    def update(self, *args):
        # Colliding with enemies
        if pg.sprite.spritecollideany(self, Enemy.enemies, collided=collided):
            self.die()
            return None
        # defining keys
        keys = pg.key.get_pressed()
        left = keys[K_a] or keys[K_LEFT]
        right = keys[K_d] or keys[K_RIGHT]
        up = keys[K_w] or keys[K_UP]
        down = keys[K_s] or keys[K_DOWN]
        space = keys[K_SPACE]
        # state = 'idle'
        speed_y = 0
        speed_x = 0
        directions = {'right': True, 'left': True}
        standing_on_platform = False
        standing_on_border = self.rect.bottom >= Border.bottom.rect.x
        platform_above = False
        if right:
            self.watching_dir = 'right'
        elif left:
            self.watching_dir = 'left'
        state = f'idle_{self.watching_dir}'
        # Colliding with platforms
        sprites = pg.sprite.spritecollide(self, Platform.platforms, False, collided=collided)
        for sprite in sprites:
            if sprite.rect.y <= self.rect.bottom <= sprite.rect.y + PLATFORM_THICKNESS and not self.is_climbing[0]:
                standing_on_platform = True
                self.rect.bottom = sprite.rect.top
            elif sprite.rect.x <= self.rect.right <= sprite.rect.right and not self.is_climbing[0]:
                directions['right'] = False
            elif sprite.rect.x <= self.rect.left <= sprite.rect.right and not self.is_climbing[0]:
                directions['left'] = False
            if (sprite.rect.top <= self.rect.top <= sprite.rect.bottom < self.rect.bottom) \
                    or (self.rect.top < sprite.rect.top and self.rect.bottom > sprite.rect.bottom) \
                    and self.is_jumping:
                platform_above = True
        # Colliding with ladders
        sprites = pg.sprite.spritecollide(self, Ladder.ladders, False, collided=collided)
        for sprite in sprites:
            if sprite.rect.x - PLAYER_SIZE <= self.rect.x <= sprite.rect.right:
                self.is_climbing = True, sprite
                state = f'climb_{self.watching_dir}'
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
            state = 'run_left'
        elif right and directions['right']:
            speed_x = self.speed
            state = 'run_right'
        elif left:
            # TODO: state = run_left
            state = 'run_left'
        elif right:
            # TODO: state = run_right
            state = 'run_right'
        self.rect.x += speed_x
        # y speed
        if self.is_jumping and not platform_above:
            speed_y -= self.count
            self.count -= 1
            if not self.count:
                self.is_jumping = False
        elif self.is_jumping and platform_above:
            self.is_jumping = False
        if standing_on_border or standing_on_platform:
            self.falling_acceleration = 1
            self.is_jumping = False
            if space and not self.is_climbing[0]:
                self.is_jumping = True
                self.count = self.jumping_frames
                # state = 'jump'
                state = f'jump_{self.watching_dir}'
        elif not self.is_climbing[0]:
            state = f'jump_{self.watching_dir}'
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
        self.image = load_image('platform1.png', None, w, h)
        self.rect = self.image.get_rect().move(x, y)
        self.add(self.all_sprites)
        self.add(self.platforms)


class Ladder(pg.sprite.Sprite):
    all_sprites = None
    ladders = None

    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = load_image('ladder2.png', -1, w, h)
        self.rect = self.image.get_rect().move(x, y)
        self.add(self.all_sprites)
        self.add(self.ladders)


class Portal(pg.sprite.Sprite):
    all_sprites = None
    portal = None

    def __init__(self, x, y, w=PORTAL_SIZE[0], h=PORTAL_SIZE[1]):
        super().__init__()
        self.image = load_image('portal1.png', -1, w, h)
        self.rect = self.image.get_rect().move(x, y)
        self.add(self.all_sprites)


class Enemy(Player):
    all_sprites = None
    enemies = None
    player = None

    def __init__(self, *args, movement_type='idle', weapon='no', movement_x=0, **kwargs):
        AnimatedSprite.__init__(self, *args, **kwargs)
        self.speed = 3
        self.movement_type = movement_type
        self.weapon = weapon
        self.dir = 'right'
        self.enemy_platform()
        self.movement_x = movement_x
        self.delta_x = 0
        self.add(self.all_sprites)
        self.add(self.enemies)
        self.counter = 0

    def update(self):
        if self.player.rect.x < self.rect.x and self.movement_type == 'idle':
            self.watching_dir = 'left'
        elif self.player.rect.x > self.rect.x and self.movement_type == 'idle':
            self.watching_dir = 'right'
        state = f'idle_{self.watching_dir}'
        # Movement type
        if self.movement_type == 'idle':
            pass
        elif self.movement_type == 'along_platform':
            if self.dir == 'right' and self.rect.right < self.platform.rect.right:
                self.rect.x += self.speed
            elif self.dir == 'right' and self.rect.right >= self.platform.rect.right:
                self.change_dir()
            elif self.dir == 'left' and self.rect.left > self.platform.rect.left:
                self.rect.x -= self.speed
            elif self.dir == 'left' and self.rect.left <= self.platform.rect.left:
                self.change_dir()
            state = f'run_{self.watching_dir}'
            # if self.dir == 'right':
            #     state = 'run_right'
            # else:
            #     state = 'run_left'
        elif self.movement_type == 'in_range':
            if self.dir == 'right' and self.delta_x + self.speed < self.movement_x:
                self.rect.x += self.speed
                self.delta_x += self.speed
            elif self.dir == 'right' and self.delta_x + self.speed >= self.movement_x:
                self.change_dir()
            elif self.dir == 'left' and self.delta_x - self.speed > -self.movement_x:
                self.rect.x -= self.speed
                self.delta_x -= self.speed
            elif self.dir == 'left' and self.delta_x - self.speed <= -self.movement_x:
                self.change_dir()
            state = f'run_{self.watching_dir}'
            # if self.dir == 'right':
            #     state = 'run_right'
            # else:
            #     state = 'run_left'
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
            AnimatedSprite.update(self, state)
        self.counter += 1

    def enemy_platform(self):
        if self.movement_type == 'along_platform':
            platform = pg.sprite.spritecollide(self, Platform.platforms, False, collided=collided)[0]
            self.platform = platform

    def change_dir(self):
        self.dir = 'left' if self.dir == 'right' else 'right'


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


class Bullet(pg.sprite.Sprite):
    all_sprites = None
    bullets = None

    def __init__(self, x, y, *args, w=BULLET_SIZE[0], h=BULLET_SIZE[1], **kwargs):
        super().__init__()
        self.image = load_image('bullet.png', -1, w, h)
        self.rect = self.image.get_rect().move(x, y)
        self.add(self.all_sprites)
        self.add(self.bullets)


if __name__ == '__main__':
    Game().run()
