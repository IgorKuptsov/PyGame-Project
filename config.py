import pygame as pg


FPS = 60
PLAYER_SIZE = 75
PLATFORM_THICKNESS = 10
LADDER_WIDTH = 30
PORTAL_SIZE = 50, 100
WIN_SIZE = pg.Rect(0, 0, 500, 500)
thickness = 2
BG_COLOR = pg.Color('blue')
WHITE = (255, 255, 255)
GREEN = (127, 255, 0)
LIGHT_GREEN = (173, 255, 47)
BLACK = (0, 0, 0) 
VERSION = '1.1'
FPS = 60
PLAYER_SIZE = 50
PLATFORM_THICKNESS = 10
LADDER_WIDTH = 30
PORTAL_SIZE = 50, 100
BULLET_SIZE = 15, 7
thickness = 2
WEAPONS_SIZES = {'gun': (50, 10)}
SOUNDS = { "background": True,
        "player": True	
}
GREY = (211,211,211)
INSTRUCTION = '''
Вашей задачей является добраться до жёлтой двери, чтобы пройти уровень.
Управление движением игрока влево и вправо осуществляется при помощи клавиш клавиатуры "A" и "D" соответственно. 
Прыжок осуществляется при помощи клавиши "Пробел". 
Игрок может бегать по платформам и взбираться по лестницам, используя клавиши "W" и "S". 
На некоторых уровнях добраться до двери игроку мешают враги. 
При касании врага игрок погибает, и Вы можете начать уровень заново, или вернуться в меню. 
Советуем Вам начать прохождение с 1 уровня. Приятной игры!
'''