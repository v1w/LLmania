try:
    import pyglet
    from pyglet.gl import *
    import os
    import sys
    import json
    import time
    import libres
    import libgame

    libgame.play()
except:
    # 不写Exception才能捕获键盘中断，最外部响应。
    raise SystemExit
