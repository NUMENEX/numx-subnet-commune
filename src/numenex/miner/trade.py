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
    def test(self):
        return {"message": "Test successful"}


if __name__ == "__main__":
    config = Config(Role.Miner)
    keypair = classic_load_key(config.miner["key"])
    miner = NumenexTradeModule()
    server = ModuleServer(miner, keypair, use_testnet=True)
    app = server.get_fastapi_app()
    server_process = multiprocessing.Process(
        target=uvicorn.run(app, host="0.0.0.0", port=8000)
    )
    try:
        server_process.start()
    except KeyboardInterrupt:
        server_process.terminate()
