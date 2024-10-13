import json
import typing as ty
from .few_shots_prompt import get_final_prompt
from .llm import get_llm
from .utils import get_website_contents, get_website_metadata
from ...settings import Config


def get_result(
    miner_submission: ty.Dict[str, str], config: Config
) -> ty.Dict[str, str]:
    final_prompt = get_final_prompt()
    llm = get_llm(
        config["llm_validator"]["openai_model"],
        config["llm_validator"]["openai_api_key"],
        config["llm_validator"]["openai_temperature"],
        config["llm_validator"]["openai_max_tokens"],
        config["llm_validator"]["openai_timeout"],
        config["llm_validator"]["openai_max_retries"],
    )
    # for url in miner_submission["supporting_resources"].values():
    #     if not get_website_metadata(url, config["llm_validator"]["api_ninja_api_key"]):
    #         return {
    #             "validation_result": "invalid",
    #             "justification": "The website is not reliable",
    #             "reference_snippet": "",
    #             "score": 0.0,
    #         }
    docs = get_website_contents(miner_submission["supporting_resources"].values())
    chain = final_prompt | llm
    result = chain.invoke(
        {
            "content": docs,
            "question": miner_submission["question"]["question"],
            "selected_answer": miner_submission["answer"],
        }
    )

    return json.loads(result.content)
