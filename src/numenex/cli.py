import typer
from typing import Annotated


from communex._common import get_node_url
from communex.client import CommuneClient
from communex.compat.key import classic_load_key
from .validator.validator import NumxValidator
from .settings import Config, Role

app = typer.Typer()


@app.command("serve-subnet")
def serve():
    # keypair = classic_load_key(commune_key)  # type: ignore
    c_client = CommuneClient(get_node_url(use_testnet=True))
    config = Config(Role.Validator)
    # subnet_uid = get_subnet_netuid("your-subnet-name")
    validator = NumxValidator(
        key=classic_load_key(config.validator["key"]),
        client=c_client,
        netuid=1,
        config=config,
    )
    validator.validation_loop()


if __name__ == "__main__":
    typer.run(serve)
