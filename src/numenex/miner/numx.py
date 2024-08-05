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
        answers = [
            {
                "question_id": "26e34ba9-4e0d-46ab-8f8e-820fce3f5e76",
                "answer": "answer 1 of 1",
                "supporting_resources": {},
            },
            {
                "question_id": "1d990f08-77f7-4278-ae1c-5b1bb5232be7",
                "answer": "answer 1 of 2",
                "supporting_resources": {},
            },
        ]
        numenex_module.answer_questions(method="post", data=answers, path="answers")


if __name__ == "__main__":
    main()
