#!/usr/bin/env python
import asyncio

from scraper import PA_Scraper

import sys          # Command line arguments
import os
from dotenv import load_dotenv

# Discord stuff
import discord


class RosterBot(discord.Client):

    def __init__(self, arg_list=None, **kwargs):
        # Configure intents
        intent_config = discord.Intents.default()
        intent_config.message_content = True
        # Pass on arguments to super
        super().__init__(intents=intent_config, **kwargs)

        # Prepare scraper
        scraper = PA_Scraper(arg_list[0], arg_list[1])

    async def on_ready(self):
        print(f'{self.user.name} is alive!')

    async def on_message(self, message):
        # Do not handle own messages or messages outside the serviced channel
        if message.author == bot.user or message.channel.name != os.getenv('SERVICED_CHANNEL'):
            return

        if '!greet' in message.content.lower():
            # Test by greeting user who sent command
            await message.channel.send(f'Hi {message.author}!')

        if '!delete' in message.content.lower():
            # Delete user message and notify
            channel = message.channel
            await message.delete()
            await channel.send('You have been deleted!')


# If executed, awaken Pie Bot
if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    guild = os.getenv('GUILD_NAME')
    region = os.getenv('REGION')
    # Pass command line arguments if provided
    if len(sys.argv) > 1:
        bot = RosterBot(sys.argv[1:], command_prefix='!')
    else:
        bot = RosterBot([guild, region], command_prefix='!')
    bot.run(TOKEN)
