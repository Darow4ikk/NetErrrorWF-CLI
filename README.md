[ENG]
# NetErrror Wallet Finder

Tool for generating and checking BIP39 mnemonics (Bitcoin and Ethereum wallets) with multiprocessing scanning. For educational purposes only! Do not use for unauthorized access to others' wallets.

## Features

* Generate random 12-word BIP39 mnemonics.
* Convert mnemonic → seed → private key → BTC (P2PKH) and ETH (EIP-55) addresses.
* Check balance via public APIs ([blockchain.info](https://blockchain.info/) and [etherscan.io](https://etherscan.io/)).
* Multiprocess + multithreaded mass scanning (configurable).
* Search for a specific address (bruteforce).
* Recover from partial mnemonic (up to 3 missing words, supports 12/15/18/21/24 words).
* Save found wallets to `found_wallets.json`.
* Interactive CLI with menus (arrow keys, space to switch language).
* Settings: language (ru/en), processes/threads count, timeout, batch size, output file.

## Installation and Usage

1. Ensure Python 3.8+ is installed.
2. Install dependencies:
   ```bash
   pip install questionary prompt_toolkit
   ```

3. Clone the repository and navigate to the folder:
   ```bash
   git clone https://github.com/your-username/neterrorr-wallet-finder.git
   cd neterrorr-wallet-finder
   ```

4. Run:
   ```bash
   python main.py
   ```

## Project Structure

* `main.py` – entry point.
* `core/` – mnemonic generation, scanning, recovery.
* `cli/` – menu, colors, ASCII art.
* `utils/` – config, localization, helpers.
* `bip39.py`, `bitcoin_keys.py`, `ethereum_keys.py`, `crypto_utils.py`, `api_client.py` – cryptographic modules (unchanged).

## Configuration

All settings are stored in `config.json` (created automatically). In the `Settings` menu you can change:

* Language (Russian/English).
* Number of processes (default = CPU cores).
* Threads per process.
* HTTP request timeout.
* Batch size – number of mnemonics per cycle.
* Output file name.

## Warning

* The probability of finding a real wallet with balance via random generation is practically zero (2¹²⁸ space).
* This tool is intended for studying BIP39 cryptography and working with APIs.
* The author is not responsible for any use of this code.





[RU]
# NetErrror Wallet Finder

Инструмент для генерации и проверки BIP39-мнемоник (криптовалютных кошельков Bitcoin и Ethereum) с использованием многопроцессорного сканирования.  
**Только для образовательных целей!** Не используйте для несанкционированного доступа к чужим кошелькам.

---

## Возможности

- Генерация случайных 12-словных мнемоник BIP39.
- Конвертация мнемоники → сид → приватный ключ → адреса BTC (P2PKH) и ETH (EIP-55).
- Проверка баланса через публичные API (blockchain.info и etherscan.io).
- Многопроцессорный + многопоточный массовый поиск (настраивается).
- Поиск по конкретному адресу (брутфорс).
- Восстановление по частичной мнемонике (до 3 пропусков, поддержка 12/15/18/21/24 слов).
- Сохранение найденных кошельков в `found_wallets.json`.
- Интерактивный CLI с меню (стрелочки, пробел для переключения языка).
- Настройки: язык (ru/en), количество процессов/потоков, таймаут, batch size, файл вывода.

---

## Установка и запуск

1. Убедитесь, что установлен Python 3.8+.
2. Установите зависимости:
   ```bash
   pip install questionary prompt_toolkit
   ```

3. Склонируйте репозиторий и перейдите в папку:
   ```bash
   git clone https://github.com/your-username/neterrorr-wallet-finder.git
   cd neterrorr-wallet-finder
   ```

4. Запустите:
   ```bash
   python main.py
   ```

## Структура проекта

* `main.py` – точка входа.
* `core/` – генерация мнемоник, сканирование, восстановление.
* `cli/` – меню, цвета, ASCII-арт.
* `utils/` – конфигурация, локализация, вспомогательные функции.
* `bip39.py`, `bitcoin_keys.py`, `ethereum_keys.py`, `crypto_utils.py`, `api_client.py` – криптографические модули (без изменений).

## Настройка

Все настройки хранятся в `config.json` (создаётся автоматически). В меню `Настройки` можно изменить:

* Язык (русский/английский).
* Количество процессов (по умолчанию – число ядер CPU).
* Потоков на процесс.
* Таймаут HTTP-запросов.
* Размер пачки (batch size) – количество мнемоник на один цикл.
* Имя файла для сохранения результатов.

## Предупреждение

* Вероятность найти реальный кошелёк с балансом при случайной генерации практически нулевая (пространство 2¹²⁸).
* Инструмент предназначен для изучения криптографии BIP39 и работы с API.
* Автор не несёт ответственности за любое использование данного кода.

## Лицензия

MIT
## License

MIT
