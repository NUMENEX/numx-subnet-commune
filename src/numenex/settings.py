from configparser import ConfigParser
from .misc import Role


class Config:
    def __init__(self, file: str, type: Role) -> None:
        if file in None:
            file = "config.ini"
        parser = ConfigParser()
        parser.read(file)
        if type == Role.Miner:
            self.miner = {"key": parser.get("miner", "key_name")}
        else:
            self.validator = {"key": parser.get("validator", "key_name")}
