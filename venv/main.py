import discord
from discord.ext import commands
import motor.motor_asyncio
import config
import datetime

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=['howler ', 'Howler '], intents=intents)
database_client = motor.motor_asyncio.AsyncIOMotorClient(config.mongo_db_token)
bot.database = database_client['ArizonaCoyotesDiscord']
player_database = database_client['Players']
bot.player_collection = player_database['Players']
bot.trivia_database = database_client['database']
bot.image_database = database_client['images']

initial_extensions = ['cogs.TweetBot', 'cogs.NHLBot', 'cogs.TriviaBot', 'cogs.ImageBot', 'jishaku', 'cogs.OwnerCommands']

whitelisted_channels = ['bot-spam', 'trivia', 'trivia-discussion', 'trivia-setup', 'test-commands', 'game-thread']
whitelisted_categories = [432008796106391565]

_cd = commands.CooldownMapping.from_cooldown(1.0, 20.0, commands.BucketType.channel)  # from ?tag cooldown mapping

bot.image_commands = []

bot.max_messages = 1000


@bot.event
async def on_message(message):
    x = message.content.lower()
    if 'tocchet' in x:
        await message.add_reaction('\U0001F422')
    if message.content.startswith(("howler ", "Howler ")):
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
            f"{error}\n"
            f"DM Roman the command and the error message.")
    elif isinstance(error, commands.CommandNotFound):  # if a command is not found and is in a valid channel
        if ctx.channel.name in whitelisted_channels or ctx.channel.category.id in whitelisted_categories:
            await ctx.send("That command doesn't exist, use howler help to find the correct usage!")
        else:
            pass
    elif isinstance(error, commands.TooManyArguments):
        await ctx.send(error)
    else:  # anything not currently covered, new errors will be added when discovered
        await ctx.send(
            f"{error}\nIf you're getting this message, I don't have a check for this specific error, so congrats you "
            f"get to help Roman add a new one! yay! DM him with the command and error and he'll get around to it.")


@bot.event
async def on_message_delete(message):
    if message.author.id == bot.user.id:
        return
    if message.guild.id == 756640701751754812:
        channel = bot.get_channel(756640703165104179)
        embed = discord.Embed(
            title="Deleted Message"
        )
        if message.content != "":
            embed.add_field(name=f"Message Author: {message.author}\nMessage Content:",
                            value=f"```{message.content}```")
        else:
            embed.add_field(name=f"Message author: {message.author}", value=f"Image only message")
        embed.set_footer(text="Howler")
        embed.timestamp = datetime.datetime.utcnow()
        if message.attachments:
            embed.set_image(url=message.attachments[0])
        await channel.send(embed=embed)


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


if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

    bot.run(config.discord_token)
