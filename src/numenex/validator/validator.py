from communex.client import CommuneClient
from communex.module.client import ModuleClient
from substrateinterface import Keypair
from communex.module.module import Module
from communex.types import Ss58Address
import time
from datetime import datetime
import asyncio
from loguru import logger
from functools import partial
import concurrent.futures

import re


from ..settings import Config

logger.add("logs/log_{time:YYYY-MM-DD}.log", rotation="1 day")
IP_REGEX = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+")


def set_weights(
    score_dict: dict[
        int, float
    ],  # implemented as a float score from 0 to 1, one being the best
    # you can implement your custom logic for scoring
    netuid: int,
    client: CommuneClient,
    key: Keypair,
    max_allowed_weights: int,
) -> None:
    """
    Set weights for miners based on their scores.

    Args:
        score_dict: A dictionary mapping miner UIDs to their scores.
        netuid: The network UID.
        client: The CommuneX client.
        key: The keypair for signing transactions.
    """

    # you can replace with `max_allowed_weights` with the amount your subnet allows
    score_dict = cut_to_max_allowed_weights(score_dict, max_allowed_weights)

    # Create a new dictionary to store the weighted scores
    weighted_scores: dict[int, int] = {}

    # Calculate the sum of all inverted scores
    scores = sum(score_dict.values())

    # process the scores into weights of type dict[int, int]
    # Iterate over the items in the score_dict
    for uid, score in score_dict.items():
        # Calculate the normalized weight as an integer
        weight = int(score * 1000 / scores)

        # Add the weighted score to the new dictionary
        weighted_scores[uid] = weight

    # filter out 0 weights
    weighted_scores = {k: v for k, v in weighted_scores.items() if v != 0}

    uids = list(weighted_scores.keys())
    weights = list(weighted_scores.values())
    # send the blockchain call
    logger.info(f"weights for the following uids: {uids}")
    if len(uids) > 0:
        client.vote(key=key, uids=uids, weights=weights, netuid=netuid)


def extract_address(string: str):
    """
    Extracts an address from a string.
    """
    return re.search(IP_REGEX, string)


def get_subnet_netuid(
    clinet: CommuneClient, subnet_name: str = "replace-with-your-subnet-name"
):
    """
    Retrieve the network UID of the subnet.

    Args:
        client: The CommuneX client.
        subnet_name: The name of the subnet (default: "foo").

    Returns:
        The network UID of the subnet.

    Raises:
        ValueError: If the subnet is not found.
    """

    subnets = clinet.query_map_subnet_names()
    for netuid, name in subnets.items():
        if name == subnet_name:
            return netuid
    raise ValueError(f"Subnet {subnet_name} not found")


def get_ip_port(modules_adresses: dict[int, str]):
    """
    Get the IP and port information from module addresses.

    Args:
        modules_addresses: A dictionary mapping module IDs to their addresses.

    Returns:
        A dictionary mapping module IDs to their IP and port information.
    """

    filtered_addr = {id: extract_address(addr) for id, addr in modules_adresses.items()}
    ip_port = {
        id: x.group(0).split(":") for id, x in filtered_addr.items() if x is not None
    }
    return ip_port


def get_modules(client: CommuneClient, netuid: int) -> dict[int, str]:
    """Retrieves all module addresses from the subnet.

    Args:
        client: The CommuneClient instance used to query the subnet.
        netuid: The unique identifier of the subnet.

    Returns:
        A list of module addresses as strings.
    """
    module_addreses = client.query_map_address(netuid)
    return module_addreses


def cut_to_max_allowed_weights(
    score_dict: dict[int, float], max_allowed_weights: int
) -> dict[int, float]:
    """
    Cut the scores to the maximum allowed weights.

    Args:
        score_dict: A dictionary mapping miner UIDs to their scores.
        max_allowed_weights: The maximum allowed weights (default: 420).

    Returns:
        A dictionary mapping miner UIDs to their scores, where the scores have been cut to the maximum allowed weights.
    """
    # sort the score by highest to lowest
    sorted_scores = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)

    # cut to max_allowed_weights
    cut_scores = sorted_scores[:max_allowed_weights]

    return dict(cut_scores)


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

    def _get_miner_trades(
        self,
        miner_info: tuple[list[str], Ss58Address],
    ) -> str | None:
        connection, miner_key = miner_info
        module_ip, module_port = connection
        client = ModuleClient(module_ip, int(module_port), self.key)
        try:
            # handles the communication with the miner
            miner_answer = asyncio.run(
                client.call(
                    "trades",
                    miner_key,
                    {},
                    timeout=self.call_timeout,  #  type: ignore
                )
            )
            miner_answer = miner_answer["trades"]
            logger.info(f"Miner {module_ip}:{module_port} answered with {miner_answer}")
        except Exception as e:
            logger.add(f"Miner {module_ip}:{module_port} failed to generate an answer")
            miner_answer = None
        return miner_answer

    def _score_miner(self, miner_answer: str | None) -> float:
        # Implement your custom scoring logic here
        if not miner_answer:
            return 0

        return 0.5

    async def validate_step(self, netuid: int, max_allowed_weights: int) -> None:
        modules_adresses = get_modules(self.client, netuid)
        modules_keys = self.client.query_map_key(netuid)
        val_ss58 = self.key.ss58_address
        if val_ss58 not in modules_keys.values():
            raise RuntimeError(f"validator key {val_ss58} is not registered in subnet")
        modules_info: dict[int, tuple[list[str], Ss58Address]] = {}

        modules_filtered_address = get_ip_port(modules_adresses)
        score_dict: dict[int, float] = {}

        for module_id in modules_keys.keys():
            module_addr = modules_filtered_address.get(module_id, None)
            if not module_addr:
                continue
            modules_info[module_id] = (module_addr, modules_keys[module_id])
        get_miner_trades = partial(self._get_miner_trades)
        logger.info(f"Selected the following miners: {modules_info.keys()}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            it = executor.map(get_miner_trades, modules_info.values())
            miner_answers = [*it]

        for uid, miner_response in zip(modules_info.keys(), miner_answers):
            miner_answer = miner_response
            if not miner_answer:
                logger.info(f"Skipping miner {uid} that didn't answer")
                continue

            score = self._score_miner(miner_answer)
            time.sleep(0.5)
            # score has to be lower or eq to 1, as one is the best score, you can implement your custom logic
            assert score <= 1
            score_dict[uid] = score

        if not score_dict:
            logger.info("No miner managed to give a valid answer")
            return None

        _ = set_weights(
            score_dict, self.netuid, self.client, self.key, max_allowed_weights
        )

    def validation_loop(self, max_allowed_weights: int) -> None:
        while True:
            start_time = time.time()
            formatted_start_time = datetime.fromtimestamp(start_time).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            print(f"check validator time: {formatted_start_time}")
            _ = asyncio.run(self.validate_step(self.netuid, max_allowed_weights))
            interval = int(self.config.validator.get("interval"))
            time.sleep(interval)
