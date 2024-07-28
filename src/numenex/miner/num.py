from ..numenex import NumenexTradeModule
from ..settings import Role
import argparse


def main():
    parser = argparse.ArgumentParser(description="Miner system for trades")
    parser.add_argument(
        "trade_function",
        type=str,
        choices=["get_miner_trades", "update_trade"],
        help="The function to execute",
    )
    path = "trades"
    numenex_module = NumenexTradeModule(role=Role.Miner, path=path)
    if parser.parse_args().trade_function == "get_miner_trades":
        numenex_module.get_trades()
    elif parser.parse_args().trade_function == "update_trade":
        data = {"predicted_price": 22.42223, "signal": "bullish"}
        numenex_module.update_trade(trade_id="1", data=data)


if __name__ == "__main__":
    main()
