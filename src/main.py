try:
    print("Loading, please stand by..")
    import os
    import sys
    import json
    import time
    import types
    import pyglet
    from pyglet.gl import *
    import matplotlib.pyplot as plt
    import gamewindow
    import libres
    import game

    game.play()

except:
    raise SystemExit
