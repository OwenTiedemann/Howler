# Howler
A Discord Bot for the Arizona Coyotes Discord server

Howler command tutorial

Twitter

howler twitter add <channel> <handle>

-adds a twitter feed to the selected channel, handle must be exact to the twitter accounts handle or it won't work

	howler twitter add #craig-morgan CraigSMorgan

howler twitter remove <handle>

-removes a twitter feed from the server, handle must be exact or it won't work

	howler twitter remove CraigSMorgan

howler twitter list

-shows a list of all feeds currently running

NHL

howler nhl draft <year> <round> <team>

-shows a list of all draft picks in the criteria you selected. If you want to show a teams draft for that year with all picks, 
you have to enter 0 as the round or it won't work. You don't have to enter a team if you want to see all picks in a certain round

	howler nhl draft 2020 0 ARI
	howler nhl draft 2020 1 "Arizona Coyotes"
	howler nhl draft 2020 6

howler nhl player <name> <team> <season_start_year> <season_end_year> <type>

-shows entered players stats for career or season, type must be either "career" or "season" or it won't work. Name must be in quotations,
team should be if you use their whole name, but you can use their abbreviation without them

	howler nhl player "Christian Dvorak" ARI 2020 2021 career
	
	howler nhl player "Jaromir Jagr" "Pittsburgh Penguins" 1995 1996 season

howler nhl team next <team>

-shows teams next game, team must be in quotation if you use their whole but doesn't need them if you use their abbreviation

	howler nhl team next "Arizona Coyotes"

howler nhl team last <team>

-same as next but shows the previous game

	howler nhl team last "Arizona Coyotes"

howler nhl team roster <team>

-shows the roster of the team you input

	howler nhl team roster ARI
