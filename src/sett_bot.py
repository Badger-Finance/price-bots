import discord
from discord.ext import tasks
import os
from price_bot import PriceBot
import requests
import json
from time import sleep
from web3 import Web3

UPDATE_INTERVAL_SECONDS = 45


class SettBot(PriceBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # number of decimals for non interest bearing token (BADGER decimals for the bBADGER example)
        self.underlying_decimals = kwargs.get("underlying_decimals")

        self._get_token_data()

    @tasks.loop(seconds=UPDATE_INTERVAL_SECONDS)
    async def update_price(self):
        """
        Asynchronous function that runs every UPDATE_INTERVAL_SECONDS to get the current price and market of the
        token and update the bot's name and activity in the guild.
        """
        # first get latest token data
        self._get_token_data()

        # for badger sett tokens, write different activity string for AUM
        try:
            activity_string = (
                "aum=$"
                + self._get_number_label(self._get_aum())
                + " ratio="
                + str(self._get_underlying_ratio())
            )
        except ValueError as e:
            self.logger.error(e)
            activity_string = None

        if activity_string:
            self.logger.info("activity string: " + activity_string)
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
                                os.getenv("DISCORD_MONITORING_WEBHOOK_URL"),
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

    def _get_aum(self):
        return self._get_supply() * self.token_data.get("token_price_usd")

    def _get_supply(self):
        supply = (
            self.token_contract.functions.totalSupply().call()
            / 10 ** self.token_contract.functions.decimals().call()
        )
        self.logger.info(f"{self.token_display} supply: {supply}")
        return supply

    def _get_underlying_ratio(self):

        if self.token_display == "bDIGG":
            ratio = (
                self.token_contract.functions.balance().call()
                / self.token_contract.functions.totalSupply().call()
                * 10 ** (self.token_contract.functions.decimals().call() / 2)
            )
        else:
            ratio = (
                self.token_contract.functions.getPricePerFullShare().call()
                / 10 ** self.token_contract.functions.decimals().call()
            )

        print(f"ratio is {round(ratio, 3)}")
        return round(ratio, 3)

    def _get_latest_transfer_log(self):
        latest_block = self.web3.eth.get_block("latest").get("number")
        transfers = []
        log = []
        offset = 10

        print(f"latest block: {latest_block}")
        while len(log) != 2 and offset < 10001:
            transfers = (
                self.token_contract.events.Transfer()
                .createFilter(fromBlock=latest_block - offset)
                .get_all_entries()
            )
            # loop over transfer txs and check the logs, return first valid transfer
            for tx in reversed(transfers):
                tx_hash = tx["transactionHash"].hex()
                receipt = self.web3.eth.getTransactionReceipt(tx_hash)
                tx_log = self.token_contract.events.Transfer().processReceipt(receipt)
                if len(tx_log) == 2:
                    return tx_log
            offset = offset * 10

        if transfers == []:
            raise ValueError(f"Something wrong, no valid txs in last 10k blocks")
            # TODO: send message to mod to let them know something wrong with bot
