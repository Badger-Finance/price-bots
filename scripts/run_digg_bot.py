import asyncio
from dotenv import load_dotenv
import json
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

from digg_bot import DiggBot

load_dotenv()

if __name__ == "__main__":
    with open("./contracts/abi/digg.json") as digg_abi_file:
        digg_abi = json.load(digg_abi_file)
    with open("./contracts/abi/btc_usd_oracle.json") as btc_oracle_abi_file:
        btc_oracle_abi = json.load(btc_oracle_abi_file)
    with open("./contracts/abi/digg_btc_oracle.json") as digg_oracle_abi_file:
        digg_oracle_abi = json.load(digg_oracle_abi_file)

    loop = asyncio.get_event_loop()
    digg_client = DiggBot(
        coingecko_token_id="digg",
        token_display="DIGG",
        token_address=os.getenv("DIGG_ADDRESS"),
        token_abi=digg_abi,
        discord_id=os.getenv("BOT_ID_DIGG"),
        btc_oracle_abi=btc_oracle_abi,
        digg_oracle_abi=digg_oracle_abi
    )

    loop.create_task(digg_client.start(os.getenv("BOT_TOKEN_DIGG")))

    loop.run_forever()
