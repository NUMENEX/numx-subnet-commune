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


class Question(BaseModel):
    question: str
    question_type: ty.Literal["multiple_choice", "short_answer", "true_false"]
    answer_choices: ty.Optional[ty.Dict[str, str]]
    start_date: datetime
    end_date: datetime

    class Config:
        from_attributes = True


class Answer(BaseModel):
    answer: str
    question_id: uuid.UUID
    supporting_resources: ty.Optional[ty.Dict[str, ty.Any]]

    class Config:
        from_attributes = True


class NumenexQAModule:
    def __init__(
        self,
        role: Role,
    ) -> None:
        self.role = role
        self.config = Config(role)[role.value]

    def get_questions(self, path: str):
        response = requests.get(f"{self.config['host']}:{self.config['port']}/{path}")
        print(response.json())

    def answer_questions(self, method: str, data: ty.List[Answer], path: str):
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
                    f"{self.config['host']}:{self.config['port']}/{path}",
                    headers=headers,
                    json=data,
                )
            else:
                response = requests.patch(
                    f"{self.config['host']}:{self.config['port']}/{path}",
                    headers=headers,
                    json=data,
                )
            print(response.json())
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except Exception as e:
            print(e)
            return []

    def get_answers(self, path: str):
        response = requests.get(f"{self.config['host']}:{self.config['port']}/{path}")
        print(response.json())

    def set_weights(
        self,
        score_dict: dict[int, ty.Union[str, float]],
        netuid: int,
        client: CommuneClient,
        key: Keypair,
        max_allowed_weights: int,
    ) -> None:

        score_dict = self.cut_to_max_allowed_weights(score_dict, max_allowed_weights)
        weighted_scores: dict[int, int] = {}

        scores = sum(value["score"] for value in score_dict.values())

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
            receit = client.vote(key=key, uids=uids, weights=weights, netuid=netuid)
            print(receit)

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
