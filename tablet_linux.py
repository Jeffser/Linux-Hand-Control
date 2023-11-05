#!/usr/bin/env python3
import sys
import libevdev
import time
resolution = [1920, 1080]


dev = libevdev.Device()
dev.name = "Tablet"
dev.enable(libevdev.EV_ABS.ABS_X,
            libevdev.InputAbsInfo(minimum=0, maximum=65534, resolution=resolution[0]))
dev.enable(libevdev.EV_ABS.ABS_Y,
            libevdev.InputAbsInfo(minimum=0, maximum=65534, resolution=resolution[1]))
dev.enable(libevdev.EV_ABS.ABS_Z,
            libevdev.InputAbsInfo(minimum=0, maximum=8191))
dev.enable(libevdev.EV_ABS.ABS_PRESSURE,
            libevdev.InputAbsInfo(minimum=0, maximum=8191))
dev.enable(libevdev.EV_MSC.MSC_SCAN)
dev.enable(libevdev.EV_KEY.KEY_P)
dev.enable(libevdev.EV_KEY.BTN_LEFT)
dev.enable(libevdev.EV_KEY.BTN_RIGHT)
dev.enable(libevdev.EV_KEY.BTN_MIDDLE)
dev.enable(libevdev.EV_KEY.BTN_TOUCH)
dev.enable(libevdev.EV_SYN.SYN_REPORT)
dev.enable(libevdev.EV_SYN.SYN_CONFIG)
dev.enable(libevdev.EV_SYN.SYN_MT_REPORT)
dev.enable(libevdev.EV_SYN.SYN_DROPPED)
dev.enable(libevdev.EV_KEY.KEY_LEFTMETA)
dev.enable(libevdev.EV_SYN._SYN_04)
dev.enable(libevdev.EV_SYN._SYN_05)
dev.enable(libevdev.EV_SYN._SYN_06)
dev.enable(libevdev.EV_SYN._SYN_07)
dev.enable(libevdev.EV_SYN._SYN_08)
dev.enable(libevdev.EV_SYN._SYN_09)
dev.enable(libevdev.EV_SYN._SYN_0A)
dev.enable(libevdev.EV_SYN._SYN_0B)
dev.enable(libevdev.EV_SYN._SYN_0C)
dev.enable(libevdev.EV_SYN._SYN_0D)
dev.enable(libevdev.EV_SYN._SYN_0E)
dev.enable(libevdev.EV_SYN.SYN_MAX)
uinput = dev.create_uinput_device()

def tablet_move(x : float, y : float):
    #x = round(x * resolution[0] / 100)
    #y = round(y * resolution[1] / 100)
    sensibility = 5
    x = round(round(x, sensibility) / 100 * 65534)
    y = round(round(y, sensibility) / 100 * 65534)
    #click_pressure = round(click_pressure / 100 * 8191)
    #print([x, y, click_pressure])

    uinput.send_events([
        libevdev.InputEvent(libevdev.EV_ABS.ABS_PRESSURE, 0),
        libevdev.InputEvent(libevdev.EV_ABS.ABS_X, x),
        libevdev.InputEvent(libevdev.EV_ABS.ABS_Y, y),
        libevdev.InputEvent(libevdev.EV_KEY.BTN_STYLUS, value=0),
        libevdev.InputEvent(libevdev.EV_KEY.BTN_STYLUS2, value=0),
        libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_PEN, value=1),
        libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0),
    ])
    

#mode 0: normal click, 1: hold, 2: release

def mouse_click(btn : int = 0, mode : int = 0):
    if btn > 2 or btn < 0 or type(btn) != int:
        raise ValueError('btn must be 0, 1 or 2')
    if mode > 2 or mode < 0 or type(mode) != int:
        raise ValueError('btn must be 0, 1 or 2')
    
    button = libevdev.EV_KEY.BTN_LEFT
    if btn == 1: button = libevdev.EV_KEY.BTN_MIDDLE
    elif btn == 2: button = libevdev.EV_KEY.BTN_RIGHT
    if mode == 0 or mode == 1: uinput.send_events([libevdev.InputEvent(button, 1), libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)])
    if mode == 0 or mode == 2: uinput.send_events([libevdev.InputEvent(button, 0), libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)])

def key_super(mode : int = 0):
    if mode == 0 or mode == 1: uinput.send_events([libevdev.InputEvent(libevdev.EV_KEY.KEY_LEFTMETA, 1)])
    if mode == 0 or mode == 2: uinput.send_events([libevdev.InputEvent(libevdev.EV_KEY.KEY_LEFTMETA, 0)])