import pygame as pg
from pygame.locals import *
import os
from config import *
import sys
from pygame import gfxdraw, K_w, K_a, K_d, K_UP, K_LEFT, K_RIGHT, K_ESCAPE, K_F4, K_p, K_RALT, K_LALT, K_SPACE, \
    MOUSEBUTTONDOWN, QUIT, KEYUP, KEYDOWN, K_TAB, K_v, K_h, K_BACKSPACE, K_q, K_m, K_r


def get_acting_level():
    with open('levels/level_acting.txt', 'r', encoding="utf-8") as file:
        return file.read()


def change_acting_level(level):
    with open('levels/level_acting.txt', 'w') as file:
        file.write(level)


def button(text, x, y, w, h, click, inactive_colour=GREEN, active_colour=LIGHT_GREEN, text_colour=BLACK):
    mouse = pg.mouse.get_pos()
    return_value = False
    if x < mouse[0] < x + w and y < mouse[1] < y + h:  # if mouse is hovering the button
        pg.draw.rect(screen, active_colour, (x, y, w, h))
        if click and pg.time.get_ticks() > 100: return_value = True
    else:
        pg.draw.rect(screen, inactive_colour, (x, y, w, h))

    text_surf, text_rect = text_objects(text, small_text, colour=text_colour)
    text_rect.center = (int(x + w / 2), int(y + h / 2))
    screen.blit(text_surf, text_rect)
    return return_value


def text_objects(text, font, colour=BLACK):
    text_surface = font.render(text, True, colour)
    return text_surface, text_surface.get_rect()


def window_init():
    # получаем размеры монитора
    # в pg неудобно получать размер монитора, поэтому воспользуемся
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


def change_level(new_level):
    level = new_level


def crossing_lines(a, b, c, d):
    return a <= c <= b or c <= a <= d


def collided_rects(rect1, rect2):
    return crossing_lines(rect1.x, rect1.right, rect2.x, rect2.right) and crossing_lines(rect1.y, rect1.bottom, rect2.y,
                                                                                         rect2.bottom)


def collided(sprite1, sprite2):
    return pg.sprite.collide_rect(sprite1, sprite2) or collided_rects(sprite1.rect, sprite2.rect)


def bg_music(name='Fantasy_Game_Background.mp3'):
    fullname = os.path.join('data', name)
    pg.mixer.music.load(fullname)
    pg.mixer.music.set_volume(0.12)
    pg.mixer.music.play(-1, fade_ms=1500)


