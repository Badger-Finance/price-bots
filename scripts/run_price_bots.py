import asyncio
import json
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

from honey_badger import BadgerBot
from price_bot import PriceBot
from sett_bot import SettBot
from digg_bot import DiggBot

if __name__ == "__main__":
    with open("./contracts/abi/digg.json") as digg_abi_file, open(
        "./contracts/abi/sett.json"
    ) as sett_abi_file:
        digg_abi = json.load(digg_abi_file)
        sett_abi = json.load(sett_abi_file)

    loop = asyncio.get_event_loop()
    digg_client = DiggBot(
        coingecko_token_id="digg",
        token_display="DIGG",
        token_address=os.getenv("DIGG_ADDRESS"),
        token_abi=digg_abi,
        discord_id=os.getenv("BOT_ID_DIGG"),
    )
    bdigg_client = SettBot(
        coingecko_token_id="badger-sett-digg",
        token_display="bDIGG",
        token_address=os.getenv("BDIGG_ADDRESS"),
        token_abi=sett_abi,
        discord_id=os.getenv("BOT_ID_BDIGG"),
        underlying_decimals=9,
    )
    badger_client = PriceBot(
        coingecko_token_id="badger-dao",
        token_display="BADGER",
        discord_id=os.getenv("BOT_ID_BADGER"),
    )
    bbadger_client = SettBot(
        coingecko_token_id="badger-sett-badger",
        token_display="bBADGER",
        token_address=os.getenv("BBADGER_ADDRESS"),
        token_abi=sett_abi,
        discord_id=os.getenv("BOT_ID_BBADGER"),
        underlying_decimals=18,
    )

    loop.create_task(digg_client.start(os.getenv("BOT_TOKEN_DIGG")))
    loop.create_task(bdigg_client.start(os.getenv("BOT_TOKEN_BDIGG")))
    loop.create_task(badger_client.start(os.getenv("BOT_TOKEN_BADGER")))
    loop.create_task(bbadger_client.start(os.getenv("BOT_TOKEN_BBADGER")))

    loop.run_forever()
