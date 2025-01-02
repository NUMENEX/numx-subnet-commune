from ..numenex import NumenexQAModule
from ..settings import Role, Config
import time
from .miner_verifier.main import get_result
import os
import json
import re

import logging
from logging.handlers import RotatingFileHandler

ANSWER_JSON = "validated_answers.json"
IP_REGEX = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+")

# check for logs folder if not found create one
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        RotatingFileHandler("logs/app.log", maxBytes=1000000, backupCount=5),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)
# Create separate handlers for different log levels
info_handler = RotatingFileHandler("logs/info.log", maxBytes=1000000, backupCount=5)
info_handler.setLevel(logging.INFO)  # Only INFO and above will be logged here
info_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
critical_handler = RotatingFileHandler(
    "logs/critical.log", maxBytes=1000000, backupCount=5
)
critical_handler.setLevel(
    logging.CRITICAL
)  # Only Critical and above will be logged here
critical_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

error_handler = RotatingFileHandler("logs/error.log", maxBytes=1000000, backupCount=5)
error_handler.setLevel(logging.ERROR)  # Only ERROR and above will be logged here
error_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

# Add the new handlers to the logger
logger.addHandler(info_handler)
logger.addHandler(error_handler)
logger.addHandler(critical_handler)


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


def get_unprocessed_answers(answers, swapped_modules_keys):
    processed_answers = load_validated_answers()
    unprocessed_answers = []
    processed_answers_ids = {
        answer["id"]: answer["score"] for answer in processed_answers
    }
    score_dict = {}
    for answer in answers:
        answer_id = answer["id"]
        try:
            module_id = swapped_modules_keys[answer["miner"]["user_address"]]
        except KeyError:
            logger.error(
                f"Could not find module_id for user_address: {answer['miner']['user_address']}"
            )
            continue
        if not module_id:
            continue
        if answer_id in processed_answers_ids:
            if module_id not in score_dict:
                score_dict[module_id] = {"score": processed_answers_ids[answer_id]}
            else:
                score_dict[module_id]["score"] += processed_answers_ids[answer_id]
            logger.info(f"Skipping already answer item with id: {answer_id}")
            continue
        unprocessed_answers.append(answer)

    return processed_answers, unprocessed_answers, score_dict


def extract_address(string: str):
    return re.search(IP_REGEX, string)


def main():
    logger.info("Validator started")
    numenex_module = NumenexQAModule(role=Role.Validator)
    modules_keys = numenex_module.commune_client.query_map_key(numenex_module.netuid)
    swapped_modules_keys = {value: key for key, value in modules_keys.items()}
    if numenex_module.keypair.ss58_address not in modules_keys.values():
        raise RuntimeError(
            f"validator key {numenex_module.keypair.ss58_address} is not registered in subnet"
        )
    while True:
        try:
            answers = numenex_module.get_answers(path="answers")
            processed_answers, unprocessed_answers, score_dict = (
                get_unprocessed_answers(answers, swapped_modules_keys)
            )
            config = Config(Role.Validator)
            if len(answers) == 0:
                logger.info("No Miners to validate")
            else:
                for answer in unprocessed_answers:
                    if len(answer["supporting_resources"]) == 0:
                        answer["score"] = 0
                    else:
                        try:
                            result = get_result(answer, config)
                            logger.info({"result": result, "answer": answer})
                            answer["score"] = float(result["score"])
                        except Exception:
                            logger.error("Error while validating answer", exc_info=True)
                            continue
                    module_id = swapped_modules_keys[answer["miner"]["user_address"]]
                    if not module_id:
                        logger.error(
                            f"Could not find module_id for user_address: {answer['miner']['user_address']}"
                        )
                        continue
                    if module_id not in score_dict:
                        score_dict[module_id] = {"score": 0}
                    score_dict[module_id]["score"] += answer["score"]
                    processed_answers.append(
                        {
                            "id": answer["id"],
                            "score": answer["score"],
                            "module_id": answer["miner"]["module_id"],
                        }
                    )
                save_validated_answers(processed_answers)
                numenex_module.set_weights(score_dict=score_dict)
                formatted_answer_validations = [
                    {"id": answer["id"], "score": answer["score"]}
                    for answer in unprocessed_answers
                ]
                numenex_module.answer_questions(
                    data=formatted_answer_validations, method="patch", path="answers"
                )
            logger.info("Sleeping for %s seconds", config["validator"]["interval"])
            time.sleep(int(config["validator"]["interval"]))
        except Exception as e:
            logger.critical(f"Error in running vali {e}", exc_info=True)


if __name__ == "__main__":
    main()
