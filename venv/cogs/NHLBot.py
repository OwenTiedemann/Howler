import discord
from discord.ext import commands, menus
import aiohttp
import datetime
import unidecode


# Period class to represent a period in a hockey game
class Period:
    def __init__(self, period, home, away):
        self.period = period
        self.home = home
        self.away = away


# Player class to represent a player, used in nhl team roster and nhl player commands
class Player:
    def __init__(self, name, position, team):
        self.name = name
        self.position = position
        self.team = team
        self.jersey_number = 0


class Draftee(Player):
    def __init__(self, name, position, team, draft_round, pick, pick_history, drafted_from):
        super().__init__(name, position, team)
        self.draft_round = draft_round
        self.pick = pick
        self.pick_history = pick_history
        self.drafted_from = drafted_from


# Skater class to represent a skater, used in nhl player command
class Skater(Player):
    def __init__(self, name, position, team):
        super().__init__(name, position, team)
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

    def get_shooting_percentage(self):
        return (self.goals / self.shots) * 100


# Goalie class to represent a goalie, used in nhl player command
class Goalie(Player):
    def __init__(self, name, position, team):
        super().__init__(name, position, team)
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

    def set_minutes(self, time_on_ice):  # adds minutes to class variable
        self.minutes_played_add, self.seconds_add = time_on_ice.split(':')
        self.minutes_played += int(self.minutes_played_add)
        self.seconds += int(self.seconds_add)

    def get_save_percentage(self):  # retrieves save percentage by dividing saves by shots against
        return self.saves / self.shots_against

    def get_goals_against_average(self):  # retrieves GAA by dividing goals against by minutes played
        self.minutes_played += self.seconds / 60
        return (self.goals_against * 60) / self.minutes_played


def set_goalie_stats(x, stats, year):
    if year > 1954:  # only adds these stats if the year is after 1954
        x.shots_against += stats['stat']['shotsAgainst']
        x.saves += stats['stat']['saves']

    x.wins += stats['stat']['wins']
    x.losses += stats['stat']['losses']
    x.set_minutes(stats['stat']['timeOnIce'])
    x.goals_against += stats['stat']['goalsAgainst']
    x.shutouts += stats['stat']['shutouts']
    x.games_played += stats['stat']['games']
    x.games_started += stats['stat']['gamesStarted']

    return x


def set_goalie_embed(x, year_start, year_end, fetch_type):
    goals_against_average = x.get_goals_against_average()

    embed = discord.Embed(
        title=x.name
    )

    if year_start > 1954:  # sets this
        save_percentage = x.get_save_percentage()
        embed.description = "```\n" \
                            f"Games Played:    {x.games_played}\n" \
                            f"Wins:            {x.wins}\n" \
                            f"Losses:          {x.losses}\n" \
                            f"Shutouts:        {x.shutouts}\n" \
                            f"Games Played:    {x.games_played}\n" \
                            f"Games Started:   {x.games_started}\n" \
                            f"Shots Against:   {x.shots_against}\n" \
                            f"Saves:           {x.saves}\n" \
                            f"Goals Against:   {x.goals_against}\n" \
                            f"Save Percentage: {round(save_percentage, 3)}\n" \
                            f"GAA:             {round(goals_against_average, 2)}```"

    else:
        embed.description = "```\n" \
                            f"Games Played:    {x.games_played}\n" \
                            f"Wins:            {x.wins}\n" \
                            f"Losses:          {x.losses}\n" \
                            f"Shutouts:        {x.shutouts}\n" \
                            f"Games Played:    {x.games_played}\n" \
                            f"Games Started:   {x.games_started}\n" \
                            f"Goals Against:   {x.goals_against}\n" \
                            f"GAA:             {round(goals_against_average, 2)}```"

    if fetch_type == "career":
        embed.description = "Career Stats\n" + embed.description
    elif fetch_type == "season":
        embed.description = f"{year_start}-{year_end} Stats\n" + embed.description

    return embed


