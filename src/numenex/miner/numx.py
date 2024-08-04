from ..numenex import NumenexQAModule
from ..settings import Role
import argparse


def main():
    parser = argparse.ArgumentParser(description="Miner system for QA")
    parser.add_argument(
        "question_answer_function",
        type=str,
        choices=["get_questions", "answer_questions"],
        help="The function to execute",
    )
    numenex_module = NumenexQAModule(role=Role.Miner)
    if parser.parse_args().question_answer_function == "get_questions":
        numenex_module.get_questions(path="questions")
    elif parser.parse_args().question_answer_function == "answer_questions":
        data = [
            {
                "answer": "string",
                "question_id": "b44c07f6-d9f7-4ce0-9516-1d235eea0eb5",
                "supporting_resources": {},
            }
        ]
        numenex_module.answer_questions(data=data, path="answers")


if __name__ == "__main__":
    main()
