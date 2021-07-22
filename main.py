import config
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Cog
import motor.motor_asyncio

intents = discord.Intents.default()

bot = commands.Bot(command_prefix=['howler '], intents=intents)
database_client = motor.motor_asyncio.AsyncIOMotorClient(config.mongo_db_token)
bot.database = database_client['ArizonaCoyotesDiscord']

initial_extensions = ['cogs.TweetBot']


@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f"Loaded the {extension} cog")


@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f"Unloaded the {extension} cog")


@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f"Reloaded the {extension} cog")

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

    bot.run(config.discord_token)





