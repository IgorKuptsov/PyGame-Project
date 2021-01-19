from config import *

objects = {
    'Player': (),
    'Portal': (WIN_SIZE.width - thickness - PORTAL_SIZE[0], WIN_SIZE.height - thickness - PORTAL_SIZE[1] - 120),
    'Platform': (WIN_SIZE.width - thickness - 250, WIN_SIZE.height - thickness - 120, 250),
    'Enemy': ({"x": WIN_SIZE.width - thickness - 250, "y": WIN_SIZE.height - thickness - PLAYER_SIZE - 120,
               "movement_type": 'along_platform'}),
    'Ladder': (WIN_SIZE.width - thickness - 250, WIN_SIZE.height - thickness - 120, LADDER_WIDTH, 120),
}
