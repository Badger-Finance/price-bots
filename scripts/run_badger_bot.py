import asyncio
from dotenv import load_dotenv
import json
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

from price_bot import PriceBot
from utils import get_secret

load_dotenv()

if __name__ == "__main__":

    loop = asyncio.get_event_loop()

    badger_client = PriceBot(
        coingecko_token_id="badger-dao",
        token_display="BADGER",
        discord_id=os.getenv("BOT_ID_BADGER"),
        bot_token_secret_name="price-bots/badger-bot-token",
        assume_role_arn=os.getenv("ASSUME_ROLE_ARN")
    )

    bot_token = get_secret("price-bots/badger-bot-token", os.getenv("ASSUME_ROLE_ARN"))
    loop.create_task(badger_client.start(bot_token))

    loop.run_forever()
