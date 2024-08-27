from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)

examples = [
    {
        "question": "Who was the first President of the United States?",
        "selected_answer": "A: George Washington",
        "sources": ["https://en.wikipedia.org/wiki/George_Washington"],
        "source_content": "George Washington was the first President of the United States, serving from 1789 to 1797.",
        "validation_result": "valid",
        "justification": "The source explicitly states that George Washington was the first President of the United States.",
        "reference_snippet": """George Washington (February 22, 1732 – December 14, 1799) was an American Founding Father, politician, military officer, and farmer who served as the first president of the United States from 1789 to 1797. Appointed by the Second Continental Congress as commander of the Continental Army in 1775, Washington led Patriot forces to victory in the American Revolutionary War and then served as president of the Constitutional Convention in 1787, which drafted the current Constitution of the United States. Washington has thus become commonly known as the "Father of his Country".""",
    },
    {
        "question": "What is the capital of France?",
        "selected_answer": "B: London",
        "sources": ["https://en.wikipedia.org/wiki/Paris"],
        "source_content": "Paris is the capital and most populous city of France.",
        "validation_result": "invalid",
        "justification": "The source clearly states that Paris is the capital of France, contradicting the miner's selected answer of London.",
        "reference_snippet": "",
    },
]

example_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "human",
            "content:{source_content}\n question:{question}\nselected_answer:{selected_answer}",
        ),
        (
            "ai",
            """{{"validation_result":"{validation_result}","justification":"{justification}","reference_snippet":"{reference_snippet}"}}""",
        ),
    ]
)
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
)


def get_final_prompt():
    final_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
            You are a helpful assistant tasked with evaluating the validity of answers based on provided source content and questions. Your responsibilities include:
            1. Verifying if the selected answer aligns with the source content in relation to the question asked.
            2. If the answer is valid, state "valid" and provide a justification.
            3. If the answer is invalid, state "invalid" and provide a justification.
            4. Apply strict criteria when determining validity, treating typos as invalid answers.
            5. Ensure the "reference_snippet" includes the relevant portion of the source content that supports your validation.
            """,
            ),
            few_shot_prompt,
            (
                "human",
                "Content: {content}\nQuestion: {question}\nSelected Answer: {selected_answer}",
            ),
        ]
    )

    return final_prompt
