#!/usr/bin/env python3
# main.py — NetErrror Wallet Finder CLI

import sys
import multiprocessing
from cli.menu import main_menu
from cli.ascii_art import print_logo
from cli.colors import cprint, COLORS
from utils.config import load_config

def main():
    multiprocessing.freeze_support()
    config = load_config()
    print_logo()
    cprint("Добро пожаловать в NetErrror Wallet Finder!", COLORS['green'])
    cprint("Версия 2.0 | Только для образовательных целей\n", COLORS['yellow'])
    main_menu(config)

if __name__ == "__main__":
    main()