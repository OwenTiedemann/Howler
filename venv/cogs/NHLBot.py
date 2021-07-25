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

class Skater:
    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.assists = 0
        self.goals = 0
        self.pim = 0
        self.shots = 0
        self.games = 0
        self.hits = 0
        self.power_play_goals = 0
        self.power_play_points = 0
        self.faceoff_percentage = 0
        self.shot_percentage = 0
        self.game_winning_goals = 0
        self.overtime_goals = 0
        self.shorthanded_goals = 0
        self.shorthanded_points = 0
        self.plus_minus = 0
        self.points = 0

class Goalie:
    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.minutes = 0
        self.wins = 0
        self.losses = 0
        self.shutouts = 0
        self.games_played = 0
        self.games_started = 0
        self.minutes_played_add = 0
        self.minutes_played = 0
        self.seconds_add = 0
        self.seconds = 0
        self.shots_against = 0
        self.saves = 0
        self.goals_against = 0

    def set_minutes(self, time_on_ice):
        self.minutes_played_add, self.seconds_add = time_on_ice.split(':')
        self.minutes_played += int(self.minutes_played_add)
        self.seconds += int(self.seconds_add)

    def get_save_percentage(self):
        return self.saves / self.shots_against

    def get_goals_against_average(self):
        self.minutes_played += self.seconds/60
        return (self.goals_against * 60) / self.minutes_played


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
                            player_id = items2['person']['id']
                            position = items2['position']['code']
                            break

        if type == "season":
            player_url = f"https://statsapi.web.nhl.com/api/v1/people/{player_id}/stats?stats=statsSingleSeason&season={season}"
        elif type == "career":
            player_url = f"https://statsapi.web.nhl.com/api/v1/people/{player_id}/stats?stats=yearByYear"

        goals = 0
        assists = 0

        if position == "G":
            x = Goalie(name, position)
        else:
            x = Skater(name, position)

        async with aiohttp.ClientSession() as cs:
            async with cs.get(player_url) as r:
                res = await r.json()
                for items in res['stats']:
                    for items2 in items['splits']:
                        if type == "career":
                            if items2['league']['name'] == "NHL" or items2['league']['name'] == "National Hockey League":
                                if position == "G":
                                    print(items2['stat'])
                                    x.wins += items2['stat']['wins']
                                    x.losses += items2['stat']['losses']
                                    x.shots_against += items2['stat']['shotsAgainst']
                                    x.set_minutes(items2['stat']['timeOnIce'])
                                    x.saves += items2['stat']['saves']
                                    x.goals_against += items2['stat']['goalsAgainst']
                                    x.shutouts += items2['stat']['shutouts']
                                    x.games_played += items2['stat']['games']
                                    x.games_started += items2['stat']['gamesStarted']
                                else:
                                    x.goals += items2['stat']['goals']
                                    x.assists += items2['stat']['assists']
                                    x.pim += items2['stat']['pim']
                                    x.shots += items2['stat']['shots']
                                    x.games += items2['stat']['games']
                                    x.hits += items2['stat']['hits']
                                    x.power_play_goals += items2['stat']['powerPlayGoals']
                                    x.power_play_points += items2['stat']['powerPlayPoints']
                                    x.shot_percentage += items2['stat']['shotPct']
                                    x.game_winning_goals += items2['stat']['gameWinningGoals']
                                    x.overtime_goals += items2['stat']['overTimeGoals']
                                    x.shorthanded_goals += items2['stat']['shortHandedGoals']
                                    x.shorthanded_points += items2['stat']['shortHandedPoints']
                                    x.plus_minus += items2['stat']['plusMinus']
                                    x.points += items2['stat']['points']
                        elif type == "season":
                            if position == "G":
                                print(items2['stat'])
                                x.wins += items2['stat']['wins']
                                x.losses += items2['stat']['losses']
                                x.shots_against += items2['stat']['shotsAgainst']
                                x.set_minutes(items2['stat']['timeOnIce'])
                                x.saves += items2['stat']['saves']
                                x.goals_against += items2['stat']['goalsAgainst']
                                x.shutouts += items2['stat']['shutouts']
                                x.games_played += items2['stat']['games']
                                x.games_started += items2['stat']['gamesStarted']
                            else:
                                x.goals += items2['stat']['goals']
                                x.assists += items2['stat']['assists']
                                x.pim += items2['stat']['pim']
                                x.shots += items2['stat']['shots']
                                x.games += items2['stat']['games']
                                x.hits += items2['stat']['hits']
                                x.power_play_goals += items2['stat']['powerPlayGoals']
                                x.power_play_points += items2['stat']['powerPlayPoints']
                                x.shot_percentage += items2['stat']['shotPct']
                                x.game_winning_goals += items2['stat']['gameWinningGoals']
                                x.overtime_goals += items2['stat']['overTimeGoals']
                                x.shorthanded_goals += items2['stat']['shortHandedGoals']
                                x.shorthanded_points += items2['stat']['shortHandedPoints']
                                x.plus_minus += items2['stat']['plusMinus']
                                x.points += items2['stat']['points']

        if position == "G":
            goals_against_average = x.get_goals_against_average()
            save_percentage = x.get_save_percentage()
            if type == "career":
                embed = discord.Embed(
                    title=name,
                    description="Career Stats\n"
                                +"```\n"
                                +f"Wins:            {x.wins}\n"
                                +f"Losses:          {x.losses}\n"
                                +f"Shutouts:        {x.shutouts}\n"
                                +f"Games Played:    {x.games_played}\n"
                                +f"Games Started:   {x.games_started}\n"
                                +f"Shots Against:   {x.shots_against}\n"
                                +f"Saves:           {x.saves}\n"
                                +f"Goals Against:   {x.goals_against}\n"
                                +f"Save Percentage: {round(save_percentage, 3)}\n"
                                +f"GAA:             {round(goals_against_average, 2)}```"
                )
            elif type == "season":
                embed = discord.Embed(
                    title=name,
                    description=f"{season_start_year}-{season_end_year} Stats\n"
                                +"```\n"
                                +f"Wins:            {x.wins}\n"
                                +f"Losses:          {x.losses}\n"
                                +f"Shutouts:        {x.shutouts}\n"
                                +f"Games Played:    {x.games_played}\n"
                                +f"Games Started:   {x.games_started}\n"
                                +f"Shots Against:   {x.shots_against}\n"
                                +f"Saves:           {x.saves}\n"
                                +f"Goals Against:   {x.goals_against}\n"
                                +f"Save Percentage: {round(save_percentage, 3)}\n"
                                +f"GAA:             {round(goals_against_average, 2)}```"
                )

            await ctx.send(embed=embed)
        else:
            if type == "career":
                embed = discord.Embed(
                    title=name,
                    description=f"Career Stats\n"
                                +"```\n"
                                +f"Goals:              {x.goals}\n"
                                +f"Assists:            {x.assists}\n"
                                +f"Points:             {x.points}\n"
                                +f"PIM:                {x.pim}\n"
                                +f"Hits:               {x.hits}\n"
                                +f"Shots:              {x.shots}\n"
                                +f"Power Play Goals:   {x.power_play_goals}\n"
                                +f"Power Play Points:  {x.power_play_points}\n"
                                +f"Shorthanded Goals:  {x.shorthanded_goals}\n"
                                +f"Shorthanded Points: {x.shorthanded_points}\n"
                                +f"Overtime Goals:     {x.overtime_goals}\n"
                                +f"Game Winning Goals: {x.game_winning_goals}\n"
                                +f"Plus/Minus:         {x.plus_minus}```"
                )
            elif type == "season":
                embed = discord.Embed(
                    title=name,
                    description=f"{season_start_year}-{season_end_year} Stats\n"
                                +"```\n"
                                +f"Goals:              {x.goals}\n"
                                +f"Assists:            {x.assists}\n"
                                +f"Points:             {x.points}\n"
                                +f"PIM:                {x.pim}\n"
                                +f"Hits:               {x.hits}\n"
                                +f"Shots:              {x.shots}\n"
                                +f"Shot Pct:           {x.shot_percentage}\n"
                                +f"Power Play Goals:   {x.power_play_goals}\n"
                                +f"Power Play Points:  {x.power_play_points}\n"
                                +f"Shorthanded Goals:  {x.shorthanded_goals}\n"
                                +f"Shorthanded Points: {x.shorthanded_points}\n"
                                +f"Overtime Goals:     {x.overtime_goals}\n"
                                + f"Game Winning Goals: {x.game_winning_goals}\n"
                                +f"Plus/Minus:         {x.plus_minus}```"
                )
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(NHLBot(bot))