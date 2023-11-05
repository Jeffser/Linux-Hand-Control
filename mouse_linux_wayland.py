import uinput, time
device = uinput.Device([uinput.BTN_LEFT, uinput.BTN_RIGHT, uinput.BTN_MIDDLE, uinput.REL_X, uinput.REL_Y, uinput.REL_WHEEL, uinput.REL_HWHEEL, uinput.KEY_LEFTMETA])
time.sleep(1)
resolution = [1920, 1080]

#Last Absolute Coordinate
lac = [resolution[0], resolution[1]]
device.emit(uinput.REL_X, resolution[0])
device.emit(uinput.REL_Y, resolution[1])

def mouse_move(x : int, y : int):
    global lac
    x = round(x * resolution[0] / 100)
    y = round(y * resolution[1] / 100)
    device.emit(uinput.REL_X, x - lac[0])
    device.emit(uinput.REL_Y, y - lac[1])
    lac = [x, y]

#mode 0: normal click, 1: hold, 2: release

def mouse_click(btn : int = 0, mode : int = 0):
    
    if btn > 2 or btn < 0 or type(btn) != int:
        raise ValueError('btn must be 0, 1 or 2')
    if mode > 2 or mode < 0 or type(mode) != int:
        raise ValueError('btn must be 0, 1 or 2')
    
    button = uinput.BTN_RIGHT
    if btn == 0: button = uinput.BTN_LEFT
    elif btn == 1: button = uinput.BTN_MIDDLE

    if mode == 0 or mode == 1: device.emit(button, 1)
    if mode == 0 or mode == 2: device.emit(button, 0)

def key_super(mode : int = 0):
    if mode == 0 or mode == 1: device.emit(uinput.KEY_LEFTMETA, 1)
    if mode == 0 or mode == 2: device.emit(uinput.KEY_LEFTMETA, 0)