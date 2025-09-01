# simple sendinput wrapper

import ctypes
import input_codes as codes  

SendInput = ctypes.windll.user32.SendInput

# structs  
class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)))

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT),
                    ("ki", KEYBDINPUT)]
    _anonymous_ = ("_input",)
    _fields_ = [("type", ctypes.c_ulong),
                ("_input", _INPUT)]

# constants
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

# key flags
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

# mouse flags
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP   = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP   = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP   = 0x0040
MOUSEEVENTF_WHEEL = 0x0800

# key functions         
def key_down(key: str):
    code = codes.KEY_CODES[key]
    inp = INPUT(type=INPUT_KEYBOARD,
                ki=KEYBDINPUT(0, code, KEYEVENTF_SCANCODE, 0, None))
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def key_up(key: str):
    code = codes.KEY_CODES[key]
    inp = INPUT(type=INPUT_KEYBOARD,
                ki=KEYBDINPUT(0, code, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0, None))
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def key_press(key: str):
    key_down(key)
    key_up(key)

# mouse functions            
def mouse_click(button="left", x=None, y=None):
    """clicks mouse at current cursor pos, or moves + clicks if x,y are given"""            
    if x != None and y != None: move_mouse(x, y, absolute=True)

    if button == "left":
        down, up = MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP
    elif button == "right":
        down, up = MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP
    elif button == "middle":
        down, up = MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP
    else:
        raise ValueError(f"Unknown mouse button: {button}")

    inp = INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(0, 0, 0, down, 0, None))
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
    inp = INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(0, 0, 0, up, 0, None))
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def mouse_down(button="left"):
    flags = {
        "left": MOUSEEVENTF_LEFTDOWN,
        "right": MOUSEEVENTF_RIGHTDOWN,
        "middle": MOUSEEVENTF_MIDDLEDOWN,
    }[button]
    inp = INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(0, 0, 0, flags, 0, None))
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def mouse_up(button="left"):
    flags = {
        "left": MOUSEEVENTF_LEFTUP,
        "right": MOUSEEVENTF_RIGHTUP,
        "middle": MOUSEEVENTF_MIDDLEUP,
    }[button]
    inp = INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(0, 0, 0, flags, 0, None))
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def move_mouse(x, y, absolute=False):
    """Move mouse to (x,y). Absolute=True means screen coords [0..65535]"""
    flags = MOUSEEVENTF_MOVE
    if absolute:
        flags |= MOUSEEVENTF_ABSOLUTE    
        import win32api
        screen_w = win32api.GetSystemMetrics(0)
        screen_h = win32api.GetSystemMetrics(1)
        x = int(x * 65535 / screen_w)
        y = int(y * 65535 / screen_h)

    inp = INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(x, y, 0, flags, 0, None))
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def scroll_mouse(amount=120):
    """scrolls mouse wheel, + = up, - = down"""
    inp = INPUT(type=INPUT_MOUSE,
                mi=MOUSEINPUT(0, 0, amount, MOUSEEVENTF_WHEEL, 0, None))
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
