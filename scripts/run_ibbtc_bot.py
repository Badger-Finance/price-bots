import asyncio
from dotenv import load_dotenv
import json
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

from price_bot import PriceBot

load_dotenv()

if __name__ == "__main__":

    loop = asyncio.get_event_loop()

    badger_client = PriceBot(
        coingecko_token_id="interest-bearing-bitcoin",
        token_display="ibBTC",
        discord_id=os.getenv("BOT_ID_IBBTC"),
    )

    loop.create_task(badger_client.start(os.getenv("BOT_TOKEN_IBBTC")))

    loop.run_forever()
