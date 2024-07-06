from communex.client import CommuneClient
from communex.module.client import ModuleClient
from substrateinterface import Keypair
from communex.module.module import Module
from communex.types import Ss58Address
import time
from datetime import datetime
import asyncio

from ..settings import Config


class NumxValidator(Module):
    def __init__(
        self,
        *,
        key: Keypair,
        client: CommuneClient,
        netuid: int,
        call_timeout: int = 60,
        config: Config,
    ):
        super().__init__()
        self.key = key
        self.client = client
        self.netuid = netuid
        self.call_timeout = call_timeout
        self.config = config

    async def validate_step(
        self, netuid: int, client: ModuleClient, miner_key: Ss58Address
    ):
        miner_response = await client.call(
            "test",
            miner_key,
            {},
            self.call_timeout,
        )
        print("test validate step", miner_response)

    def validation_loop(
        self,
    ) -> None:
        while True:
            start_time = time.time()
            formatted_start_time = datetime.fromtimestamp(start_time).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            print(f"check validator time: {formatted_start_time}")
            module_client = ModuleClient(
                "127.0.0.1",
                8000,
                self.key,
            )
            weighted_scores = asyncio.run(
                self.validate_step(
                    self.netuid,
                    module_client,
                    Ss58Address("5G6EojfND5JLoLkkGrZYS6McRnbBJ5vNjzsAufZkivK6D67n"),
                )
            )
            print(f"vote data: {weighted_scores}")
            interval = int(self.config.validator.get("interval"))
            time.sleep(interval)
