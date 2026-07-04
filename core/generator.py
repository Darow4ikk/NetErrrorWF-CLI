from bip39 import generate_mnemonic, mnemonic_to_seed, mnemonic_to_entropy
from bitcoin_keys import seed_to_master_key, private_key_to_address as btc_address
from ethereum_keys import private_key_to_address as eth_address

def generate_random_mnemonic(words=12):
    return generate_mnemonic(words)

def mnemonic_to_keys(mnemonic):
    seed = mnemonic_to_seed(mnemonic)
    priv_key = seed_to_master_key(seed)
    btc_addr = btc_address(priv_key, compressed=True)
    eth_addr = eth_address(priv_key)
    return {
        'mnemonic': mnemonic,
        'btc_address': btc_addr,
        'eth_address': eth_addr,
        'private_key': priv_key.hex()  # только для отладки, не сохраняем
    }

def generate_keypair():
    mnemonic = generate_random_mnemonic(12)
    return mnemonic_to_keys(mnemonic)