class Game:
    def __init__(self):
        pg.init()
        global screen
        self.is_running = True
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

        self.transparency = 0
        self.black_surface = pg.Surface(screen.get_size())
        self.black_surface.fill((0, 0, 0))
        self.death_image = pg.Surface((350, 200), pg.SRCALPHA)
        self.death_image.blit(load_image('dead_text.png', -1, 350, 100), (0, 100))
        self.death_image.blit(load_image('you_died.png', -1, 350, 75), (0, 0))
        self.victory_image = pg.Surface((350, 200), pg.SRCALPHA)
        self.victory_image.blit(load_image('victory_text.png', -1, 250, 50), (50, 100))
        self.victory_image.blit(load_image('victory.png', -1, 300, 75), (25, 0))
        if SOUNDS['background']:
            bg_music()

        if get_acting_level() != "7":
            self.load_level(get_acting_level())

    def load_level(self, level):
        # creating level
        exec(f'from levels.level{level} import *', globals())

        self.ladders = pg.sprite.Group()
        Ladder.ladders = self.ladders
        Ladder.all_sprites = self.all_sprites

        self.platforms = pg.sprite.Group()
        Platform.platforms = self.platforms
        Platform.all_sprites = self.all_sprites

        self.enemies = pg.sprite.Group()
        Enemy.enemies = self.enemies
        Enemy.all_sprites = self.all_sprites

        for obj, value in objects.items():
            # Creating the player
            if obj == 'Player':
                self.player_sprite = pg.sprite.Group()
                Player.player = self.player_sprite
                self.player = Player(load_image('player14.png', -1), *value)
            # creating platform
            elif "Platform" in obj:
                Platform(*value)
            # creating Ladder
            elif 'Ladder' in obj:
                Ladder(*value)
            # creating portal
            elif 'Portal' in obj:
                Portal.all_sprites = self.all_sprites
                self.portal = Portal(*value)
                Portal.portal = self.portal
            # creating enemy
            elif "Enemy" in obj:
                Enemy(load_image('enemy2.png', -1), x=value['x'], y=value['y'], movement_type=value['movement_type'])
                Enemy.player = self.player

    def run(self):
        while self.is_running:
            self.events()
            self.update()
            self.render()
        return False

    def events(self):
        for event in pg.event.get():
            if event.type == QUIT:
                self.is_running = False
                main_menu()
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    self.is_running = False
                    pg.mixer.music.stop()
                    main_menu()
                if event.key == K_ESCAPE and not self.player.is_alive:
                    main_menu()
                if event.key == K_RETURN and not self.player.is_alive:
                    self.is_running = False
                    Game().run()
                if event.key == K_RETURN and self.player.victory:
                    main_menu()

    def update(self):
        if self.player.is_alive and not self.player.victory:
            self.player_sprite.update()
            self.enemies.update()
        self.clock.tick_busy_loop(FPS)

    def render(self):
        screen.blit(self.screen_bg, (0, 0))
        self.all_sprites.draw(screen)
        self.player_sprite.draw(screen)
        if not self.player.is_alive:
            self.black_surface.set_alpha(self.transparency)
            self.death_image.set_alpha(self.transparency + 50)
            screen.blit(self.black_surface, (0, 0))
            screen.blit(self.death_image, (WIN_SIZE.width // 2 - self.death_image.get_width() // 2,
                                           WIN_SIZE.height // 2 - self.death_image.get_height() // 2))
            if self.transparency <= 200:
                self.transparency += 2
        elif self.player.victory:
            self.black_surface.set_alpha(self.transparency)
            self.victory_image.set_alpha(self.transparency + 50)
            screen.blit(self.black_surface, (0, 0))
            screen.blit(self.victory_image, (WIN_SIZE.width // 2 - self.victory_image.get_width() // 2,
                                             WIN_SIZE.height // 2 - self.victory_image.get_height() // 2))
            if self.transparency <= 200:
                self.transparency += 2
        pg.display.update()

    def quit(self):
        pg.quit()


def draw_circle(surface, x, y, radius, color):
    gfxdraw.aacircle(surface, x, y, radius, color)
    gfxdraw.filled_circle(surface, x, y, radius, color)


def toggle_btn(text, x, y, w, h, click, text_colour=BLACK, enabled=True, draw_toggle=True, blit_text=True,
               enabled_color=LIGHT_GREEN, disabled_color=GREY):
    mouse = pg.mouse.get_pos()
    rect_height = h // 2
    if rect_height % 2 == 0: rect_height += 1
    # включенное состояние кнпки
    if enabled and draw_toggle:
        pg.draw.rect(screen, WHITE, (x + TOGGLE_WIDTH - h // 4, y, TOGGLE_ADJ + h, rect_height))
        pg.draw.rect(screen, enabled_color, (x + TOGGLE_WIDTH, y, TOGGLE_ADJ, rect_height))
        draw_circle(screen, int(x + TOGGLE_WIDTH), y + h // 4, h // 4, enabled_color)
        draw_circle(screen, int(x + TOGGLE_WIDTH + TOGGLE_ADJ), y + h // 4, h // 4, enabled_color)
        draw_circle(screen, int(x + TOGGLE_WIDTH + TOGGLE_ADJ), y + h // 4, h // 5, WHITE)  # small inner circle
    # выключенное состояние кнопки
    elif draw_toggle:
        pg.draw.rect(screen, WHITE, (x + TOGGLE_WIDTH - h // 4, y, TOGGLE_ADJ + h, rect_height))
        pg.draw.rect(screen, disabled_color, (x + TOGGLE_WIDTH, y, TOGGLE_ADJ, rect_height))
        draw_circle(screen, int(x + TOGGLE_WIDTH), y + h // 4, h // 4, disabled_color)
        draw_circle(screen, int(x + TOGGLE_WIDTH + TOGGLE_ADJ), y + h // 4, h // 4, disabled_color)
        draw_circle(screen, int(x + TOGGLE_WIDTH), y + h // 4, h // 5, WHITE)  # small inner circle
    # написание текста для кнопки
    if blit_text:
        text_surf, text_rect = text_objects(text, medium_text, colour=text_colour)
        text_rect.topleft = (x, y)
        screen.blit(text_surf, text_rect)
    return x < mouse[0] < x + w and y < mouse[1] < y + h and click and pg.time.get_ticks() > 100


def main_menu():
    screen.fill(WHITE)
    text_surf, text_rect = text_objects('Платформы и лестницы', menu_text)
    text_rect.center = (int(screen_width / 2), int(screen_height / 4))
    screen.blit(text_surf, text_rect)
    text_surf, text_rect = text_objects(f'v{VERSION}', small_text)
    text_rect.center = (int(screen_width * 0.98), int(screen_height * 0.98))
    screen.blit(text_surf, text_rect)
    pg.display.update()
    view_level = False
    while True:
        click = False
        pressed_keys = pg.key.get_pressed()
        for event in pg.event.get():
            alt_f4 = (event.type == KEYDOWN and (event.key == K_F4
                                                 and (pressed_keys[K_LALT] or pressed_keys[K_RALT])
                                                 or event.key == K_q or event.key == K_ESCAPE))
            if event.type == QUIT or alt_f4:
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                view_level = True
            elif event.type == MOUSEBUTTONDOWN:
                click = True

        if button('Н А Ч А Т Ь  И Г Р У', *button_layout_main_menu[0], click):
            view_level = True
        elif button('И Н С Т Р У К Ц И Я', *button_layout_main_menu[1], click):
            view_instruct()
            main_menu()

        elif button('Н А С Т Р О Й К И', *button_layout_main_menu[2], click):
            settings_menu()
            main_menu()
        elif button('В Ы Х О Д  И З  И Г Р Ы', *button_layout_main_menu[3], click):
            sys.exit()
        if view_level:
            level = menu_level()
            if level:
                change_acting_level(str(level))
                screen.fill(WHITE)
                if not Game().run():
                    main_menu()
            else:
                main_menu()
        pg.display.update(button_layout_main_menu)
        clock.tick(60)


def settings_menu():
    global SOUNDS
    screen.fill(WHITE)
    text_surf, text_rect = text_objects('Настройки', menu_text)
    text_rect.center = ((screen_width // 2), (screen_height // 4))
    screen.blit(text_surf, text_rect)
    pg.display.update()
    first_run = draw_bg_toggle = draw_jump_toggle = draw_player_toggle = True
    while True:
        click = False
        pressed_keys = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == MOUSEBUTTONDOWN:
                click = True
        if toggle_btn('Музыка', *button_layout_main_menu[0], click, enabled=SOUNDS['background'],
                      draw_toggle=draw_bg_toggle, blit_text=first_run):
            SOUNDS['background'] = not SOUNDS['background']
            draw_bg_toggle = True
        elif toggle_btn('SFX', *button_layout_main_menu[1], click, enabled=SOUNDS['player'],
                        draw_toggle=draw_jump_toggle, blit_text=first_run):
            SOUNDS['player'] = not SOUNDS['player']
            draw_player_toggle = True
        elif button("Н А З А Д", *button_layout_main_menu[3], click):
            main_menu()

        pg.display.update(button_layout_main_menu)
        clock.tick(60)


def view_instruct():
    global SOUNDS
    screen.fill(WHITE)
    text_surf, text_rect = text_objects('Инструкция', menu_text)
    text_rect.center = ((screen_width // 2), (screen_height // 10))
    screen.blit(text_surf, text_rect)
    instruction_img = load_image('instruction.png', -1, 490, 200)
    screen.blit(instruction_img, (10, 100))

    pg.display.update()

    while True:
        click = False
        pressed_keys = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == MOUSEBUTTONDOWN:
                click = True
        if button("Н А З А Д", *button_layout_main_menu[3], click):
            main_menu()

        pg.display.update(button_layout_main_menu)
        clock.tick(60)


def menu_level():
    screen.fill(WHITE)
    text_surf, text_rect = text_objects('Уровень', menu_text)
    text_rect.center = (int(screen_width / 2), int(screen_height / 4))
    screen.blit(text_surf, text_rect)
    click = False
    while True:
        pressed_keys = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                click = True
        if button("1", *button_layout_level_menu[0], click):
            return 1
        elif button("2", *button_layout_level_menu[1], click):
            return 2
        elif button("3", *button_layout_level_menu[2], click):
            return 3
        elif button("4", *button_layout_level_menu[3], click):
            return 4
        elif button("5", *button_layout_level_menu[4], click):
            return 5
        elif button("6", *button_layout_level_menu[5], click):
            return 6
        elif button('Н А З А Д', *button_layout_level_menu[6], click):
            return 0
        pg.display.update(button_layout_level_menu)
        clock.tick(60)


class AnimatedSprite(pg.sprite.Sprite):
    def __init__(self, sheet, columns=7, rows=7, x=thickness, y=WIN_SIZE.height - thickness):
        super().__init__()
        self.climb_right_frames = []
        self.climb_left_frames = []
        self.idle_right_frames = []
        self.idle_left_frames = []
        self.run_left_frames = []
        self.run_right_frames = []
        self.jump_right_frames = []
        self.jump_left_frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.idle_right_frames[self.cur_frame]
        self.rect = self.image.get_rect().move(x, y)
        self.watching_dir = 'right'

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


# Класс игрока
class Player(AnimatedSprite):
    player = None

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.add(Player.player)
        self.speed = 7
        self.is_jumping = False
        self.is_climbing = False, None
        # Кол-во кадров, в которых игрок прыгает после нажатия пробела
        self.jumping_frames = 20
        # Кол-во кадров, используется для отрисовки
        self.counter = 0
        # Используется для прыжка
        # После нажатия пробела с каждым кадром игрок будет меньше подниматься вверх
        self.count = 0
        self.falling_acceleration = 1
        self.is_alive = True
        self.victory = False
        self.cur_sound = None
        self.running_sound = pg.mixer.Sound(os.path.join('data', 'footstep.ogg'))
        self.running_sound.set_volume(0.3)
        self.jump_sound = pg.mixer.Sound(os.path.join('data', 'jump.mp3'))
        self.jump_sound.set_volume(0.9)
        self.climbing_sound = pg.mixer.Sound(os.path.join('data', 'ladder1.mp3'))
        self.climbing_sound.set_volume(0.5)
        self.death_sound = pg.mixer.Sound(os.path.join('data', 'death_sound.mp3'))
        self.death_sound.set_volume(0.5)
        self.victory_sound = pg.mixer.Sound(os.path.join('data', 'victory_sound.mp3'))
        self.victory_sound.set_volume(0.55)

    # Метод, вызывающийся, когда игрок погиб
    def die(self):
        self.is_alive = False
        # Воспроизведение звука
        if SOUNDS['background']:
            pg.mixer.music.stop()
            self.death_sound.play()
        # Если игрок взбирался по лестнице, когда умер, то звук взбирания выключается.
        # Для бега и прыжка это не нужно делать, так как им соответсвуют короткие
        # по длительности звуки, а взбиранию по лестнице - длинный
        if SOUNDS['player']:
            self.climbing_sound.stop()

    def update(self, *args):
        # Игрок погибает при любом пересечении с врагами
        if pg.sprite.spritecollideany(self, Enemy.enemies, collided=collided):
            self.die()
            return None
        # Получаем значения, какие клавиши клавиатуры нажаты
        keys = pg.key.get_pressed()
        left = keys[K_a] or keys[K_LEFT]
        right = keys[K_d] or keys[K_RIGHT]
        up = keys[K_w] or keys[K_UP]
        down = keys[K_s] or keys[K_DOWN]
        space = keys[K_SPACE]
        speed_y = 0
        speed_x = 0
        # Изначально игрок может двигаться в обе стороны
        directions = {'right': True, 'left': True}
        # Изначально игрок не стоит не платформе
        standing_on_platform = False
        # Узнаём, стоит ли игрок на границе
        standing_on_border = self.rect.bottom >= Border.bottom.rect.x
        # Изначально над игроком нет платформы
        platform_above = False
        # Если нажаты кнопки клавиатуры, отвечающие за движение вправо и влево, игрок поворачивается
        if right:
            self.watching_dir = 'right'
        elif left:
            self.watching_dir = 'left'
        # state используется для выбора анимации
        state = f'idle_{self.watching_dir}'
        # Пересечение с платформам
        # Получаем все платформы, с которыми игрок пересекается
        sprites = pg.sprite.spritecollide(self, Platform.platforms, False, collided=collided)
        for sprite in sprites:
            # Условие, проверяющее, стоит ли игрок на платформе
            if sprite.rect.y <= self.rect.bottom <= sprite.rect.y + PLATFORM_THICKNESS and not self.is_climbing[0]:
                standing_on_platform = True
                # Выравниваем игрока по верхней части платформы
                self.rect.bottom = sprite.rect.top
            # Условие, проверяющее, есть ли платформа справа от игрока
            elif sprite.rect.x <= self.rect.right <= sprite.rect.right and not self.is_climbing[0]:
                directions['right'] = False
            # Условие, проверяющее, есть ли платформа слева от игрока
            elif sprite.rect.x <= self.rect.left <= sprite.rect.right and not self.is_climbing[0]:
                directions['left'] = False
            # Условие, проверяющее, есть ли платформа над игроком
            if (sprite.rect.top <= self.rect.top <= sprite.rect.bottom <= self.rect.bottom) \
                    or (self.rect.top <= sprite.rect.top and self.rect.bottom >= sprite.rect.bottom) \
                    and self.is_jumping:
                platform_above = True
        # Пересечение с лестницами
        # Получаем все лестницы, с которыми игрок пересекается
        sprites = pg.sprite.spritecollide(self, Ladder.ladders, False, collided=collided)
        for sprite in sprites:
            # Если игрок пересекает лестницу, то он взбирается
            if sprite.rect.x - PLAYER_SIZE <= self.rect.x <= sprite.rect.right:
                self.is_climbing = True, sprite
                state = f'climb_{self.watching_dir}'
        # Если игрок взбирается по лестнице
        if self.is_climbing[0]:
            # Если игрок слез с лестницы, то он больше не взбирается
            if self.rect.y + PLAYER_SIZE < self.is_climbing[1].rect.y or self.is_climbing[1].rect.right < self.rect.x \
                    or self.rect.x < self.is_climbing[1].rect.x - PLAYER_SIZE or self.rect.top > self.is_climbing[1].rect.bottom:
                self.is_climbing = False, None
        # Пересечение с порталом
        if pg.sprite.collide_rect(self, Portal.portal):
            # Если игрок на последнем уровне, то он побеждает
            if int(get_acting_level()) == 6:
                self.victory = True
                if SOUNDS['background']:
                    pg.mixer.music.stop()
                    self.victory_sound.play()
            # Иначе загружается следующий уровень
            else:
                Game().is_running = False
                pg.display.update()
                change_acting_level(str(int(get_acting_level()) + 1))
                Game().run()

        # Скорость по оси x
        if left == right:
            speed_x = 0
        elif left and directions['left']:
            speed_x = -self.speed
            state = 'run_left'
        elif right and directions['right']:
            speed_x = self.speed
            state = 'run_right'
        elif left:
            state = 'run_left'
        elif right:
            state = 'run_right'
        self.rect.x += speed_x
        # Скорость по оси y
        if self.is_jumping and not platform_above:
            # С каждым кадром после нажатия пробела высота, на которую поднимается игрок,
            # уменьшается на 1
            speed_y -= self.count
            self.count -= 1
            if not self.count:
                self.is_jumping = False
        # Прыжок прекращается, если над игроком есть платформа
        elif self.is_jumping and platform_above:
            self.is_jumping = False
        # Если игрок стоит на границе или платформе, он не падает
        if standing_on_border or standing_on_platform:
            self.falling_acceleration = 1
            self.is_jumping = False
            # При нажатии пробела осуществляется прыжок
            if space and not self.is_climbing[0]:
                self.is_jumping = True
                self.count = self.jumping_frames
                if SOUNDS['player']:
                    self.jump_sound.play()
                    self.cur_sound = self.jump_sound
                state = f'jump_{self.watching_dir}'
        # Если игрок не на лестнице, он падает.
        # Но игрок падает, если он на лестницу попал во время прыжка(когда не достиг высшей точки)
        elif not self.is_climbing[0] or (self.is_climbing[0] and self.is_jumping):
            state = f'jump_{self.watching_dir}'
            speed_y += self.falling_acceleration
            # Ускорение при падении меняется следующим образом: 1, 2, 4, 8
            # После достижения 8, оно не увеличивается
            if self.falling_acceleration == 1:
                self.falling_acceleration = 2
            elif self.falling_acceleration < 4:
                self.falling_acceleration = self.falling_acceleration ** 2
            else:
                self.falling_acceleration = 8
        # Если игрок на лестнице
        if self.is_climbing[0]:
            if up and down:
                speed_y = 0
            elif up and abs(self.is_climbing[1].rect.y - (self.rect.y + PLAYER_SIZE)) >= self.speed:
                speed_y = -self.speed
                # Если игрок на верхней точке лестницы, то он не может подняться выше(иначе он поднимется,
                # а потом сразу упадёт из-за гравитации. Таким образом, игрок бы дёргался на месте
            elif up and abs(self.is_climbing[1].rect.y - (self.rect.y + PLAYER_SIZE)) < self.speed:
                speed_y = self.is_climbing[1].rect.y - self.rect.y - PLAYER_SIZE
            elif down:
                speed_y = self.speed

        self.rect.y += speed_y
        # Если игрок вдруг "заходит"  за барьеры, то его выталкивает
        if self.rect.x <= thickness:
            self.rect.x = thickness
        elif self.rect.x + PLAYER_SIZE >= WIN_SIZE.width - thickness:
            self.rect.x = WIN_SIZE.width - PLAYER_SIZE - thickness
        if self.rect.y + PLAYER_SIZE >= WIN_SIZE.height:
            self.rect.y = WIN_SIZE.height - PLAYER_SIZE - thickness
        elif self.rect.y <= thickness:
            self.rect.y = thickness
        # Каждый пятый кадр изменяется картинка для анимации
        if self.counter % 5 == 0:
            super().update(state)
        self.counter += 1
        # Воспроизведение звуков
        if 'run' in state and self.counter % 5 == 0 and not self.is_climbing[0] and not self.is_jumping:
            if SOUNDS['player']: self.running_sound.play()
        elif 'climb' in state and speed_y and self.cur_sound != self.climbing_sound:
            if SOUNDS["player"]:
                self.climbing_sound.play()
                self.cur_sound = self.climbing_sound
        elif 'climb' in state and not speed_y or ('climb' not in state and self.cur_sound == self.climbing_sound):
            if SOUNDS["player"]:
                self.climbing_sound.stop()
                self.cur_sound = None


# Класс платформы
class Platform(pg.sprite.Sprite):
    all_sprites = None
    platforms = None

    def __init__(self, x, y, w, h=PLATFORM_THICKNESS):
        super().__init__()
        self.image = load_image('platform1.png', None, w, h)
        self.rect = self.image.get_rect().move(x, y)
        self.add(self.all_sprites)
        self.add(self.platforms)


# Класс лестницы
class Ladder(pg.sprite.Sprite):
    all_sprites = None
    ladders = None

    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = load_image('ladder2.png', -1, w, h)
        self.rect = self.image.get_rect().move(x, y)
        self.add(self.all_sprites)
        self.add(self.ladders)


# Класс портала(выхода)
class Portal(pg.sprite.Sprite):
    all_sprites = None
    portal = None

    def __init__(self, x, y, w=PORTAL_SIZE[0], h=PORTAL_SIZE[1]):
        super().__init__()
        self.image = load_image('portal1.png', -1, w, h)
        self.rect = self.image.get_rect().move(x, y)
        self.add(self.all_sprites)


# Класс врага
class Enemy(Player):
    all_sprites = None
    enemies = None
    player = None

    def __init__(self, *args, movement_type='idle', weapon='no', movement_x=0, **kwargs):
        AnimatedSprite.__init__(self, *args, **kwargs)
        self.speed = 3
        # movement_type отвечает за то, будет ли враг стоять на месте, двигаться вдоль платформы
        # или двигаеться вдоль отрезка длиной movement_x
        self.movement_type = movement_type
        # оржие для дальнейшей разработки
        self.weapon = weapon
        # начальное направление движения врага
        self.dir = 'right'
        self.enemy_platform()
        self.movement_x = movement_x
        # смещение врага относительно точки его появления
        self.delta_x = 0
        self.add(self.all_sprites)
        self.add(self.enemies)
        self.counter = 0

    def update(self):
        # враг поворачивается в сторону игрока
        if self.player.rect.x < self.rect.x and self.movement_type == 'idle':
            self.watching_dir = 'left'
        elif self.player.rect.x > self.rect.x and self.movement_type == 'idle':
            self.watching_dir = 'right'
        state = f'idle_{self.watching_dir}'
        # В зависимости от типа движения врага, изменяем его кординаты
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
        # Проверяем, не вышел ли враг за границы
        # Если это так, то перемещаем врага к границе
        if self.rect.x <= thickness:
            self.rect.x = thickness
        elif self.rect.x + PLAYER_SIZE >= WIN_SIZE.width - thickness:
            self.rect.x = WIN_SIZE.width - PLAYER_SIZE - thickness
        if self.rect.y + PLAYER_SIZE >= WIN_SIZE.height:
            self.rect.y = WIN_SIZE.height - PLAYER_SIZE - thickness
        elif self.rect.y <= thickness:
            self.rect.y = thickness
        # Каждые 5 кадров обновляем картинку врага
        if self.counter % 5 == 0:
            AnimatedSprite.update(self, state)
        self.counter += 1

    # Если враг двигается вдоль платформы, то "привязвыаем" к нему эту платформу
    def enemy_platform(self):
        if self.movement_type == 'along_platform':
            platform = pg.sprite.spritecollide(self, Platform.platforms, False, collided=collided)[0]
            self.platform = platform

    # Изменение направления движения
    def change_dir(self):
        self.dir = 'left' if self.dir == 'right' else 'right'


# Класс границы
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


# Класс пули для дальнейшей разработки
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
    pg.init()
    screen = window_init()
    screen_width, screen_height = screen.get_size()
    BUTTON_WIDTH_START = int(screen_width // 2)
    BUTTON_HEIGHT_START = int(screen_height * 5 // 81)
    button_x_start = (screen_width - BUTTON_WIDTH_START) // 2
    BUTTON_WIDTH_LEVEL = int(screen_width * 0.3)
    BUTTON_HEIGHT_LEVEL = int(screen_height * 5 // 81)
    TOGGLE_WIDTH = int(BUTTON_WIDTH_START * 0.875)
    TOGGLE_ADJ = int(BUTTON_WIDTH_START * 0.075)
    button_layout_main_menu = [(button_x_start, screen_height * 5 // 13, BUTTON_WIDTH_START, BUTTON_HEIGHT_START),
                               (button_x_start, screen_height * 6 // 13, BUTTON_WIDTH_START, BUTTON_HEIGHT_START),
                               (button_x_start, screen_height * 7 // 13, BUTTON_WIDTH_START, BUTTON_HEIGHT_START),
                               (button_x_start, screen_height * 8 // 13, BUTTON_WIDTH_START, BUTTON_HEIGHT_START)]

    button_layout_level_menu = [(10, screen_height * 5 // 13, BUTTON_WIDTH_LEVEL, BUTTON_HEIGHT_LEVEL),
                                (170, screen_height * 5 // 13, BUTTON_WIDTH_LEVEL, BUTTON_HEIGHT_LEVEL),
                                (330, screen_height * 5 // 13, BUTTON_WIDTH_LEVEL, BUTTON_HEIGHT_LEVEL),
                                (10, screen_height * 6 // 13, BUTTON_WIDTH_LEVEL, BUTTON_HEIGHT_LEVEL),
                                (170, screen_height * 6 // 13, BUTTON_WIDTH_LEVEL, BUTTON_HEIGHT_LEVEL),
                                (330, screen_height * 6 // 13, BUTTON_WIDTH_LEVEL, BUTTON_HEIGHT_LEVEL),
                                (170, screen_height * 7 // 13, BUTTON_WIDTH_LEVEL, BUTTON_HEIGHT_LEVEL)]
    clock = pg.time.Clock()
    menu_text = pg.font.SysFont('arial', int(110 / 1080 * screen_height))
    large_text = pg.font.SysFont('arial', int(40 / 1080 * screen_height))
    medium_text = pg.font.SysFont('arial', int(35 / 1440 * screen_height))
    small_text = pg.font.SysFont('arial', int(25 / 1440 * screen_height))
    main_menu()
