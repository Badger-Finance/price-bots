import asyncio
from dotenv import load_dotenv
import json
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

from sett_bot import SettBot

load_dotenv()

if __name__ == "__main__":
    with open("./contracts/abi/sett.json") as sett_abi_file:
        sett_abi = json.load(sett_abi_file)

    loop = asyncio.get_event_loop()

    bdigg_client = SettBot(
        coingecko_token_id="badger-sett-digg",
        token_display="bDIGG",
        token_address=os.getenv("BDIGG_ADDRESS"),
        token_abi=sett_abi,
        discord_id=os.getenv("BOT_ID_BDIGG"),
        underlying_decimals=9,
    )

    loop.create_task(bdigg_client.start(os.getenv("BOT_TOKEN_BDIGG")))

    loop.run_forever()
