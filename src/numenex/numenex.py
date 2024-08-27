import requests
from substrateinterface import Keypair
from datetime import datetime
from .utils import sign_message
from communex.compat.key import classic_load_key
from .settings import Config, Role
import uuid
from pydantic import BaseModel
import typing as ty
import math
from communex.client import CommuneClient
from communex.module.module import Module, endpoint
from fastapi.exceptions import HTTPException
from communex._common import get_node_url
import logging

logger = logging.getLogger(__name__)


class Question(BaseModel):
    question: str
    question_type: ty.Literal["multiple_choice", "short_answer", "true_false"]
    answer_choices: ty.Optional[ty.Dict[str, str]]
    start_date: datetime
    end_date: datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class Answer(BaseModel):
    answer: str
    question_id: uuid.UUID
    supporting_resources: ty.Optional[ty.Dict[str, ty.Any]]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class NumenexQAModule(Module):
    def __init__(
        self,
        role: Role,
    ) -> None:
        self.role = role
        self.config = Config(role)[role.value]
        self.keypair = classic_load_key(self.config["key"])
        if role.value == "validator":
            self.default_config = Config(role)
            self.netuid = int(self.default_config["subnet"]["netuid"])
            self.use_testnet = self.default_config["subnet"]["use_testnet"] == "True"
            self.commune_client = CommuneClient(
                get_node_url(use_testnet=self.use_testnet)
            )
            self.max_allowed_weights = int(
                self.default_config["subnet"]["max_allowed_weights"]
            )

    @endpoint
    def get_questions(self):
        try:
            response = requests.get(
                f"{self.config['host']}:{self.config['port']}/questions/"
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code, detail=response.text
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=e)

    @endpoint
    def answer_questions(
        self, data: ty.List[Answer], method: str = "POST", path: str = "answers"
    ):
        key_pair = classic_load_key(self.config["key"])
        nonce = datetime.now().timestamp() * 1000
        address = key_pair.ss58_address
        message = f"{key_pair.public_key.hex()}:{address}:{nonce}"
        signature = sign_message(key_pair.private_key.hex(), message)
        headers = {
            "message": message,
            "signature": signature,
        }
        try:
            if method == "post":
                response = requests.post(
                    f"{self.config['host']}:{self.config['port']}/{path}/",
                    headers=headers,
                    json=data,
                )
            else:
                response = requests.patch(
                    f"{self.config['host']}:{self.config['port']}/{path}/",
                    headers=headers,
                    json=data,
                )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code, detail=response.text
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=e)

    @endpoint
    def get_answers(self, path: str = "answers"):
        try:
            response = requests.get(
                f"{self.config['host']}:{self.config['port']}/{path}"
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code, detail=response.text
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=e)

    def set_weights(self, score_dict: dict[int, ty.Union[str, float]]) -> None:

        score_dict = self.cut_to_max_allowed_weights(
            score_dict, self.max_allowed_weights
        )
        weighted_scores: dict[int, int] = {}

        scores = sum(value["score"] for value in score_dict.values())
        if scores == 0:
            logger.info("All miners scored 0")
            return
        # process the scores into weights of type dict[int, int]
        # Iterate over the items in the score_dict
        for uid, score_data in score_dict.items():
            # Calculate the normalized weight as an integer
            weight = int(score_data["score"] * 1000 / scores)

            # Add the weighted score to the new dictionary
            weighted_scores[uid] = weight

        # filter out 0 weights
        weighted_scores = {k: v for k, v in weighted_scores.items() if v != 0}

        uids = list(weighted_scores.keys())
        weights = list(weighted_scores.values())
        # send the blockchain call
        print(f"weights for the following uids: {uids}")
        if len(uids) > 0:
            receit = self.commune_client.vote(
                key=self.keypair, uids=uids, weights=weights, netuid=self.netuid
            )
            print(receit.is_success)

    def cut_to_max_allowed_weights(
        self, score_dict: dict[int, float], max_allowed_weights: int
    ) -> dict[int, float]:
        if (len(score_dict)) >= max_allowed_weights:
            max_allowed_miners = math.ceil(
                (len(score_dict) if len(score_dict) % 2 == 0 else (len(score_dict) + 1))
                // 2
            )
        else:
            max_allowed_miners = len(score_dict)
        # sort the score by highest to lowest
        sorted_scores = sorted(
            score_dict.items(), key=lambda x: x[1]["score"], reverse=True
        )

        # cut to max_allowed_weights
        cut_scores = sorted_scores[:max_allowed_miners]

        return dict(cut_scores)
