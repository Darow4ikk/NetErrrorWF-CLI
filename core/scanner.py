import json
import multiprocessing
from multiprocessing import Process, Value, Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import sys
import os
import time

from core.generator import generate_keypair
from api_client import ApiClient
from cli.colors import cprint, COLORS
from utils.config import get_text
from utils.helpers import clear_screen, pause_and_clear, display_header

BTC_API = "https://blockchain.info/balance?active={address}"
ETH_API = "https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest"


def check_btc_balance(client, address):
    try:
        url = BTC_API.replace("{address}", address)
        data = client.get(url)
        return int(data.get(address, {}).get("final_balance", 0))
    except:
        return -1


def check_eth_balance(client, address):
    try:
        url = ETH_API.replace("{address}", address)
        data = client.get(url)
        if data.get("status") == "1":
            return int(data.get("result", 0))
        return 0
    except:
        return -1


def process_single(mnemonic, client):
    from core.generator import mnemonic_to_keys
    try:
        keys = mnemonic_to_keys(mnemonic)
        btc_bal = check_btc_balance(client, keys['btc_address'])
        eth_bal = check_eth_balance(client, keys['eth_address'])
        if btc_bal > 0 or eth_bal > 0:
            return {
                "mnemonic": mnemonic,
                "btc_address": keys['btc_address'],
                "btc_balance_satoshi": btc_bal if btc_bal > 0 else 0,
                "eth_address": keys['eth_address'],
                "eth_balance_wei": eth_bal if eth_bal > 0 else 0,
                "found_at": datetime.now().isoformat()
            }
    except Exception:
        pass
    return None


def save_found(wallet, output_file):
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = []
    else:
        data = []
    for w in data:
        if w.get('btc_address') == wallet['btc_address'] or w.get('eth_address') == wallet['eth_address']:
            return
    data.append(wallet)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# =============================================================================
#  РАБОЧАЯ ФУНКЦИЯ ДЛЯ ПРОЦЕССА
# =============================================================================
def _worker_process(proc_id, batch_size, threads, timeout,
                    checked_counter, btc_counter, eth_counter, lock,
                    output_file, config, running_flag):
    """Запускается в отдельном процессе, генерирует и проверяет мнемоники."""
    local_checked = 0
    with ThreadPoolExecutor(max_workers=threads) as executor:
        clients = [ApiClient(timeout=timeout, retries=0) for _ in range(threads)]
        while running_flag.value:
            from core.generator import generate_random_mnemonic
            mnemonics = [generate_random_mnemonic(12) for _ in range(batch_size)]
            futures = []
            for i, m in enumerate(mnemonics):
                client = clients[i % len(clients)]
                future = executor.submit(process_single, m, client)
                futures.append(future)

            for future in as_completed(futures):
                result = future.result()
                local_checked += 1
                with lock:
                    checked_counter.value += 1
                    total = checked_counter.value
                    btc_f = btc_counter.value
                    eth_f = eth_counter.value

                if result:
                    if result["btc_balance_satoshi"] > 0:
                        with lock:
                            btc_counter.value += 1
                    if result["eth_balance_wei"] > 0:
                        with lock:
                            eth_counter.value += 1
                    save_found(result, output_file)
                    from cli.colors import cprint, COLORS
                    cprint(f"\n[!!!] {get_text('found_wallet', config)} {result['mnemonic'][:40]}...",
                           COLORS['bright_yellow'])

                if local_checked % 10 == 0:
                    start_time = config.get('start_time', datetime.now().isoformat())
                    elapsed = (datetime.now() - datetime.fromisoformat(start_time)).total_seconds()
                    rate = total / elapsed if elapsed > 0 else 0
                    # Убрали подсчёт сохранённых, чтобы избежать ошибок
                    status = (f"\r[P{proc_id:02d}] #{total:8d} | Rate: {rate:.1f}/s | "
                              f"BTC: {btc_f} | ETH: {eth_f}")
                    sys.stdout.write(status)
                    sys.stdout.flush()


def mass_scan(config):
    clear_screen()
    display_header(config)
    cprint("\n" + get_text('mass_scan_start', config), COLORS['green'])
    cprint(get_text('press_ctrl_c_to_stop', config), COLORS['bright_black'])

    output_file = config.get("output_file", "found_wallets.json")
    processes = config.get("processes", multiprocessing.cpu_count())
    threads = config.get("threads_per_process", 25)
    timeout = config.get("timeout", 2)
    batch_size = config.get("batch_size", 50)

    # Разделяемые счётчики
    checked_counter = Value('i', 0)
    btc_counter = Value('i', 0)
    eth_counter = Value('i', 0)
    lock = Lock()
    running_flag = Value('b', True)  # флаг для остановки процессов

    # Сохраняем время старта в конфиг для расчёта скорости
    config['start_time'] = datetime.now().isoformat()

    processes_list = []
    try:
        # Запускаем рабочие процессы
        for i in range(processes):
            p = Process(target=_worker_process,
                        args=(i, batch_size, threads, timeout,
                              checked_counter, btc_counter, eth_counter, lock,
                              output_file, config, running_flag))
            p.start()
            processes_list.append(p)

        # Ждём завершения (обычно бесконечно)
        for p in processes_list:
            p.join()

    except KeyboardInterrupt:
        cprint("\n\n[!] " + get_text('stop_signal', config), COLORS['red'])
        # Останавливаем флаг
        running_flag.value = False

        # Принудительно завершаем процессы
        for p in processes_list:
            if p.is_alive():
                p.terminate()
                p.join(timeout=1)

        # Собираем статистику
        with lock:
            total = checked_counter.value
            btc_f = btc_counter.value
            eth_f = eth_counter.value

        # Подсчитываем сохранённые кошельки
        saved_count = 0
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r') as f:
                    saved_count = len(json.load(f))
            except:
                pass

        cprint("\n" + get_text('stat_total_checked', config, total=total), COLORS['cyan'])
        cprint(get_text('stat_btc_balance', config, count=btc_f), COLORS['cyan'])
        cprint(get_text('stat_eth_balance', config, count=eth_f), COLORS['cyan'])
        cprint(get_text('stat_saved_wallets', config, count=saved_count), COLORS['cyan'])
        pause_and_clear(get_text('press_enter_to_continue', config))
        return

    except Exception as e:
        cprint(f"Ошибка: {e}", COLORS['red'])
        pause_and_clear(get_text('press_enter_to_continue', config))
        return


