from decimal import Decimal
import discord
from discord.ext import tasks
from price_bot import PriceBot
import os
import requests
import json
from time import sleep
from web3 import Web3

UPDATE_INTERVAL_SECONDS = 45

BTC_USD_ORACLE_ADDRESS = "0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c"
DIGG_BTC_ORACLE_ADDRESS = "0x418a6C98CD5B8275955f08F0b8C1c6838c8b1685"


class DiggBot(PriceBot):
    def __init__(self, *args, **kwargs):
        self.web3 = Web3(Web3.HTTPProvider(get_secret("price-bots/infura-url", "INFURA_URL")))
        self.digg_oracle_abi = kwargs.get("digg_oracle_abi")
        self.btc_oracle_abi = kwargs.get("btc_oracle_abi")
        self.btc_oracle_contract = self.web3.eth.contract(
            address=self.web3.toChecksumAddress(BTC_USD_ORACLE_ADDRESS),
            abi=self.btc_oracle_abi,
        )
        self.digg_oracle_contract = self.web3.eth.contract(
            address=self.web3.toChecksumAddress(DIGG_BTC_ORACLE_ADDRESS),
            abi=self.digg_oracle_abi,
        )
        # super down here because we need to read the digg oracle contract from web3 before init
        super().__init__(*args, **kwargs)

    @tasks.loop(seconds=UPDATE_INTERVAL_SECONDS)
    async def update_price(self):
        """
        Asynchronous function that runs every UPDATE_INTERVAL_SECONDS to get the current price and market of the
        token and update the bot's name and activity in the guild.
        """
        # first get latest token data
        self._get_token_data()

        activity_string = (
            "mcap=$"
            + self._get_number_label(self.token_data.get("market_cap"))
            + " btc="
            + str(round(self.token_data.get("token_price_btc"), 2))
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
                            + str(round(self.token_data.get("token_price_usd")))
                        )
                    except Exception as e:
                        self.logger.error("Error updated nickname")
                        self.logger.error(e)
                        webhook = discord.Webhook.from_url(os.getenv("DISCORD_MONITORING_WEBHOOK_URL"), adapter=discord.RequestsWebhookAdapter())
                        embed = discord.Embed(
                            title=f"**{self.token_display} Price Bot Error**",
                            description=f"Error message: {e}"
                        )
                        webhook.send(embed=embed, username="Price Bot Monitoring")

    @update_price.before_loop
    async def before_update_price(self):
        await self.wait_until_ready()  # wait until the bot logs in

    def _get_token_data(self):
        """
        Private function to make call to thegraph to retrieve price and market cap for the token and update
        token data property.
        """

        token_price_btc = self._get_digg_btc_price()
        token_price_usd = token_price_btc * self._get_btc_usd_price()
        market_cap = token_price_usd * Decimal(self._get_supply())

        self.token_data = {
            "token_price_usd": token_price_usd,
            "token_price_btc": token_price_btc,
            "market_cap": market_cap,
        }

    def _get_digg_btc_price(self) -> Decimal:

        return Decimal(
            self.digg_oracle_contract.functions.latestRoundData().call()[1] 
            / 10 ** 8
        )

    def _get_btc_usd_price(self) -> Decimal:

        return Decimal(
            self.btc_oracle_contract.functions.latestRoundData().call()[1] 
            / 10 ** 8
        )

    def _get_supply(self):
        supply = (
            self.token_contract.functions.totalSupply().call()
            / 10 ** self.token_contract.functions.decimals().call()
        )
        return supply
