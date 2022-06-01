# price-bots
Discord price bots framework using CoinGecko, web3, and python.


### How to Run

#### Environment Variables
1. Copy and paste the `.example-env` contents into a new `.env` file. 
2. Provide the bot token fields with the discord client secrets for the bots you're trying to run. 
3. Provide the bot id fields with the user ids of the bots you're trying to run. 
4. Fill out the token address fields with the tokens you're representing with the price bots. 
5. Provide a web3 node URL
6. Provide a monitoring webhook if you'd like to receive alerts for some of the failures.

#### Build Project
Note: subject to change, docker structure less than ideal right now.

1. Run `docker-compose up -d` which will build and run all of the uncommented services in a background process
2. Run `docker-compose logs -f` if you want to stream the logs for the active services

In the case you need to restart or rebuild the images, following process works.
1. Stop running service using `docker-compose rm -s -v <service-name>`
2. Build new service container with updates using `docker-compose build <service-name>`
3. Delete old image to free up space by running `docker images` and then `docker image rm -f <image-id>`
4. Run new service in background with `docker-compose up -d <service-name>`

### Extending Structure
All the source code is in the `src/` directory. The `price-bot.py` file contains the most basic implementation to update a Discord bot with the current price and market cap of a token every 45 seconds using CoinGecko's API. The `sett-bot.py` and `digg-bot.py` classes extend the PriceBot class with unique modifications to get additional data and more accurate data. 

You can reference the DiggBot and SettBot classes for how to integrate Chainlink oracles and other web3 calls to get price information and display it using Discord.
