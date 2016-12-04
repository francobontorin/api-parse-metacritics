#!/usr/bin/python

###########
# IMPORTS
###########
import sys
import getopt
import json
import requests
from bs4 import BeautifulSoup

############
# FUNCTIONS
############


def parse_url(link, headers):

	""" Parse Metacritics URLs
    
    Get a URL and parse the html using BeautifulSoup module

    :param link: The URL for Metacritics Top Games (By Metascore)
    :param headers: Default HTTP header
    :returns: The URL parsed
    """

	f = requests.get(link, headers=headers)
	if f.status_code != 200:
		print 'Error: Server returned status code %s' % f.status_code
		sys.exit(2)
	else:
		parsed = BeautifulSoup(f.text, 'html.parser')
		return parsed

def get_gamesdata(link, headers, title_class, metascore_class):

	""" Retrive Game Title and Score
    
    Using a parsed URL it finds the title(s) and game score

    :param title_class: The HTML class where the title can be found
    :param metascore_class: HTML where is the game metascore
    :returns: JSON with the Games/Scores
    """

	parsed_url = parse_url(link, headers)
	game_title = ['title: '+i.a.get_text().strip() for i in parsed_url.find_all("div", class_=title_class)]
	game_score = ['score: '+i.get_text().strip() for i in parsed_url.find_all("div", class_=metascore_class)]
	d = zip(game_title, game_score)
	return json.dumps(d, indent=4, sort_keys=True)

def rest_api(link, headers, title_class, metascore_class, payload):

	""" REST API 
    
    Exposed method to get PS3 Game title and score

    :param payload: Can be /games or /games/title_of_game
    :returns: JSON with the Games/Scores
    """

	parsed_url = parse_url(link, headers)
	if payload == '/games':
		rest = get_gamesdata(link, headers, title_class, metascore_class)
		return rest
	else:
		game_title = payload[7:]
		get_title = [i.get_text().strip() for i in parsed_url.find_all("div", class_=title_class) if game_title in i.get_text().strip()]
		for i in parsed_url.find_all("div", class_="product_wrap"):
			if game_title in i.get_text():
				get_score = [filter(None, i.get_text().splitlines())[2]]
		if get_title and get_score:
			d = zip(get_title, get_score)
			return json.dumps(d, indent=2, sort_keys=True)
		else:
			print 'Error: Game Title/Score not found'
			sys.exit(2)

def help_menu():
	print '---------------------------------------------'
	print 'Usage - Parsing Metacritics www contents'
	print '---------------------------------------------\n'
	print 'Options'
	print '\tparseMetacritics.py [-h] or [--help] [-p] or [--parse] [-r] or [--restapi]'  
	print '\n[-h] or [--help]\n'
	print '\tDisplay a help menu with the correct usage of the code'
	print '\n[-p] or [--parse]\n'
	print '\tThis option will parse an URL from Metacritics returning a JSON of the game titles and its related scores.'
	print '\n\tExamples:' 
	print '\t\tparseMetacritics.py --parse http://www.metacritic.com/browse/games/release-date/new-releases/ps4/metascore'
	print '\t\tparseMetacritics.py --parse http://www.metacritic.com/browse/games/release-date/new-releases/ps3/metascore'
	print '\n[-r] or [--restapi]\n'
	print '\tONLY for PS3 games, it returns all PS3 titles and scores or information about a specific game.'
	print '\n\tExamples:' 
	print '\t\tparseMetacritics.py --restapi "/games"'
	print '\t\tparseMetacritics.py --restapi "/games/Yakuza 5"'
	return
	
def main(argv):

	""" MAIN
    
    Main program function which calls the other functions 

    :param argv: Arguments passed via command line
    :returns: JSON with the Games/Scores
    """

	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
	top_ps3 = 'http://www.metacritic.com/browse/games/release-date/new-releases/ps3/metascore'

	try:
		opts, args = getopt.getopt(argv, "hp:r:",["help","parse=", "restapi=" ])
	except getopt.GetoptError:
		help_menu()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			help_menu()
			sys.exit()
		elif opt in ("-p", "--parse"):
			url = arg
			result = get_gamesdata(url, headers, "basic_stat product_title", "basic_stat product_score brief_metascore")
			if len(result) > 2:
				print result
			else:
				print 'Error: Json parsing failure, check the url', url
		elif opt in ("-r", "--restapi"):
			result = rest_api(top_ps3, headers, "basic_stat product_title", "basic_stat product_score brief_metascore", arg)
			print result
		else:
			"Error: Wrong argument passed, check -h for help"

if __name__ == "__main__":
	main(sys.argv[1:])