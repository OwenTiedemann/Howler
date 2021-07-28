import discord
from discord.ext import commands, tasks
import motor.motor_asyncio
import config

intents = discord.Intents.default()

bot = commands.Bot(command_prefix=['howler ', 'Howler '], intents=intents)
database_client = motor.motor_asyncio.AsyncIOMotorClient(config.mongo_db_token)
bot.database = database_client['ArizonaCoyotesDiscord']
bot.trivia_database = database_client['database']

initial_extensions = ['cogs.TweetBot', 'cogs.NHLBot', 'cogs.TriviaBot']

whitelisted_channels = ['bot-spam', 'trivia', 'trivia-discussion', 'trivia-setup', 'test-commands', 'game-thread']
whitelisted_categories = [432008796106391565]

_cd = commands.CooldownMapping.from_cooldown(1.0, 60.0, commands.BucketType.channel) # from ?tag cooldown mapping

@bot.check
async def restrict_commands(ctx):
    if ctx.channel.name in whitelisted_channels:
        return True
    elif ctx.channel.category.id in whitelisted_categories:
        return True
    else:
        return False

@bot.check
async def cooldown_check(ctx):
    if ctx.channel.category.id in whitelisted_categories:
        return True
    if ctx.channel.name == "game-thread":
        bucket = _cd.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after)
        return True
    else:
        return True

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You're missing a required argument, use howler help <command name> to see the arguments!")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(error)
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have permission to use this command!")
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send(f"{error}\nIf this is a \"KeyError:\" it's probably because the season you requested doesn't have the data more recent seasons do, sometimes I can fix that. \n If not, DM Roman with the command and the error and he'll fix it. Sorry")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send(f"{error}\nIf you're getting this message, I don't have a check for this specific error, so congrats you get to help Roman add a new one! yay! DM him with the command and error and he'll get around to it.")


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





