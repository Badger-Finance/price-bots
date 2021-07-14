import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from sett_bot import SettBot
from utils import get_secret

if __name__ == "__main__":
    with open("./contracts/abi/sett.json") as sett_abi_file:
        sett_abi = json.load(sett_abi_file)

    loop = asyncio.get_event_loop()
    # name of secret in secrets manager
    bot_token_secret_name = "price-bots/bdigg-bot-token"
    # key value to retrieve secret value after boto3 call to secretsmanager
    bot_token_secret_key = "BOT_TOKEN_BDIGG"

    bdigg_client = SettBot(
        coingecko_token_id="badger-sett-digg",
        token_display="bDIGG",
        token_address=os.getenv("BDIGG_ADDRESS"),
        token_abi=sett_abi,
        discord_id=os.getenv("BOT_ID_BDIGG"),
        underlying_decimals=9,
        bot_token_secret_name=bot_token_secret_name,
        bot_token_secret_key=bot_token_secret_key,
    )

    bot_token = get_secret(bot_token_secret_name, bot_token_secret_key)
    loop.create_task(bdigg_client.start(bot_token))

    loop.run_forever()
