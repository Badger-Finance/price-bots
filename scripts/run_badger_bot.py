import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from price_bot import PriceBot
from utils import get_secret

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    # name of secret in secrets manager
    bot_token_secret_name = "price-bots/badger-bot-token"
    # key value to retrieve secret value after boto3 call to secretsmanager
    bot_token_secret_key = "BOT_TOKEN_BADGER"

    badger_client = PriceBot(
        coingecko_token_id="badger-dao",
        token_display="BADGER",
        discord_id=os.getenv("BOT_ID_BADGER"),
        bot_token_secret_name=bot_token_secret_name,
        bot_token_secret_key=bot_token_secret_key,
    )

    bot_token = get_secret(bot_token_secret_name, bot_token_secret_key)
    loop.create_task(badger_client.start(bot_token))

    loop.run_forever()
