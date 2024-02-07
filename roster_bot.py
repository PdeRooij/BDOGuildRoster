#!/usr/bin/env python
from scraper import PA_Scraper
from formatter import Formatter
from sage import Sage

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
admins = [int(id) for id in os.getenv('ADMIN_IDS').split(',')]
permitted_roles = [int(id) for id in os.getenv('PERMITTED_ROLE_IDS').split(',')]
serviced_channels = [ch for ch in os.getenv('SERVICED_CHANNELS').split(',')]
guild = os.getenv('GUILD_NAME')
region = os.getenv('REGION')
db_loc = os.getenv('DB')
roster_loc = f'{guild}_roster.html'

# Prepare scraper, logic and formatter
scraper = PA_Scraper(guild, region)
sage = Sage(db_loc)
formatter = Formatter()

# Initialise bot
bot = commands.Bot(command_prefix='!', intents=intent_config)

@bot.event
async def on_ready():
    print(f'{bot.user.name} is alive!')

def is_admin(user):
    """
    Checks if provided user is listed as bot admin.
    If so, the user has elevated priviliges to adjust the bot.
    :param user: A Discord user.
    :return: Whether or not a user is a bot admin.
    """
    return user.id in admins

def is_permitted(user):
    """
    Checks if provided user has a permitted role ID.
    If so, the user is allowed to command the bot.
    :param user: A Discord user.
    :return: Whether or not a user is permitted to command the bot.
    """
    user_role_ids = [role.id for role in user.roles]
    return any(id in permitted_roles for id in user_role_ids)

def is_serviced_channel(channel):
    """
    Checks if provided channel is serviced by bot.
    :param channel: A Discord channel.
    :return: Whether or not the channel is serviced by the bot.
    """
    return channel.name in serviced_channels

async def remove_previous_roster(channel):
    """
    Deletes a previously posted roster from the provided channel
    :param channel: A Discord channel.
    """
    # Loop through last five messages and delete a message if it starts with the roster line
    async for message in channel.history(limit=5):
        if message.content.startswith('Players currently in'):
            await message.delete()

# Define commands
@bot.command(name='permit?')
async def permission(ctx):
    # Check if user has any of the permitted roles (intersection of both lists)
    if is_permitted(ctx.message.author):
        await ctx.reply('At your service.')
    else:
        await ctx.reply('I will not obey you.')

@bot.command(name='admin?')
async def admin(ctx):
    # Check if user has any of the permitted roles (intersection of both lists)
    if is_admin(ctx.message.author):
        await ctx.reply('Yes master.')
    else:
        await ctx.reply('Who are you?.')

@bot.command()
async def greet(ctx):
    await ctx.send(f'Hi {ctx.message.author.mention}!')

@bot.command()
async def name(ctx):
    if is_serviced_channel(ctx.channel):
        await ctx.send(f'Your name is {ctx.message.author.display_name} (message deleted after 3 seconds)', delete_after=3.0)
        await ctx.message.delete()

@bot.command()
async def delete(ctx):
    """
    Delete user message and notify.
    :param ctx: Command context.
    """
    if is_serviced_channel(ctx.channel) and is_permitted(ctx.message.author):
        await ctx.message.delete()
        await ctx.send(f'{ctx.message.author.mention} Your message has been deleted!')

@bot.command()
async def purge(ctx, n: int = 0):
    """
    Deletes latest n messages.
    :param ctx: Command context.
    :param n: Number of messages to be purged (1 - 50).
    """
    # Only permitted users are allowed to delete multiple messages
    if is_permitted(ctx.author) and is_serviced_channel(ctx.channel) and 0 < n < 50: await ctx.channel.purge(limit=n+1)

@bot.command()
async def dummy(ctx, entity):
    """
    Posts a dummy table.
    :param ctx: Command context.
    :param entity: What dummy object to display.
    """
    # Delete user message and print dummy table
    if is_serviced_channel(ctx.channel) and is_permitted(ctx.message.author):
        await ctx.message.delete()
        if entity == 'roster':
            await ctx.send(formatter.format_roster('dummy_guild', scraper.dummy_roster()))
        if entity == 'changes':
            await ctx.send(formatter.format_roster_changes('dummy_guild', '0000-00-00 00:00:00', sage.dummy_roster_change()))

@bot.command()
async def update(ctx):
    """
    Updates the roster with the latest information.
    :param ctx: Command context.
    """
    # Check if user is allowed to update the roster
    if is_permitted(ctx.message.author) and is_serviced_channel(ctx.channel):
        # Remove the previous roster
        await remove_previous_roster(ctx.channel)
        # Post an updated roster
        cur_members = scraper.parse_roster()
        await ctx.send(formatter.format_roster(guild, cur_members))
        # Post roster changes
        changes = sage.compare_guild_members(cur_members)
        await ctx.send(formatter.format_roster_changes(guild, sage.last_update, changes))
    else:
        # Tell user they do not have a required role
        await ctx.send(f'{ctx.message.author.mention} you do not have permission to update the roster!')
    # Remove !update message
    await ctx.message.delete()

@bot.command()
async def disk_update(ctx):
    """
    Updates the roster from HTML stored on disk.
    :param ctx: Command context.
    """
    # Only admins may execute this command
    if is_admin(ctx.message.author) and is_serviced_channel(ctx.channel):
        # Remove the previous roster
        await remove_previous_roster(ctx.channel)
        # Post an updated roster read from disk
        cur_members = scraper.parse_roster(roster_loc)
        await ctx.send(formatter.format_roster(guild, cur_members))
        # Post roster changes
        changes = sage.compare_guild_members(cur_members)
        await ctx.send(formatter.format_roster_changes(guild, sage.last_update, changes))
    # Remove !update message
    await ctx.message.delete()

@bot.command()
async def alias(ctx, *args):
    """
    Allows adding and removing aliases.
    :param ctx: Command context.
    :param args: Arguments passed to the command. Can be names/aliases or the keyword remove.
    """
    # Only perform operation in serviced channels
    if is_serviced_channel(ctx.channel):
        # Anybody is allowed to add or remove their own alias
        if len(args) == 1:
            # If only one argument is provided, the user wishes to either add or remove their own alias
            if args[0] == 'remove':
                sage.remove_alias(ctx.message.author.display_name)
            else:
                sage.replace_alias(args[0], ctx.message.author.display_name)
        # Adding/removing aliases for others is only allowed for permitted roles
        elif is_permitted(ctx.message.author):
            if len(args) == 2:
                if args[0] == 'remove':
                    # Remove alias(es) of provided Discord user
                    sage.remove_alias(args[1])
                else:
                    # Add/replace alias of provided Discord user
                    sage.replace_alias(args[1], args[0])

    # Delete message from user
    await ctx.message.delete()

@bot.command()
async def whois(ctx, alias):
    """
    Looks up alias in database.
    :param ctx: Command context.
    :param alias: Name to look for.
    """
    if is_serviced_channel(ctx.channel):
        if alias.startswith('<@'):
            # Search by mention implies somebody is looking for an alias by Discord name
            await ctx.reply('I do not support searching by Discord name yet. :(')
        else:
            await ctx.reply(formatter.format_alias(sage.find_alias(alias), alias))

# Let it rip!
bot.run(TOKEN)
