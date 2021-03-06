from asyncio import events
from typing import AsyncContextManager
from discord import guild
from discord import member
from discord import client
from discord.ext import commands
from config import settings
from discord.guild import Guild
import discord
import session, functions, users_stats, db_functions
import os

#bot = commands.Bot(command_prefix=settings['prefix'], intents=discord.Intents.all())
bot = commands.Bot(command_prefix=settings['prefix'])


# Events
@bot.event
async def on_ready():
    print('Приветствую, Господин.')
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
    print('Все модули загружены.')


@bot.event
async def on_member_join(member):
    print(f'{member} присоединился на сервер.')


@bot.event
async def on_member_remove(member):
    print(f'{member} покинул сервер.')


@bot.event
async def on_message(message):
    #print(f'{message.author}: {message.content}')
    author = message.author.name

    new_user = functions.find_user(author, session.all_users)
    
    if new_user:
        new_user.count_messages += 1
    else:
        # create new author with start stats
        new_user = users_stats.User(message.author.name)
        session.all_users.append(new_user)
        db_functions.create_user(new_user)

    # так как on_message перекрывает все команды
    await bot.process_commands(message)


bot.run(settings['token'])
