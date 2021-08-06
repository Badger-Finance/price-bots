import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from digg_bot import DiggBot
from utils import get_secret

if __name__ == "__main__":
    with open("./contracts/abi/digg.json") as digg_abi_file:
        digg_abi = json.load(digg_abi_file)
    with open("./contracts/abi/btc_usd_oracle.json") as btc_oracle_abi_file:
        btc_oracle_abi = json.load(btc_oracle_abi_file)
    with open("./contracts/abi/digg_btc_oracle.json") as digg_oracle_abi_file:
        digg_oracle_abi = json.load(digg_oracle_abi_file)
    with open("./contracts/abi/uni_pool.json") as uni_pool_file:
        uni_pool_abi = json.load(uni_pool_file)
    with open("./contracts/abi/sushi_pool.json") as sushi_pool_file:
        sushi_pool_abi = json.load(sushi_pool_file)

    loop = asyncio.get_event_loop()
    # name of secret in secrets manager
    bot_token_secret_name = "price-bots/digg-bot-token"
    # key value to retrieve secret value after boto3 call to secretsmanager
    bot_token_secret_key = "BOT_TOKEN_DIGG"

    digg_client = DiggBot(
        coingecko_token_id="digg",
        token_display="DIGG",
        token_address=os.getenv("DIGG_ADDRESS"),
        token_abi=digg_abi,
        discord_id=os.getenv("BOT_ID_DIGG"),
        btc_oracle_abi=btc_oracle_abi,
        digg_oracle_abi=digg_oracle_abi,
        bot_token_secret_name=bot_token_secret_name,
        bot_token_secret_key=bot_token_secret_key,
        uni_pool_abi=uni_pool_abi,
        sushi_pool_abi=sushi_pool_abi,
    )

    bot_token = get_secret(bot_token_secret_name, bot_token_secret_key)
    loop.create_task(digg_client.start(bot_token))

    loop.run_forever()
