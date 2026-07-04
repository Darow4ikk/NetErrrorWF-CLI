import questionary
from cli.colors import cprint, COLORS
from utils.config import get_text, load_config, save_config
from utils.helpers import clear_screen, display_header


def settings_menu(config):
    while True:
        clear_screen()
        display_header(config)
        lang_val = config.get('language', 'ru')
        processes_val = str(config.get('processes', 0))
        threads_val = str(config.get('threads_per_process', 25))
        timeout_val = str(config.get('timeout', 2))
        batch_val = str(config.get('batch_size', 50))
        output_val = config.get('output_file', 'found_wallets.json')

        choices = [
            f"{get_text('setting_language', config)}: {lang_val}",
            f"{get_text('setting_processes', config)}: {processes_val}",
            f"{get_text('setting_threads', config)}: {threads_val}",
            f"{get_text('setting_timeout', config)}: {timeout_val}",
            f"{get_text('setting_batch', config)}: {batch_val}",
            f"{get_text('setting_output', config)}: {output_val}",
            f"{get_text('save_and_exit', config)}",
            f"{get_text('back_without_save', config)}",
        ]

        choice = questionary.select(
            get_text('settings_title', config),
            choices=choices,
            use_shortcuts=True,
            use_arrow_keys=True,
            pointer="👉 ",
            style=questionary.Style([
                ('selected', 'fg:yellow bold'),
                ('pointer', 'fg:cyan bold'),
            ])
        ).ask()

        if choice.startswith(get_text('setting_language', config)):
            new_lang = 'en' if lang_val == 'ru' else 'ru'
            config['language'] = new_lang
            save_config(config)
            continue

        elif choice.startswith(get_text('setting_processes', config)):
            val = questionary.text(get_text('enter_value', config), default=processes_val).ask()
            try:
                v = int(val)
                if v > 0:
                    config['processes'] = v
                    save_config(config)
                else:
                    cprint(get_text('must_be_positive', config), COLORS['red'])
            except:
                cprint(get_text('invalid_number', config), COLORS['red'])
            continue

        elif choice.startswith(get_text('setting_threads', config)):
            val = questionary.text(get_text('enter_value', config), default=threads_val).ask()
            try:
                v = int(val)
                if v > 0:
                    config['threads_per_process'] = v
                    save_config(config)
                else:
                    cprint(get_text('must_be_positive', config), COLORS['red'])
            except:
                cprint(get_text('invalid_number', config), COLORS['red'])
            continue

        elif choice.startswith(get_text('setting_timeout', config)):
            val = questionary.text(get_text('enter_value', config), default=timeout_val).ask()
            try:
                v = float(val)
                if v > 0:
                    config['timeout'] = v
                    save_config(config)
                else:
                    cprint(get_text('must_be_positive', config), COLORS['red'])
            except:
                cprint(get_text('invalid_number', config), COLORS['red'])
            continue

        elif choice.startswith(get_text('setting_batch', config)):
            val = questionary.text(get_text('enter_value', config), default=batch_val).ask()
            try:
                v = int(val)
                if v > 0:
                    config['batch_size'] = v
                    save_config(config)
                else:
                    cprint(get_text('must_be_positive', config), COLORS['red'])
            except:
                cprint(get_text('invalid_number', config), COLORS['red'])
            continue

        elif choice.startswith(get_text('setting_output', config)):
            val = questionary.text(get_text('enter_value', config), default=output_val).ask()
            if val:
                config['output_file'] = val
                save_config(config)
            else:
                cprint("Имя не может быть пустым", COLORS['red'])
            continue

        elif choice == get_text('save_and_exit', config):
            save_config(config)
            cprint(get_text('settings_saved', config), COLORS['green'])
            break

        elif choice == get_text('back_without_save', config):
            config.update(load_config())
            break