import discord
from discord.ext import commands
import motor.motor_asyncio
import config

intents = discord.Intents.default()

bot = commands.Bot(command_prefix=['howler ', 'Howler '], intents=intents)
database_client = motor.motor_asyncio.AsyncIOMotorClient(config.mongo_db_token)
bot.database = database_client['ArizonaCoyotesDiscord']
player_database = database_client['Players']
bot.player_collection = player_database['Players']
bot.trivia_database = database_client['database']
bot.image_database = database_client['images']

initial_extensions = ['cogs.TweetBot', 'cogs.NHLBot', 'cogs.TriviaBot', 'cogs.ImageBot']

whitelisted_channels = ['bot-spam', 'trivia', 'trivia-discussion', 'trivia-setup', 'test-commands', 'game-thread']
whitelisted_categories = [432008796106391565]

bot.image_commands = []

_cd = commands.CooldownMapping.from_cooldown(1.0, 60.0, commands.BucketType.channel)  # from ?tag cooldown mapping


@bot.check
async def restrict_commands(ctx):
    if ctx.channel.name in whitelisted_channels:
        return True
    elif ctx.channel.category.id in whitelisted_categories:
        return True
    else:
        return False


@bot.check
async def cool_down_check(ctx):
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
async def on_message(message):
    if message.content.startswith("howler ") or message.content.startswith("Howler "):
        res = message.content[0].lower() + message.content[1:]
        for command in bot.image_commands:
            if res == command.command:
                file = discord.File(f"images/{command.file}")
                await message.channel.send(file=file)
                return

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):  # if a command is a missing a certain argument
        await ctx.send("You're missing a required argument, use howler help <command name> to see the arguments!")
    elif isinstance(error, commands.CommandOnCooldown):  # if a command is cool down
        await ctx.send(error)
    elif isinstance(error, commands.CheckFailure):  # if the command failed a check
        await ctx.send("You do not have permission to use this command!")
    elif isinstance(error, commands.CommandInvokeError):  # if the command has an error in the code
        await ctx.send(
            f"{error}\nIf this is a \"KeyError:\" it's probably because the season you requested doesn't have the data "
            f"more recent seasons do, but I can probably write a specific error message for it. "
            f"DM Roman the command and the error message."
            f" If it isn't that error, DM Roman the info anyway.")
    elif isinstance(error, commands.CommandNotFound):  # if a command is not found and is in a valid channel
        if ctx.channel.name in whitelisted_channels or ctx.channel.category.id in whitelisted_categories:
            await ctx.send("That command doesn't exist, use howler help to find the correct usage!")
        else:
            pass
    else:  # anything not currently covered, new errors will be added when discovered
        await ctx.send(
            f"{error}\nIf you're getting this message, I don't have a check for this specific error, so congrats you "
            f"get to help Roman add a new one! yay! DM him with the command and error and he'll get around to it.")


@bot.command()
@commands.is_owner()
async def load(ctx, bot_extension):
    bot.load_extension(f'cogs.{bot_extension}')
    await ctx.send(f"Loaded the {bot_extension} cog")


@bot.command()
@commands.is_owner()
async def unload(ctx, bot_extension):
    bot.unload_extension(f'cogs.{bot_extension}')
    await ctx.send(f"Unloaded the {bot_extension} cog")


@bot.command()
@commands.is_owner()
async def reload(ctx, bot_extension):
    bot.unload_extension(f'cogs.{bot_extension}')
    bot.load_extension(f'cogs.{bot_extension}')
    await ctx.send(f"Reloaded the {bot_extension} cog")


if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

    bot.run(config.discord_token)
