import discord
from discord.ext import commands
import aiohttp


class Player:
    def __init__(self, firstName, lastName, round, pick):
        self.firstName = firstName
        self.lastName = lastName
        self.round = round
        self.pick = pick

class NHLBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.group()
    async def nhl(self, ctx):
        pass

    async def getTeamID(self, team: str, year: int):
        if team == None:
            return None
        elif team == "Calgary Flames" or team == "CGY":
            return 20
        elif team == "Arizona Coyotes" or team == "ARI" or team == "PHX":
            if year < 2014 and year > 1995:
                return 27
            elif year < 1996:
                return 33
            else:
                return 53
        elif team == "Anaheim Ducks" or team == "ANA":
            pass
        elif team == "New Jersey Devils" or team == "NJD":
            return 1
        elif team == "New York Islanders" or team == "NYI":
            return 2
        elif team == "New York Rangers" or team == "NYR":
            return 3
        elif team == "Philadelphia Flyers" or team == "PHI":
            return 4
        elif team == "Pittsburgh Penguins" or team == "PIT":
            return 5
        elif team == "Boston Bruins" or team == "BOS":
            return 6

    async def get_nhl_draft_url(self, year, round, teamID):
        if teamID == None and round == 0:
            return 0
        elif round == 0:
            return f'https://records.nhl.com/site/api/draft?cayenneExp=draftedByTeamId={teamID}%20and%20draftYear={year}'
        elif teamID == None:
            return f'https://records.nhl.com/site/api/draft?cayenneExp=draftYear={year}%20and%20roundNumber={round}'
        else:
            return f'https://records.nhl.com/site/api/draft?cayenneExp=draftedByTeamId={teamID}%20and%20draftYear={year}%20and%20roundNumber={round}'

    @nhl.command()
    async def draft(self, ctx, year: int, round=0, team=None):
        player_list = []
        teamID = await self.getTeamID(team, year)
        url = await self.get_nhl_draft_url(year, round, teamID)
        if url == 0:
            await ctx.send("Invalid Arguments, input a team with round as 0 for all rounds, or input a round")
            return

        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()  # returns dict
                for key in res.items():
                        for values in key:
                            if values == "data" or values == "total" or type(values) is int:
                                pass
                            else:
                                for player in values:
                                    x = Player(player['firstName'], player['lastName'], player['roundNumber'], player['overallPickNumber'])
                                    player_list.append(x)

        players = ""
        for player in player_list:
            players += f"{player.firstName} {player.lastName}: pick {player.pick}: round {player.round}" + "\n"


        if team == None:
            embed = discord.Embed(
                title=f"{year} NHL Draft: Round {round}",
                description=players
            )
        elif round == 0:
            embed = discord.Embed(
                title=f"{team} {year} NHL Draft",
                description=players
            )
        else:
            embed = discord.Embed(
                title=f"{team} {year} draft round {round}",
                description=players
            )
        await ctx.send(embed=embed)


    @draft.error
    async def draft_error(self, ctx, error):
        await ctx.send(error)


def setup(bot):
    bot.add_cog(NHLBot(bot))