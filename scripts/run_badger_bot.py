import asyncio
import json
import logging
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

from price_bot import PriceBot
from utils import get_secret

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    logger = logging.getLogger("test")
    arn = os.getenv("ASSUME_ROLE_ARN")

    logger.info(f"ASSUME_ROLE_ARN = {arn}")

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