# =============================================================================
#  ОСТАЛЬНЫЕ ФУНКЦИИ (поиск по адресу, просмотр найденных) — без изменений
# =============================================================================

def scan_address(config):
    clear_screen()
    display_header(config)
    cprint("\n" + get_text('address_scan_title', config), COLORS['green'])
    import questionary
    address = questionary.text(get_text('enter_address', config)).ask()
    if not address:
        cprint(get_text('address_not_entered', config), COLORS['red'])
        pause_and_clear(get_text('press_enter_to_continue', config))
        return
    is_btc = address.startswith('1') or address.startswith('3') or address.startswith('bc1')
    is_eth = address.startswith('0x') and len(address) == 42
    if not is_btc and not is_eth:
        cprint(get_text('unknown_address_format', config), COLORS['red'])
        pause_and_clear(get_text('press_enter_to_continue', config))
        return

    cprint(get_text('start_bruteforce', config, address=address), COLORS['yellow'])
    cprint(get_text('bruteforce_note', config), COLORS['bright_black'])

    from core.generator import generate_keypair
    counter = 0
    try:
        while True:
            keys = generate_keypair()
            counter += 1
            if counter % 1000 == 0:
                sys.stdout.write(f"\r{get_text('checked_prefix', config)}: {counter}")
                sys.stdout.flush()
            if is_btc and keys['btc_address'] == address:
                cprint(f"\n" + get_text('address_found', config, mnemonic=keys['mnemonic']), COLORS['bright_green'])
                wallet = {
                    "mnemonic": keys['mnemonic'],
                    "btc_address": keys['btc_address'],
                    "eth_address": keys['eth_address'],
                    "btc_balance_satoshi": 0,
                    "eth_balance_wei": 0,
                    "found_at": datetime.now().isoformat(),
                    "found_by_address": address
                }
                save_found(wallet, config.get("output_file", "found_wallets.json"))
                pause_and_clear(get_text('press_enter_to_continue', config))
                return
            if is_eth and keys['eth_address'] == address:
                cprint(f"\n" + get_text('address_found', config, mnemonic=keys['mnemonic']), COLORS['bright_green'])
                wallet = {
                    "mnemonic": keys['mnemonic'],
                    "btc_address": keys['btc_address'],
                    "eth_address": keys['eth_address'],
                    "btc_balance_satoshi": 0,
                    "eth_balance_wei": 0,
                    "found_at": datetime.now().isoformat(),
                    "found_by_address": address
                }
                save_found(wallet, config.get("output_file", "found_wallets.json"))
                pause_and_clear(get_text('press_enter_to_continue', config))
                return
    except KeyboardInterrupt:
        cprint(f"\n" + get_text('search_stopped', config, count=counter), COLORS['yellow'])
        pause_and_clear(get_text('press_enter_to_continue', config))
        return


def show_found(config):
    clear_screen()
    display_header(config)
    output_file = config.get("output_file", "found_wallets.json")
    if not os.path.exists(output_file):
        cprint(get_text('file_not_found', config), COLORS['yellow'])
        pause_and_clear(get_text('press_enter_to_continue', config))
        return
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        cprint("Ошибка чтения файла.", COLORS['red'])
        pause_and_clear(get_text('press_enter_to_continue', config))
        return
    if not data:
        cprint(get_text('no_found', config), COLORS['yellow'])
        pause_and_clear(get_text('press_enter_to_continue', config))
        return

    cprint("\n" + get_text('show_found_title', config, count=len(data)), COLORS['cyan'])
    for i, w in enumerate(data, 1):
        cprint(get_text('wallet_entry', config, idx=i, mnemonic=w.get('mnemonic', 'N/A')[:50]), COLORS['white'])
        cprint(get_text('btc_line', config, addr=w.get('btc_address', 'N/A'), bal=w.get('btc_balance_satoshi', 0)), COLORS['bright_black'])
        cprint(get_text('eth_line', config, addr=w.get('eth_address', 'N/A'), bal=w.get('eth_balance_wei', 0)), COLORS['bright_black'])
        cprint(get_text('found_at', config, time=w.get('found_at', 'N/A')), COLORS['bright_black'])
        print()
    pause_and_clear(get_text('press_enter_to_continue', config))