def set_skater_embed(x, year_start, year_end, fetch_type):
    embed = discord.Embed(
        title=x.name
    )

    if year_start > 1996:
        embed.description = "```\n" \
                            f"Games Played:       {x.games}\n" \
                            f"Goals:              {x.goals}\n" \
                            f"Assists:            {x.assists}\n" \
                            f"Points:             {x.points}\n" \
                            f"PIM:                {x.pim}\n" \
                            f"Hits:               {x.hits}\n" \
                            f"Shots:              {x.shots}\n" \
                            f"Shot Pct:           {round(x.get_shooting_percentage(), 1)}\n" \
                            f"Power Play Goals:   {x.power_play_goals}\n" \
                            f"Power Play Points:  {x.power_play_points}\n" \
                            f"Shorthanded Goals:  {x.shorthanded_goals}\n" \
                            f"Shorthanded Points: {x.shorthanded_points}\n" \
                            f"Overtime Goals:     {x.overtime_goals}\n" \
                            f"Game Winning Goals: {x.game_winning_goals}\n" \
                            f"Plus/Minus:         {x.plus_minus}```"

    elif year_start > 1958:
        embed.description = "```\n" \
                            f"Games Played:       {x.games}\n" \
                            f"Goals:              {x.goals}\n" \
                            f"Assists:            {x.assists}\n" \
                            f"Points:             {x.points}\n" \
                            f"PIM:                {x.pim}\n" \
                            f"Shots:              {x.shots}\n" \
                            f"Shot Pct:           {round(x.get_shooting_percentage(), 1)}\n" \
                            f"Power Play Goals:   {x.power_play_goals}\n" \
                            f"Power Play Points:  {x.power_play_points}\n" \
                            f"Shorthanded Goals:  {x.shorthanded_goals}\n" \
                            f"Shorthanded Points: {x.shorthanded_points}\n" \
                            f"Overtime Goals:     {x.overtime_goals}\n" \
                            f"Game Winning Goals: {x.game_winning_goals}\n" \
                            f"Plus/Minus:         {x.plus_minus}```"

    elif year_start > 1932:
        embed.description = "```\n" \
                            f"Games Played:       {x.games}\n" \
                            f"Goals:              {x.goals}\n" \
                            f"Assists:            {x.assists}\n" \
                            f"Points:             {x.points}\n" \
                            f"PIM:                {x.pim}\n" \
                            f"Power Play Goals:   {x.power_play_goals}\n" \
                            f"Power Play Points:  {x.power_play_points}\n" \
                            f"Shorthanded Goals:  {x.shorthanded_goals}\n" \
                            f"Shorthanded Points: {x.shorthanded_points}\n" \
                            f"Overtime Goals:     {x.overtime_goals}\n" \
                            f"Game Winning Goals: {x.game_winning_goals}```"

    else:
        embed.description = "```\n" \
                            + f"Games Played:       {x.games}\n" \
                            + f"Goals:              {x.goals}\n" \
                            + f"Assists:            {x.assists}\n" \
                            + f"Points:             {x.points}\n" \
                            + f"PIM:                {x.pim}\n" \
                            + f"Overtime Goals:     {x.overtime_goals}\n" \
                            + f"Game Winning Goals: {x.game_winning_goals}```"

    if fetch_type == "career":
        embed.description = "Career Stats\n" + embed.description
    elif fetch_type == "season":
        embed.description = f"{year_start}-{year_end} Stats\n" + embed.description

    return embed


def get_nhl_draft_url(year, draft_round, team_id):
    if team_id is None and draft_round == 0:
        return 0
    elif draft_round == 0:
        return f'https://records.nhl.com/site/api/draft?cayenneExp=draftedByTeamId={team_id}%20and%20draftYear={year}'
    elif team_id is None:
        return f'https://records.nhl.com/site/api/draft?cayenneExp=draftYear={year}%20and%20roundNumber={draft_round}'
    else:
        return f'https://records.nhl.com/site/api/draft?cayenneExp=draftedByTeamId={team_id}%20and%20draftYear={year}' \
               f'%20and%20roundNumber={draft_round} '


