import requests
from substrateinterface import Keypair
from datetime import datetime
from ..utils import sign_message
from communex.compat.key import classic_load_key
from ..settings import Config, Role


def get_trades():
    config = Config(Role.Miner)
    key_pair = classic_load_key(config.miner["key"])
    print(key_pair.private_key.hex())
    nonce = datetime.now().timestamp() * 1000
    address = key_pair.ss58_address
    message = f"{key_pair.public_key.hex()}{address}:{nonce}"
    signature = sign_message(key_pair.private_key.hex(), message)
    print(signature)
    headers = {
        "message": message,
        "signature": signature,
    }
    response = requests.get("http://localhost:8001/trades", headers=headers)
    print(response.json())


if __name__ == "__main__":
    get_trades()
