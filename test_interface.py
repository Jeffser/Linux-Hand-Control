debug = False

def tablet_move(x : float, y : float):
    if debug: print(["tablet_move", x, y])
    

#mode 0: normal click, 1: hold, 2: release

def mouse_click(btn : int = 0, mode : int = 0):
    if debug: print(["mouse_click", btn, mode])

def key_super(mode : int = 0):
    if debug: print(["key_super", mode])