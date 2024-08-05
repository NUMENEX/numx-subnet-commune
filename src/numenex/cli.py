import typer
from typing import Annotated


from communex._common import get_node_url
from communex.client import CommuneClient
from communex.compat.key import classic_load_key
from .validator.validator import NumxValidator
from .settings import Config, Role
from .numenex import NumenexQAModule

app = typer.Typer()


@app.command("serve-subnet")
def serve():
    config = Config(Role.Validator)
    use_testnet: Annotated[bool, "Whether to use testnet or not"] = (
        config["subnet"]["use_testnet"] == "True"
    )
    c_client = CommuneClient(get_node_url(use_testnet=use_testnet))
    keypair = classic_load_key(config["validator"]["key"])
    max_allowed_weights = int(config["subnet"]["max_allowed_weights"])
    validator = NumxValidator(
        key=keypair,
        client=c_client,
        netuid=config["subnet"]["netuid"],
        config=config,
    )
    validator.validation_loop(max_allowed_weights)


if __name__ == "__main__":
    typer.run(serve)
