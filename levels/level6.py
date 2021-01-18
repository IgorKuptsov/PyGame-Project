from config import *


objects = {
    'Player': (),
    'Portal': (WIN_SIZE.width - thickness - PORTAL_SIZE[0], WIN_SIZE.height - thickness - 125 - 200 - PORTAL_SIZE[1]),
    'Platform1': (thickness, WIN_SIZE.height - thickness - 125, WIN_SIZE.height - thickness * 2),
    'Platform2':(thickness, WIN_SIZE.height - thickness - 125 - 200, WIN_SIZE.height - thickness * 2),
    'Ladder':(WIN_SIZE.width - thickness - LADDER_WIDTH, WIN_SIZE.height - thickness - 125, LADDER_WIDTH, 125),
    'Ladder2': (thickness, WIN_SIZE.height - thickness - 125 - 200, LADDER_WIDTH, 200),
    'Enemy1': ({"x": thickness + WIN_SIZE.width // 2, "y": WIN_SIZE.height - thickness - 125 - PLAYER_SIZE,
               "movement_type": 'along_platform'}),
    'Enemy2': ({"x": thickness, "y": WIN_SIZE.height - thickness - 125 - PLAYER_SIZE - 200,
               "movement_type": 'along_platform'})
}