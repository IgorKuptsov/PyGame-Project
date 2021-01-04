import pygame as pg
from pygame.locals import *


class Game:
    FPS = 60
    BG_COLOR = pg.Color('red')
    WIN_SIZE = pg.Rect(0, 0, 500, 500)

    def __init__(self):
        pg.init()
        self.is_running = True
        self.screen = pg.display.set_mode(self.WIN_SIZE.size)
        self.clock = pg.time.Clock()
        # self.screen = pg.display.set_mode()

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
        self.clock.tick_busy_loop(self.FPS)

    def render(self):
        self.screen.fill(self.BG_COLOR)
        pg.display.update()

    def quit(self):
        pg.quit()


if __name__ == '__main__':
    Game().run()
