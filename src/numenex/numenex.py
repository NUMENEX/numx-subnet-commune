import requests
from substrateinterface import Keypair
from datetime import datetime
from .utils import sign_message
from communex.compat.key import classic_load_key
from .settings import Config, Role
import uuid
from pydantic import BaseModel
from typing import Optional


class Trade(BaseModel):
    id: uuid.UUID
    feeder_address: str
    token_price_on_trade_day: float
    predicted_price: Optional[float]
    predictor_address: Optional[str]
    validator_address: Optional[str]
    prediction_end_date: datetime
    price_prediction_date: datetime
    status: str
    roi: Optional[float]
    token_price_on_prediction_day: Optional[float]
    hash: str
    token_name: str
    token_symbol: str
    trading_pair: str
    signal: Optional[str]
    token_address: str
    closeness_value: float
    module_id: str

    class Config:
        from_attributes = True


class NumenexTradeModule:
    def __init__(
        self,
        role: Role,
        path: str,
    ) -> None:
        self.role = role
        self.path = path
        self.config = Config(role)[role.value]

    def get_trades(self):
        key_pair = classic_load_key(self.config["key"])
        nonce = datetime.now().timestamp() * 1000
        address = key_pair.ss58_address
        message = f"{key_pair.public_key.hex()}:{address}:{nonce}"
        signature = sign_message(key_pair.private_key.hex(), message)
        headers = {
            "message": message,
            "signature": signature,
        }
        response = requests.get(
            f"{self.config['host']}:{self.config['port']}/{self.path}", headers=headers
        )
        print(response.json())

    def update_trade(self, trade_id: str, data: dict):
        key_pair = classic_load_key(self.config.miner["key"])
        nonce = datetime.now().timestamp() * 1000
        address = key_pair.ss58_address
        message = f"{key_pair.public_key.hex()}:{address}:{nonce}"
        signature = sign_message(key_pair.private_key.hex(), message)
        headers = {
            "message": message,
            "signature": signature,
        }
        response = requests.put(
            f"{self.config['host']}:{self.config['port']}/{self.path}/{self.role}/{trade_id}",
            headers=headers,
            json=data,
        )
        if response.status_code == 200:
            return response.json()
        else:
            return []
