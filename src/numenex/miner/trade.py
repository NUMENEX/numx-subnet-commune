from communex.module import Module, endpoint
from communex.compat.key import classic_load_key
from communex.module.server import ModuleServer
from fastapi import HTTPException
import multiprocessing
from ..settings import Config, Role
import uvicorn


class NumenexTradeModule(Module):
    def __init__(self):
        super().__init__()

    @staticmethod
    def _validate_required_params(data: dict, required_params: list[str]) -> None:
        missing_params = [param for param in required_params if param not in data]
        if missing_params:
            raise HTTPException(
                status_code=400, detail=f"Missing required parameters: {missing_params}"
            )

    @endpoint
    def trades(self):
        return {
            "trades": [
                {
                    "pair": "BTC/USDT",
                    "price": 10000.0,
                    "amount": 1.0,
                    "side": "buy",
                    "timestamp": 1623240000,
                },
                {
                    "pair": "ETH/USDT",
                    "price": 300.0,
                    "amount": 2.0,
                    "side": "sell",
                    "timestamp": 1623240000,
                },
            ]
        }


if __name__ == "__main__":
    config = Config(Role.Miner)
    keypair = classic_load_key(config.miner["key"])
    miner = NumenexTradeModule()
    server = ModuleServer(miner, keypair, use_testnet=True)
    app = server.get_fastapi_app()
    host = config.miner["host"]
    port = config.miner["port"]
    server_process = multiprocessing.Process(
        target=uvicorn.run(app, host=host, port=int(port))
    )
    try:
        server_process.start()
    except KeyboardInterrupt:
        server_process.terminate()
