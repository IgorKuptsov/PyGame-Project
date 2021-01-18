from config import *


objects = {
    'Player': (),
    'Portal': (WIN_SIZE.width - thickness - PORTAL_SIZE[0], WIN_SIZE.height - thickness - PORTAL_SIZE[1]),
    'Enemy': ({'x':WIN_SIZE.width - thickness - PORTAL_SIZE[0] - 200, 'y':WIN_SIZE.height - thickness - PLAYER_SIZE, 'movement_type':'idle'})
}