def getTeamID(team: str, year: int):
    if team is None:  # returns None if team is none
        return None

    # async with aiohttp.ClientSession() as cs:
    # async with cs.get("https://statsapi.web.nhl.com/api/v1/teams") as r:
    # res = await r.json()
    # for items in res['teams']:
    # if items['name'] == team or items['abbreviation'] == team:
    # print(items['id'])
    # return int(items['id'])

    # if statement tree for team ids, would use the above code, but it doesn't work for defunct teams or different names

    if team == "New Jersey Devils" or team == "NJD" or team == "Colorado Rockies" or team == "CLR" \
            or team == "Kansas City Scouts" or team == "KCS":
        if year < 1976:
            return 48
        elif year < 1982:
            return 35
        else:
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
    elif team == "Buffalo Sabres" or team == "BUF":
        return 7
    elif team == "Montreal Canadiens" or team == "MTL":
        return 8
    elif team == "Ottawa Senators" or team == "OTT" or team == "St Louis Eagles" or team == "SLE":
        if year < 1934:
            return 36
        elif year < 1935:
            return 45
        else:
            return 9
    elif team == "Toronto Maple Leafs" or team == "TOR":
        return 10

    elif team == "Atlanta Thrashers" or team == "ATL" or team == "Winnipeg Jets" or team == "WIN":
        if year < 2011:
            return 11
        else:
            return 52

    elif team == "Carolina Hurricanes" or team == "CAR" or team == "Hartford Whalers" or team == "HFD":
        if year < 1997:
            return 34
        else:
            return 12
    elif team == "Florida Panthers" or team == "FLA":
        return 13
    elif team == "Tampa Bay Lightning" or team == "TBL":
        return 14
    elif team == "Washington Capitols" or team == "WSH":
        return 15
    elif team == "Chicago Blackhawks" or team == "CHI":
        return 16
    elif team == "Detroit Red Wings" or team == "DET" or team == "Detroit Cougars" or team == "DCG" \
            or team == "Detroit Falcons" or team == "DFL":
        if year < 1930:
            return 40
        elif year < 1932:
            return 50
        else:
            return 17
    elif team == "Nashville Predators" or team == "NSH":
        return 18
    elif team == "St Louis Blues" or team == "STL":
        return 19
    elif team == "Calgary Flames" or team == "CGY" or team == "Atlanta Flames" or team == "AFM":
        if year < 1980:
            return 47
        else:
            return 20
    elif team == "Colorado Avalanche" or team == "COL" or team == "Quebec Nordiques" or team == "QUE":
        if year < 1995:
            return 32
        else:
            return 21
    elif team == "Edmonton Oilers" or team == "EDM":
        return 22
    elif team == "Vancouver Canucks" or team == "VAN":
        return 23
    elif team == "Anaheim Ducks" or team == "ANA":
        return 24
    elif team == "Dallas Stars" or team == "DAL" or team == "Minnesota North Stars" or team == "MNS":
        if year < 1993:
            return 31
        else:
            return 25
    elif team == "Los Angeles Kings" or team == "LAK":
        return 26
    elif team == "Arizona Coyotes" or team == "ARI" or team == "PHX":
        if 2014 > year > 1995:
            return 27
        elif year < 1996:
            return 33
        else:
            return 53
    elif team == "San Jose Sharks" or team == "SJS":
        return 28
    elif team == "Columbus Blue Jackets" or team == "CBJ":
        return 29
    elif team == "Minnesota Wild" or team == "MIN":
        return 30
    elif team == "Hamilton Tigers" or team == "HAM" or team == "Quebec Bulldogs" or team == "QBD":
        if year < 1920:
            return 42
        return 37
    elif team == "Pittsburgh Pirates" or team == "PIR" or team == "Philadelphia Quakers" or team == "QUA":
        if year < 1930:
            return 39
        else:
            return 38
    elif team == "Montreal Wanderers" or team == "MWN":
        return 41
    elif team == "Montreal Maroons" or team == "MMN":
        return 43
    elif team == "New York Americans" or team == "NYA" or team == "Brooklyn Americans" or team == "BRK":
        if year < 1941:
            return 44
        else:
            return 51
    elif team == "Oakland Seals" or team == "OAK" or team == "Cleveland Barons" or team == "CLE":
        if year < 1970:
            return 46
        else:
            return 49
    elif team == "Vegas Golden Knights" or team == "VGK":
        return 54
    elif team == "Seattle Kraken" or team == "SEA":
        return 55


