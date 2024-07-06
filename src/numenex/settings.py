from configparser import ConfigParser
from enum import Enum
import os


class Role(Enum):
    Miner = "miner"
    Validator = "validator"


class Config:
    def __init__(self, type: Role) -> None:
        file = "config.ini"
        parser = ConfigParser()
        parser.read(file)
        if type == Role.Miner:
            self.miner = {
                "key": parser.get("miner", "key_name"),
                "host": parser.get("miner", "host"),
                "port": parser.get("miner", "port"),
            }
        else:
            self.validator = {
                "key": parser.get("validator", "key_name"),
                "interval": parser.get("validator", "interval"),
            }
        self.subnet = {
            "netuid": parser.get("subnet", "netuid"),
            "use_testnet": parser.get("subnet", "use_testnet"),
            "max_allowed_weights": parser.get("subnet", "max_allowed_weights"),
        }
