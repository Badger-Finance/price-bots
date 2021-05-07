import asyncio
from dotenv import load_dotenv
import json
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
)

from sett_bot import SettBot

load_dotenv()

if __name__ == "__main__":
    with open("./contracts/abi/sett.json") as sett_abi_file:
        sett_abi = json.load(sett_abi_file)

    loop = asyncio.get_event_loop()

    bbadger_client = SettBot(
        coingecko_token_id="badger-sett-badger",
        token_display="bBADGER",
        token_address=os.getenv("BBADGER_ADDRESS"),
        token_abi=sett_abi,
        discord_id=os.getenv("BOT_ID_BBADGER"),
        underlying_decimals=18,
    )

    loop.create_task(bbadger_client.start(os.getenv("BOT_TOKEN_BBADGER")))

    loop.run_forever()
