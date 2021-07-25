import discord
from discord.ext import commands
import aiohttp
import json


class Player:
    def __init__(self, firstName, lastName, position, round, pick, team):
        self.firstName = firstName
        self.lastName = lastName
        self.position = position
        self.round = round
        self.pick = pick
        self.team = team

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
                                print(player)
                                x = Player(player['firstName'], player['lastName'], player['position'], player['roundNumber'], player['overallPickNumber'], player['teamPickHistory'])
                                player_list.append(x)

        players = ""

        if team == None:
            for player in player_list:
                players += f"{player.position} {player.firstName} {player.lastName}: pick {player.pick}: {player.team}" + "\n"

            embed = discord.Embed(
                title=f"{year} NHL Draft: Round {round}",
                description=players
            )
        elif round == 0:
            for player in player_list:
                players += f"{player.position} {player.firstName} {player.lastName}: pick {player.pick}: round {player.round}: {player.team}" + "\n"

            embed = discord.Embed(
                title=f"{team} {year} NHL Draft",
                description=players
            )
        else:
            for player in player_list:
                players += f"{player.position} {player.firstName} {player.lastName}: pick {player.pick}" + "\n"

            embed = discord.Embed(
                title=f"{team} {year} draft round {round}",
                description=players
            )
        await ctx.send(embed=embed)


    @draft.error
    async def draft_error(self, ctx, error):
        await ctx.send(error)

    def Convert(lst):
        res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
        return res_dct

    @nhl.command()
    async def player(self, ctx, name, team, season_start_year: int, season_end_year: int, type: str):

        teamID = await self.getTeamID(team, season_start_year)
        season = str(season_start_year) + str(season_end_year)
        team_url = f"https://statsapi.web.nhl.com/api/v1/teams/{teamID}?expand=team.roster&season={season}"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(team_url) as r:
                res = await r.json()
                for items in res['teams']:
                    for items2 in items['roster']['roster']:
                        if name == items2['person']['fullName']:
                            print(items2['position'])
                            player_id = items2['person']['id']
                            position = items2['position']['code']
                            break

        if type == "season":
            player_url = f"https://statsapi.web.nhl.com/api/v1/people/{player_id}/stats?stats=statsSingleSeason&season={season}"
        elif type == "career":
            player_url = f"https://statsapi.web.nhl.com/api/v1/people/{player_id}/stats?stats=yearByYear"

        goals = 0
        assists = 0
        wins = 0
        losses = 0
        save_percentage = []
        goals_against_average = []

        async with aiohttp.ClientSession() as cs:
            async with cs.get(player_url) as r:
                res = await r.json()
                for items in res['stats']:
                    for items2 in items['splits']:
                        if type == "career":
                            if items2['league']['name'] == "NHL" or items2['league']['name'] == "National Hockey League":
                                if position == "G":
                                    print(items2['stat'])
                                    wins += items2['stat']['wins']
                                    losses += items2['stat']['losses']
                                    save_percentage.append(items2['stat']['savePercentage'])
                                    goals_against_average.append(items2['stat']['goalAgainstAverage'])
                                else:
                                    goals += items2['stat']['goals']
                                    assists += items2['stat']['assists']
                        else:
                            if position == "G":
                                print(items2['stat'])
                                wins += items2['stat']['wins']
                                losses += items2['stat']['losses']
                                save_percentage.append(items2['stat']['savePercentage'])
                                goals_against_average.append(items2['stat']['goalAgainstAverage'])
                            else:
                                goals += items2['stat']['goals']
                                assists += items2['stat']['assists']


        if position == "G":
            average_svp = sum(save_percentage) / len(save_percentage)
            average_gaa = sum(goals_against_average) / len(goals_against_average)
            await ctx.send(f"wins: {wins} losses: {losses} save percentage: {round(average_svp, 3)} GAA: {round(average_gaa, 2)} Note: SVP and GAA slighly off from actual values due to API issues")
        else:
            points = goals + assists
            await ctx.send(f"goals: {goals} assists: {assists} points: {points}")




def setup(bot):
    bot.add_cog(NHLBot(bot))