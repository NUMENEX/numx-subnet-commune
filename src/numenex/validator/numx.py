from ..numenex import NumenexQAModule
from ..settings import Role, Config
from typing import Annotated
from communex._common import get_node_url
from communex.compat.key import classic_load_key
from communex.client import CommuneClient
import argparse


def main():
    parser = argparse.ArgumentParser(description="Validator system for QA")
    parser.add_argument(
        "question_answer_function",
        type=str,
        choices=["get_answers", "validate_and_update_answers"],
        help="The function to execute",
    )
    numenex_module = NumenexQAModule(role=Role.Validator)
    if parser.parse_args().question_answer_function == "get_answers":
        numenex_module.get_answers(path="answers")
    elif parser.parse_args().question_answer_function == "validate_and_update_answers":
        config = Config(Role.Validator)
        use_testnet: Annotated[bool, "Whether to use testnet or not"] = (
            config["subnet"]["use_testnet"] == "True"
        )
        c_client = CommuneClient(get_node_url(use_testnet=use_testnet))
        keypair = classic_load_key(config["validator"]["key"])
        max_allowed_weights = int(config["subnet"]["max_allowed_weights"])
        answers = [
            {
                "id": "1fa6f43c-73cc-401c-9544-763ea9799d51",
                "created_at": "2024-08-06T01:31:54.847839+05:45",
                "updated_at": "2024-08-06T01:31:54.847839+05:45",
                "answer": "answer 1 of 1",
                "question_id": "26e34ba9-4e0d-46ab-8f8e-820fce3f5e76",
                "supporting_resources": {},
                "miner": {
                    "id": "f665a3e3-b9f5-40dd-b606-7905432c1253",
                    "created_at": "2024-08-06T01:31:54.827930+05:45",
                    "updated_at": "2024-08-06T01:31:54.827930+05:45",
                    "user_address": "5FLbaLYazG4EnJdz2pw2ZEgaSYRfwQN7FqufcV4xtW1RVitm",
                    "user_type": "miner",
                    "module_id": 1,
                },
                "score": 0.5,
            },
            {
                "id": "e6f4d4d9-0d2b-46d6-82fc-26ce7965233b",
                "created_at": "2024-08-06T01:31:54.847839+05:45",
                "updated_at": "2024-08-06T01:31:54.847839+05:45",
                "answer": "answer 1 of 2",
                "question_id": "1d990f08-77f7-4278-ae1c-5b1bb5232be7",
                "supporting_resources": {},
                "miner": {
                    "id": "f665a3e3-b9f5-40dd-b606-7905432c1253",
                    "created_at": "2024-08-06T01:31:54.827930+05:45",
                    "updated_at": "2024-08-06T01:31:54.827930+05:45",
                    "user_address": "5FLbaLYazG4EnJdz2pw2ZEgaSYRfwQN7FqufcV4xtW1RVitm",
                    "user_type": "miner",
                    "module_id": 1,
                },
                "score": 0.1,
            },
        ]
        score_dict = {}
        for answer in answers:
            module_id = answer["miner"]["module_id"]
            if module_id not in score_dict:
                score_dict[module_id] = {"score": 0}
            score_dict[answer["miner"]["module_id"]]["score"] += answer["score"]
        numenex_module.set_weights(
            score_dict=score_dict,
            netuid=config["subnet"]["netuid"],
            client=c_client,
            key=keypair,
            max_allowed_weights=max_allowed_weights,
        )
        formatted_answer_validations = [
            {"id": answer["id"], "score": answer["score"]} for answer in answers
        ]
        print(formatted_answer_validations)
        numenex_module.answer_questions(
            method="patch", data=formatted_answer_validations, path="answers"
        )


if __name__ == "__main__":
    main()
