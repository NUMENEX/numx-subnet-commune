from ..numenex import NumenexQAModule
from ..settings import Role, Config
import time
from .miner_verifier.main import get_result
import os
import json

import logging
from logging.handlers import RotatingFileHandler

ANSWER_JSON = "validated_answers.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        RotatingFileHandler("app.log", maxBytes=1000000, backupCount=5),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

os.environ["USER_AGENT"] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
)


def load_validated_answers():
    if os.path.exists(ANSWER_JSON):
        with open(ANSWER_JSON, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_validated_answers(processed_answers):
    with open(ANSWER_JSON, "w") as f:
        json.dump(list(processed_answers), f)


def get_unprocessed_answers(answers):
    processed_answers = load_validated_answers()
    unprocessed_answers = []
    processed_answers_ids = {answer["id"] for answer in processed_answers}
    score_dict = {}
    for answer in answers:
        answer_id = answer["id"]
        module_id = answer["miner"]["module_id"]
        if answer_id in processed_answers_ids:
            if module_id not in score_dict:
                score_dict[module_id] = {"score": processed_answers[module_id]["score"]}
            else:
                score_dict[module_id]["score"] += processed_answers[module_id]["score"]
            logger.info(f"Skipping already answer item with id: {answer_id}")
            continue
        unprocessed_answers.append(answer)

    return processed_answers, unprocessed_answers, score_dict


def main():
    logger.info("Validator started")
    while True:
        numenex_module = NumenexQAModule(role=Role.Validator)
        answers = numenex_module.get_answers(path="answers")
        processed_answers, unprocessed_answers, score_dict = get_unprocessed_answers(
            answers
        )
        config = Config(Role.Validator)
        if len(answers) == 0:
            logger.info("No Miners to validate")
        else:
            for answer in unprocessed_answers:
                if len(answer["supporting_resources"]) == 0:
                    answer["score"] = 0
                else:
                    result = get_result(answer, config)
                    logger.info({"result": result, "answer": answer})
                    answer["score"] = float(result["score"])
                module_id = answer["miner"]["module_id"]
                if module_id not in score_dict:
                    score_dict[module_id] = {"score": 0}
                score_dict[answer["miner"]["module_id"]]["score"] += answer["score"]
                processed_answers.append(
                    {
                        "id": answer["id"],
                        "score": answer["score"],
                        "module_id": answer["miner"]["module_id"],
                    }
                )
            numenex_module.set_weights(score_dict=score_dict)
            save_validated_answers(processed_answers)
            formatted_answer_validations = [
                {"id": answer["id"], "score": answer["score"]}
                for answer in unprocessed_answers
            ]
            numenex_module.answer_questions(
                data=formatted_answer_validations, method="patch", path="answers"
            )
        logger.info("Sleeping for %s seconds", config["validator"]["interval"])
        time.sleep(int(config["validator"]["interval"]))


if __name__ == "__main__":
    main()