def set_skater_stats(x, stats, year):
    if year > 1996:
        x.hits += stats['stat']['hits']
    if year > 1958:
        x.plus_minus += stats['stat']['plusMinus']
        x.shots += stats['stat']['shots']
    if year > 1932:
        x.power_play_goals += stats['stat']['powerPlayGoals']
        x.power_play_points += stats['stat']['powerPlayPoints']
        x.shorthanded_goals += stats['stat']['shortHandedGoals']
        x.shorthanded_points += stats['stat']['shortHandedPoints']

    x.goals += stats['stat']['goals']
    x.assists += stats['stat']['assists']
    x.pim += stats['stat']['pim']
    x.games += stats['stat']['games']
    x.game_winning_goals += stats['stat']['gameWinningGoals']
    x.overtime_goals += stats['stat']['overTimeGoals']
    x.points += stats['stat']['points']

    return x


class EmbedPages(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, entries):
        return entries


class NHLBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player_collection = bot.player_collection

    @commands.group()  # invoke_without_command=True)
    async def nhl(self, ctx):
        pass

    @nhl.command()
    async def draft(self, ctx, year: int, draft_round=0, team=None):

        player_list = []

        team_id = getTeamID(team, year)

        url = get_nhl_draft_url(year, draft_round, team_id)
        if url == 0:
            await ctx.send("Invalid Arguments, input a team with round as 0 for all rounds, or input a round")
            return

        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()  # returns dict
                print(res)
                for player in res['data']:
                    x = Draftee(player['playerName'],
                                player['position'],
                                player['triCode'],
                                player['roundNumber'],
                                player['overallPickNumber'],
                                player['teamPickHistory'],
                                f"{player['amateurClubName']} {player['amateurLeague']}")
                    player_list.append(x)

        embed_list = []

        for player in player_list:
            embed = discord.Embed(
                title=f"{year} Draft: Pick {player.pick}",
                description="```"
                            f"Player:       {player.name}\n"
                            f"Pick:         {player.pick}\n"
                            f"Round:        {player.draft_round}\n"
                            f"Position:     {player.position}\n"
                            f"Drafted From: {player.drafted_from}\n"
                            f"Drafted By:   {player.team}\n"
                            f"Pick History: {player.pick_history}\n"
                            f"```"
            )

            embed_list.append(embed)

        pages = menus.MenuPages(source=EmbedPages(embed_list), clear_reactions_after=True)
        await pages.start(ctx)

    @nhl.command()
    async def player(self, ctx, name, team, season_start_year: int, season_end_year: int, fetch_type: str):
        type_list = ["career", "season"]
        if fetch_type not in type_list:
            await ctx.send("Type must be either \"career\" or \"season\"")

        name = unidecode.unidecode(name)  # decodes name for special symbols

        player = await self.bot.player_collection.find_one({'fullName': name})
        season = str(season_start_year) + str(season_end_year)

        if player is None:  # if player is not already in the database
            team_id = getTeamID(team, season_start_year)  # get the team ID
            season = str(season_start_year) + str(season_end_year)  # put together a valid seasons string
            team_url = f"https://statsapi.web.nhl.com/api/v1/teams/{team_id}?expand=team.roster&season={season}"
            # build the api url call
            print(team_url)  # print it for debugging purposes
            player_id = None  # set player id to none for a check later

            async with aiohttp.ClientSession() as cs:  # gets the data from the website
                async with cs.get(team_url) as r:
                    res = await r.json()
                    print(res)  # prints the dict for debugging purposes
                    if 'teams' in res:
                        for items in res['teams']:
                            for items2 in items['roster']['roster']:
                                if name == unidecode.unidecode(
                                        items2['person']['fullName']):  # decodes name from database and checks it
                                    player_id = items2['person']['id']
                                    player_name = unidecode.unidecode(items2['person']['fullName'])
                                    position = items2['position']['code']
                                    break
                    else:  # if it was an invalid url it will return this string
                        await ctx.send(f'I couldn\'t find {team} for the {season_start_year}-{season_end_year} season! '
                                       f'Sorry, blame the NHL. '
                                       f'Or blame yourself if it didn\'t exist then. Your fault.')
                        return

            if player_id is None:  # if it couldn't find the player on that roster, it returns this string
                await ctx.send("Player not found, try again.")
                return

            else:  # double checks to make sure the player was not in the database and does nothing if it is
                if await self.bot.player_collection.count_documents({"_id": player_id}, limit=1) != 0:
                    pass
                else:  # adds the player to the database
                    player_dict = {"_id": player_id, 'fullName': player_name, 'position': position}
                    await self.bot.player_collection.insert_one(player_dict)

        else:  # if the player was in the database it sets these values
            player_id = player['_id']
            position = player['position']

        player_url = ""

        if fetch_type == "season":  # builds the url for a player for one season
            player_url = f"https://statsapi.web.nhl.com/api/v1/people/{player_id}" \
                         f"/stats?stats=statsSingleSeason&season={season}"
        elif fetch_type == "career":  # builds the url for a player for their career
            player_url = f"https://statsapi.web.nhl.com/api/v1/people/{player_id}/stats?stats=yearByYear"

        if position == "G":  # creates a class for the player
            x = Goalie(name, position, team)
        else:
            x = Skater(name, position, team)

        async with aiohttp.ClientSession() as cs:  # pulls data from the website
            async with cs.get(player_url) as r:
                res = await r.json()
                for items in res['stats']:
                    for items2 in items['splits']:
                        year = int(str(items2['season'])[
                                   :4])  # gets the first year of the season so that it can check what values are valid
                        if fetch_type == "career":
                            if items2['league']['name'] == "NHL" \
                                    or items2['league']['name'] == "National Hockey League":  # only checks stats for
                                # NHL seasons
                                if position == "G":
                                    x = set_goalie_stats(x, items2, year)
                                else:

                                    x = set_skater_stats(x, items2, year)

                        elif fetch_type == "season":  # just checks that year stats
                            if position == "G":
                                x = set_goalie_stats(x, items2, year)
                            else:
                                x = set_skater_stats(x, items2, year)

        if position == "G":  # builds goalie embed
            embed = set_goalie_embed(x, season_start_year, season_end_year, fetch_type)
            await ctx.send(embed=embed)
        else:  # builds skater embed
            embed = set_skater_embed(x, season_start_year, season_end_year, fetch_type)
            await ctx.send(embed=embed)

    @nhl.group()
    async def team(self, ctx):
        pass

    @team.command()
    async def next(self, ctx, team):
        team_id = getTeamID(team, datetime.datetime.now().year)
        team_url = f"https://statsapi.web.nhl.com/api/v1/teams/{team_id}?expand=team.schedule.next"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(team_url) as r:
                res = await r.json()
                print(res)
                for matchup in res['teams']:
                    if 'nextGameSchedule' in matchup:
                        for schedule in matchup['nextGameSchedule']['dates']:
                            for game in schedule['games']:
                                game_date = datetime.datetime.strptime(game['gameDate'], '%Y-%m-%dT%H:%M:%S%f%z')
                                game_status = game['status']
                                away_team = game['teams']['away']
                                home_team = game['teams']['home']
                    else:
                        await ctx.send(
                            "Look, there's two things that could've happened here. One, you asked for a team that "
                            "doesn't exist, in which case this is your fault. "
                            " Two, I screwed up and you're allowed to yell at me. I hope it's the first one.")
                        return

        embed = discord.Embed(
            title=f"{away_team['team']['name']} AT {home_team['team']['name']}",
            description=f"```Date: {game_date} \nStatus: {game_status['detailedState']}```"
        )

        embed.add_field(name=f"{away_team['team']['name']}",
                        value=f"```Record: {away_team['leagueRecord']['wins']}-{away_team['leagueRecord']['losses']}-"
                              f"{away_team['leagueRecord']['ot']}```")
        embed.add_field(name=f"{home_team['team']['name']}",
                        value=f"```Record: {home_team['leagueRecord']['wins']}-{home_team['leagueRecord']['losses']}-"
                              f"{home_team['leagueRecord']['ot']}```")

        await ctx.send(embed=embed)

    @team.command()
    async def last(self, ctx, team):
        period_list = []

        team_id = getTeamID(team, datetime.datetime.now().year)
        team_url = f"https://statsapi.web.nhl.com/api/v1/teams/{team_id}?expand=team.schedule.previous"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(team_url) as r:
                res = await r.json()
                for matchup in res['teams']:
                    if 'previousGameSchedule' in matchup:
                        for schedule in matchup['previousGameSchedule']['dates']:
                            for game in schedule['games']:
                                game_date = datetime.datetime.strptime(game['gameDate'], '%Y-%m-%dT%H:%M:%S%f%z')
                                game_status = game['status']
                                game_id = game['gamePk']
                                away_team = game['teams']['away']
                                home_team = game['teams']['home']
                    else:
                        await ctx.send(
                            "Look, there's two things that could've happened here. "
                            "One, you asked for a team that doesn't exist, in which case this is your fault."
                            "Two, I screwed up and you're allowed to yell at me. I hope it's the first one.")
                        return

        game_url = f"https://statsapi.web.nhl.com/api/v1/game/{game_id}/linescore"

        async with aiohttp.ClientSession() as cs:
            async with cs.get(game_url) as r:
                res = await r.json()
                print(res)
                for period in res['periods']:
                    x = Period(period['ordinalNum'], period['home'], period['away'])
                    period_list.append(x)

        embed = discord.Embed(
            title=f"{away_team['team']['name']} AT {home_team['team']['name']}",
            description=f"```Date: {game_date} \nStatus: {game_status['detailedState']} \nScore: {away_team['score']}-"
                        f"{home_team['score']}```"
        )

        away_periods = ""
        home_periods = ""

        for period in period_list:
            away_periods += f"{period.period} period:\n Shots: {period.away['shotsOnGoal']}\n" \
                            f" Goals: {period.away['goals']}\n"
            home_periods += f"{period.period} period:\n Shots: {period.home['shotsOnGoal']}\n" \
                            f" Goals: {period.home['goals']}\n"

        embed.add_field(name=f"{away_team['team']['name']}",
                        value=f"```Record: {away_team['leagueRecord']['wins']}-{away_team['leagueRecord']['losses']}-"
                              f"{away_team['leagueRecord']['ot']}\n{away_periods}```")
        embed.add_field(name=f"{home_team['team']['name']}",
                        value=f"```Record: {home_team['leagueRecord']['wins']}-{home_team['leagueRecord']['losses']}-"
                              f"{home_team['leagueRecord']['ot']}\n{home_periods}```")

        await ctx.send(embed=embed)

    @team.command()
    @commands.cooldown(1, 60, commands.BucketType.channel)
    async def roster(self, ctx, team, season_start_year, season_end_year):
        forward_list = []
        defencemen_list = []
        goalie_list = []

        team_id = getTeamID(team, int(season_start_year))
        if team_id is None:
            await ctx.send("Couldn't find that team, try again.")
            return
        season = str(season_start_year) + str(season_end_year)

        team_url = f"https://statsapi.web.nhl.com/api/v1/teams/{team_id}?expand=team.roster&season={season}"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(team_url) as r:
                res = await r.json()
                print(res)
                if 'teams' in res:
                    for team_dict in res['teams']:
                        for player in team_dict['roster']['roster']:
                            x = Player(player['person']['fullName'],
                                       player['position']['code'],
                                       team)
                            x.name = player['person']['fullName']
                            x.position = player['position']['code']
                            if 'jerseyNumber' in player:
                                x.jersey_number = player['jerseyNumber']
                            else:
                                pass
                            if player['position']['code'] == "D":
                                defencemen_list.append(x)
                            elif player['position']['code'] == "G":
                                goalie_list.append(x)
                            else:
                                forward_list.append(x)
                else:
                    await ctx.send(f'I couldn\'t find {team} for the {season_start_year}-{season_end_year} season! '
                                   f'Sorry, blame the NHL. '
                                   f'Or blame yourself if it didn\'t exist then. Your fault.')
                    return

        forwards_string = f"```"
        defencemen_string = f"```"
        goalies_string = f"```"

        for forward in forward_list:
            forwards_string += f"{forward.jersey_number:<3}{forward.position} {forward.name}\n"

        forwards_string += "```"

        for defenceman in defencemen_list:
            defencemen_string += f"{defenceman.jersey_number:<3}{defenceman.position} {defenceman.name}\n"

        for goalie in goalie_list:
            goalies_string += f"{goalie.jersey_number:<3}{goalie.position} {goalie.name}\n"

        defencemen_string += "```"
        goalies_string += "```"

        type_list = ['Forwards', 'Defencemen', 'Goalies']

        string_list = [forwards_string, defencemen_string, goalies_string]
        embed_list = []

        for position_type, string in zip(type_list, string_list):
            embed = discord.Embed(
                title=f"{team} {season_start_year}-{season_end_year} {position_type}",
                description=string
            )
            embed_list.append(embed)

        pages = menus.MenuPages(source=EmbedPages(embed_list), clear_reactions_after=True)
        await pages.start(ctx)


def setup(bot):
    bot.add_cog(NHLBot(bot))
