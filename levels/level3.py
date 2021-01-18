from config import *


objects = {
    'Player': (),
    'Portal': (WIN_SIZE.width - thickness - 200, WIN_SIZE.height - thickness - PORTAL_SIZE[1] - 150),
    'Platform': (WIN_SIZE.width - thickness - 200, WIN_SIZE.height - thickness - 150, 200),
    'Ladder':(WIN_SIZE.width - thickness - LADDER_WIDTH, WIN_SIZE.height - thickness - 150, LADDER_WIDTH, 150)
}