import os
import sys

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def pause_and_clear(prompt=None):
    if prompt is None:
        prompt = "Нажмите Enter для продолжения..."
    input(prompt)
    clear_screen()

def display_header(config):
    from cli.ascii_art import print_logo
    from cli.colors import cprint, COLORS
    print_logo()
    cprint("  \n", COLORS['bright_blue'])