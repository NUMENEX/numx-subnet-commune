from ..numenex import NumenexQAModule
from ..settings import Role
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import typing as ty


def main():
    numenex_module = NumenexQAModule(role=Role.Miner)
    server = FastAPI()
    server.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])
    server.add_api_route("/questions/", numenex_module.get_questions, methods=["GET"])

    @server.post("/answers/")
    async def answer_questions(answers: ty.List[ty.Dict[str, ty.Any]]):
        return numenex_module.answer_questions(
            data=answers, method="post", path="answers"
        )

    uvicorn.run(server, host="0.0.0.0", port=9000)


if __name__ == "__main__":
    main()
