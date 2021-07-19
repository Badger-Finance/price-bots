import discord
from discord.ext import commands, tasks
import json
import logging
import math
import os
import requests
from time import sleep
from utils import get_secret
from web3 import Web3

logging.basicConfig(
    # filename="price_bots_log.txt",
    # filemode='a',
    # format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    # datefmt='%H:%M:%S',
    level=logging.INFO
)
UPDATE_INTERVAL_SECONDS = 45
cache = {}


class PriceBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("price-bot")
        if cache.get("session") == None:
            cache["session"] = requests.Session()
        if cache.get("web3") == None:
            web3_url = get_secret("price-bots/infura-url", "INFURA_URL")
            cache["web3"] = Web3(Web3.HTTPProvider(web3_url))
        self.session = cache.get("session")

        self.coingecko_token_id = kwargs.get("coingecko_token_id")
        self.token_display = kwargs.get("token_display")
        self.token_address = kwargs.get("token_address")
        self.token_abi = kwargs.get("token_abi") if kwargs.get("token_abi") else None
        self.monitoring_webhook_url = get_secret(
            "price-bots/monitoring-webhook", "DISCORD_MONITORING_WEBHOOK_URL"
        )
        self.bot_token = get_secret(
            kwargs.get("bot_token_secret_name"), kwargs.get("bot_token_secret_key")
        )
        if self.token_address and self.token_abi:
            self.web3 = cache.get("web3")
            self.token_contract = self.web3.eth.contract(
                address=self.web3.toChecksumAddress(self.token_address),
                abi=self.token_abi,
            )
        self.discord_id = kwargs.get("discord_id")
        self._get_token_data()

        self.update_price.start()

    async def on_ready(self):
        self.logger.info(f"Logged in as {self.user.name} {self.user.id}")

    @tasks.loop(seconds=UPDATE_INTERVAL_SECONDS)
    async def update_price(self):
        """
        Asynchronous function that runs every UPDATE_INTERVAL_SECONDS to get the current price and market of the
        token and update the bot's name and activity in the guild.
        """
        # first get latest token data
        self._get_token_data()

        activity_string = "mcap=$" + self._get_number_label(
            self.token_data.get("market_cap")
        )
        if self.token_display == "ibBTC":
            activity_string += " btc=" + str(
                round(self.token_data.get("token_price_btc"), 2)
            )
        activity = discord.Activity(
            name=activity_string,
            type=discord.ActivityType.playing,
        )
        await self.change_presence(activity=activity)
        for guild in self.guilds:
            self.logger.info(guild.members)
            for member in guild.members:
                if str(member.id) == self.discord_id:
                    try:
                        await member.edit(
                            nick=f"{self.token_display} $"
                            + str(self.token_data.get("token_price_usd"))
                        )
                    except Exception as e:
                        self.logger.error("Error updated nickname")
                        self.logger.error(e)
                        webhook = discord.Webhook.from_url(
                            self.monitoring_webhook_url,
                            adapter=discord.RequestsWebhookAdapter(),
                        )
                        embed = discord.Embed(
                            title=f"**{self.token_display} Price Bot Error**",
                            description=f"Error message: {e}",
                        )
                        webhook.send(embed=embed, username="Price Bot Monitoring")
                        # sleep and restart bot if breaks
                        sleep(10)
                        await self.logout()
                        await self.start(self.bot_token)

    @update_price.before_loop
    async def before_update_price(self):
        await self.wait_until_ready()  # wait until the bot logs in

    def _get_token_data(self):
        """
        Private function to make call to coingecko to retrieve price and market cap for the token and update
        token data property.
        """
        try:
            response = self.session.get(
                f"https://api.coingecko.com/api/v3/coins/{self.coingecko_token_id}"
            ).content
            token_data = json.loads(response)

            token_price_usd = (
                token_data.get("market_data").get("current_price").get("usd")
            )
            token_price_btc = (
                token_data.get("market_data").get("current_price").get("btc")
            )
            market_cap = token_data.get("market_data").get("market_cap").get("usd")

            self.token_data = {
                "token_price_usd": token_price_usd,
                "token_price_btc": token_price_btc,
                "market_cap": market_cap,
            }
        except json.JSONDecodeError:
            self.logger.error("Error decoding json")

    def _get_number_label(self, value: str) -> str:
        """
        Formats number in billions, millions, or thousands into Discord name friendly string

        Args:
            value (str): value between 0 - 999 billion

        Returns:
            str: formatted string. EG if 1,000,000,000 is passed in, will return 1B
        """
        # Nine Zeroes for Billions
        if abs(int(value)) >= 1.0e9:
            return str(round(abs(int(value)) / 1.0e9)) + "B"
        # Six Zeroes for Millions
        elif abs(int(value)) >= 1.0e6:
            return str(round(abs(int(value)) / 1.0e6)) + "M"
        # Three Zeroes for Thousands
        elif abs(int(value)) >= 1.0e3:
            return str(round(abs(int(value)) / 1.0e3)) + "K"
        else:
            return str(abs(int(value)))
