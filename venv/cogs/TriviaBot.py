import discord
from discord.ext import commands, tasks
import motor.motor_asyncio


class TriviaBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_info = bot.trivia_database['server_info']

    @commands.group()
    async def trivia(self, ctx):
        pass

    @trivia.command()
    async def leaderboard(self, ctx, *, season=""):
        if season == "":
            x = await self.server_info.find_one()
            current_season = x['current_season']
            print(current_season)
        else:
            current_season = season

        await self.leaderboard_setup(ctx, current_season)

    async def leaderboard_setup(self, ctx, season):
        season_user_collection = self.bot.trivia_database[str(season)]

        if await season_user_collection.estimated_document_count() == 0:
            await ctx.send('The leaderboard is empty, complete a trivia question in the season first!')
            return

        userNames = []
        userScores = []

        users = await season_user_collection.find().to_list(length=None)

        for user in users:
            points, name = user['number_correct'], user['display_name']
            userNames.append(name)
            userScores.append(points)

        embed = discord.Embed(
            title=str(season) + " Trivia Leaderboard",
            color=discord.Colour.blue(),
        )

        zipped_lists = zip(userScores, userNames)
        sorted_pairs = sorted(zipped_lists)

        tuples = zip(*sorted_pairs)
        userScores, userNames = [list(tuple) for tuple in tuples]

        userScores.reverse()
        userNames.reverse()
        ranks = []
        for rank in range(len(userScores)):
            ranks.append(rank + 1)

        leaderboard_string = "```\n"

        for (user, score, rank) in zip(userNames, userScores, ranks):
            if rank > 10:
                break
            leaderboard_string += f"{rank:<3}{user:<20} {score}\n"

        leaderboard_string += "```"
        embed.description = leaderboard_string
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(TriviaBot(bot))