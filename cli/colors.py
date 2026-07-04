# ANSI color codes
COLORS = {
    'reset': '\033[0m',
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'bright_black': '\033[90m',
    'bright_red': '\033[91m',
    'bright_green': '\033[92m',
    'bright_yellow': '\033[93m',
    'bright_blue': '\033[94m',
    'bright_magenta': '\033[95m',
    'bright_cyan': '\033[96m',
    'bright_white': '\033[97m',
}

def cprint(text, color_code=COLORS['white'], end='\n'):
    print(f"{color_code}{text}{COLORS['reset']}", end=end)

def set_text_color(color):
    """Устанавливает цвет для обычного текста (COLORS['white'] и COLORS['bright_white'])."""
    global COLORS
    # Сопоставление имени цвета с ANSI-кодом
    color_map = {
        'white': ('37', '97'),
        'yellow': ('33', '93'),
        'green': ('32', '92'),
        'cyan': ('36', '96'),
        'magenta': ('35', '95'),
        'red': ('31', '91'),
        'blue': ('34', '94'),
    }
    normal, bright = color_map.get(color, ('37', '97'))
    COLORS['white'] = f'\033[{normal}m'
    COLORS['bright_white'] = f'\033[{bright}m'