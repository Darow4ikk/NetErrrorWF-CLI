import sys
from datetime import datetime
from cli.colors import cprint, COLORS
from bip39 import WORDLIST, mnemonic_to_seed, mnemonic_to_entropy
from core.generator import mnemonic_to_keys
from core.scanner import check_btc_balance, check_eth_balance, save_found
from api_client import ApiClient
import itertools
import questionary
from utils.config import get_text
from utils.helpers import clear_screen, pause_and_clear, display_header

# Поддерживаемые длины мнемоник (количество слов)
SUPPORTED_WORDS = [12, 15, 18, 21, 24]

def recover_mnemonic(config):
    clear_screen()
    display_header(config)
    cprint("\n" + get_text('recovery_title', config), COLORS['green'])
    cprint(get_text('enter_known_words', config), COLORS['yellow'])
    user_input = questionary.text(get_text('example_12_words', config)).ask()
    if not user_input:
        pause_and_clear(get_text('press_enter_to_continue', config))
        return
    parts = user_input.strip().lower().split()
    word_count = len(parts)
    if word_count not in SUPPORTED_WORDS:
        cprint(f"Поддерживаются только {SUPPORTED_WORDS} слов. У вас {word_count}.", COLORS['red'])
        pause_and_clear(get_text('press_enter_to_continue', config))
        return

    unknown_positions = [i for i, word in enumerate(parts) if word == '?']
    if not unknown_positions:
        cprint(get_text('no_unknown_words', config), COLORS['yellow'])
        pause_and_clear(get_text('press_enter_to_continue', config))
        return

    cprint(get_text('unknown_count', config, count=len(unknown_positions)), COLORS['cyan'])
    if len(unknown_positions) > 3:
        cprint(get_text('too_many_unknown', config), COLORS['red'])
        pause_and_clear(get_text('press_enter_to_continue', config))
        return

    unknown_count = len(unknown_positions)
    total_combinations = 2048 ** unknown_count
    cprint(get_text('total_combinations', config, total=total_combinations), COLORS['cyan'])

    check_addr = questionary.text(get_text('enter_check_address', config)).ask()
    if check_addr:
        is_btc = check_addr.startswith('1') or check_addr.startswith('3') or check_addr.startswith('bc1')
        is_eth = check_addr.startswith('0x') and len(check_addr) == 42
        if not is_btc and not is_eth:
            cprint(get_text('unknown_check_address', config), COLORS['yellow'])
            check_addr = None
    else:
        check_addr = None

    unknown_words_lists = [WORDLIST for _ in range(unknown_count)]
    client = ApiClient(timeout=config.get("timeout", 2), retries=0)
    found = False
    count = 0

    try:
        for combo in itertools.product(*unknown_words_lists):
            mnemonic_list = parts[:]
            for idx, word in zip(unknown_positions, combo):
                mnemonic_list[idx] = word
            mnemonic = " ".join(mnemonic_list)
            count += 1

            # Проверяем контрольную сумму (валидность мнемоники)
            try:
                mnemonic_to_entropy(mnemonic)
            except ValueError:
                continue

            if check_addr:
                keys = mnemonic_to_keys(mnemonic)
                if is_btc and keys['btc_address'] == check_addr:
                    cprint(f"\n" + get_text('found_mnemonic', config, mnemonic=mnemonic), COLORS['bright_green'])
                    btc_bal = check_btc_balance(client, keys['btc_address'])
                    eth_bal = check_eth_balance(client, keys['eth_address'])
                    wallet = {
                        "mnemonic": mnemonic,
                        "btc_address": keys['btc_address'],
                        "btc_balance_satoshi": btc_bal if btc_bal > 0 else 0,
                        "eth_address": keys['eth_address'],
                        "eth_balance_wei": eth_bal if eth_bal > 0 else 0,
                        "found_at": datetime.now().isoformat(),
                        "recovered": True
                    }
                    save_found(wallet, config.get("output_file", "found_wallets.json"))
                    found = True
                    break
                elif is_eth and keys['eth_address'] == check_addr:
                    cprint(f"\n" + get_text('found_mnemonic', config, mnemonic=mnemonic), COLORS['bright_green'])
                    btc_bal = check_btc_balance(client, keys['btc_address'])
                    eth_bal = check_eth_balance(client, keys['eth_address'])
                    wallet = {
                        "mnemonic": mnemonic,
                        "btc_address": keys['btc_address'],
                        "btc_balance_satoshi": btc_bal if btc_bal > 0 else 0,
                        "eth_address": keys['eth_address'],
                        "eth_balance_wei": eth_bal if eth_bal > 0 else 0,
                        "found_at": datetime.now().isoformat(),
                        "recovered": True
                    }
                    save_found(wallet, config.get("output_file", "found_wallets.json"))
                    found = True
                    break
            else:
                keys = mnemonic_to_keys(mnemonic)
                btc_bal = check_btc_balance(client, keys['btc_address'])
                eth_bal = check_eth_balance(client, keys['eth_address'])
                if btc_bal > 0 or eth_bal > 0:
                    wallet = {
                        "mnemonic": mnemonic,
                        "btc_address": keys['btc_address'],
                        "btc_balance_satoshi": btc_bal if btc_bal > 0 else 0,
                        "eth_address": keys['eth_address'],
                        "eth_balance_wei": eth_bal if eth_bal > 0 else 0,
                        "found_at": datetime.now().isoformat(),
                        "recovered": True
                    }
                    save_found(wallet, config.get("output_file", "found_wallets.json"))
                    cprint(f"\n" + get_text('found_balance', config, mnemonic=mnemonic), COLORS['bright_yellow'])
                    found = True
                    break

            if count % 1000 == 0:
                sys.stdout.write(f"\rПроверено комбинаций: {count}")
                sys.stdout.flush()
    except KeyboardInterrupt:
        cprint(f"\n" + get_text('recovery_stopped', config, count=count), COLORS['yellow'])

    if not found and check_addr:
        cprint(get_text('no_match_address', config, address=check_addr, count=count), COLORS['red'])
    elif not found and not check_addr:
        cprint(get_text('no_balance_found', config, count=count), COLORS['yellow'])
    pause_and_clear(get_text('press_enter_to_continue', config))