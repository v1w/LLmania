try:
    print("Loading, please stand by..")
    import os
    import sys
    import json
    import time
    import types
    import cmd
    import pyglet
    import requests
    from pyglet.gl import *
    import matplotlib.pyplot as plt
    import gamewindow
    import libres
    import game
    import llpractice

    game.init()

except:
    raise SystemExit
