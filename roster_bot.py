#!/usr/bin/env python
from scraper import PA_Scraper
from formatter import Formatter

# Reading environment variables
import os
from dotenv import load_dotenv

# Discord stuff
import discord
from discord.ext import commands

# Configure intents
intent_config = discord.Intents.default()
intent_config.message_content = True

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
permitted_roles = [int(id) for id in os.getenv('PERMITTED_ROLE_IDS').split(',')]
guild = os.getenv('GUILD_NAME')
region = os.getenv('REGION')

# Prepare scraper and formatter
scraper = PA_Scraper(guild, region)
formatter = Formatter()

# Initialise bot
bot = commands.Bot(command_prefix='!', intents=intent_config)

@bot.event
async def on_ready():
    print(f'{bot.user.name} is alive!')

def is_permitted(user):
    """
    Checks if provided user has a permitted role ID.
    If so, the user is allowed to command the bot.
    :param user: A Discord user.
    :return: Whether or not a user is permitted to command the bot.
    """
    user_role_ids = [role.id for role in user.roles]
    return any(id in permitted_roles for id in user_role_ids)

# Define commands
@bot.command()
async def permission(ctx):
    # Check if user has any of the permitted roles (intersection of both lists)
    if is_permitted(ctx.message.author):
        await ctx.send('Yes master.')
    else:
        await ctx.send('I will not obey you.')

@bot.command()
async def greet(ctx):
    await ctx.send(f'Hi {ctx.message.author.mention}!')

@bot.command()
async def delete(ctx):
    """
    Delete user message and notify.
    :param ctx: Command context.
    """
    await ctx.message.delete()
    await ctx.send(f'{ctx.message.author.mention} Your message has been deleted!')

@bot.command()
async def purge(ctx, n: int = 0):
    """
    Deletes latest n messages.
    :param ctx: Command context.
    :param n: Number of messages to be purged.
    """
    # Only permitted users are allowed to delete multiple messages
    if is_permitted(ctx.author): await ctx.channel.purge(limit=n+1)

@bot.command()
async def dummy(ctx):
    """
    Posts a dummy table.
    :param ctx: Command context.
    """
    # Delete user message and print dummy table
    await ctx.message.delete()
    await ctx.send(formatter.format_table(scraper.dummy_roster()))

@bot.command()
async def update(ctx):
    """
    Posts a dummy table.
    :param ctx: Command context.
    """
    # Check if user is allowed to update the roster
    if is_permitted(ctx.message.author):
        # Post an updated roster
        await ctx.send(formatter.format_roster(guild, scraper.parse_roster()))
    else:
        # Tell user they do not have a required role
        await ctx.send(f'{ctx.message.author.mention} you do not have permission to update the roster!')
    # Remove !update message
    await ctx.message.delete()

# Let it rip!
bot.run(TOKEN)
