import sys
import questionary
from cli.colors import cprint, COLORS
from utils.config import get_text
from utils.helpers import clear_screen, display_header


def main_menu(config):
    while True:
        clear_screen()
        display_header(config)  # теперь выводит логотип и подпись

        menu_choices = [
            get_text('menu_mass_scan', config),
            get_text('menu_address_scan', config),
            get_text('menu_recovery', config),
            get_text('menu_show_found', config),
            get_text('menu_settings', config),
            get_text('menu_exit', config),
        ]

        choice = questionary.select(
            get_text('main_menu', config),
            choices=menu_choices,
            use_shortcuts=True,
            use_arrow_keys=True,
            pointer="👉 ",
            style=questionary.Style([
                ('selected', 'fg:yellow bold'),
                ('pointer', 'fg:cyan bold'),
            ])
        ).ask()

        if choice == menu_choices[0]:  # Mass scan
            from core.scanner import mass_scan
            mass_scan(config)
        elif choice == menu_choices[1]:  # Address scan
            from core.scanner import scan_address
            scan_address(config)
        elif choice == menu_choices[2]:  # Recovery
            from core.recovery import recover_mnemonic
            recover_mnemonic(config)
        elif choice == menu_choices[3]:  # Show found
            from core.scanner import show_found
            show_found(config)
        elif choice == menu_choices[4]:  # Settings
            from cli.settings import settings_menu
            settings_menu(config)
        elif choice == menu_choices[5]:  # Exit
            cprint(get_text('exit', config), COLORS['red'])
            sys.exit(0)