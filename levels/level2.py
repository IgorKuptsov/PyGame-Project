from config import *


objects = {
    'Player': (),
    'Portal': (WIN_SIZE.width - thickness - PORTAL_SIZE[0], WIN_SIZE.height - thickness - PORTAL_SIZE[1] - 100),
    'Platform': (WIN_SIZE.width - thickness - 200, WIN_SIZE.height - thickness - 100, 200)
}