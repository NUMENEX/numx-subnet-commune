from ..numenex import NumenexQAModule
from ..settings import Role, Config
import time
from .miner_verifier.main import get_result
import os

import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        RotatingFileHandler("app.log", maxBytes=1000000, backupCount=5),
        logging.StreamHandler(),
    ],
)
os.environ["USER_AGENT"] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
)


def main():
    logger = logging.getLogger(__name__)
    logger.info("Validator started")
    while True:
        numenex_module = NumenexQAModule(role=Role.Validator)
        answers = numenex_module.get_answers(path="answers")
        config = Config(Role.Validator)
        score_dict = {}
        if len(answers) == 0:
            logger.info("No Miners to validate")
        else:
            for answer in answers:
                if len(answer["supporting_resources"]) == 0:
                    answer["score"] = 0
                else:
                    result = get_result(answer, config)
                    logger.info({"result": result, "answer": answer})
                    answer["score"] = 1 if result["validation_result"] == "valid" else 0
                module_id = answer["miner"]["module_id"]
                if module_id not in score_dict:
                    score_dict[module_id] = {"score": 0}
                score_dict[answer["miner"]["module_id"]]["score"] += answer["score"]
            numenex_module.set_weights(score_dict=score_dict)
            formatted_answer_validations = [
                {"id": answer["id"], "score": answer["score"]} for answer in answers
            ]
            numenex_module.answer_questions(
                data=formatted_answer_validations, method="patch", path="answers"
            )
        logger.info("Sleeping for %s seconds", config["validator"]["interval"])
        time.sleep(int(config["validator"]["interval"]))


if __name__ == "__main__":
    main()
