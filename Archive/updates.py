import requests
import pathlib
import simplejson as json
import argparse
import traceback
from modules.sendEmail import sendEmail

parser = argparse.ArgumentParser()

parser.add_argument("--key", "-k", help="set googledoc key")

args = parser.parse_args()

def load():
	print ("File does not exist")
	with open(key + '.json', 'w') as outfile:
		json.dump(data, outfile)
	trigger()

def exist():
	print ("File exist")
	with open(key + '.json') as f:
		json_data = json.load(f)
		if sorted(json_data.items()) == sorted(data.items()):
		    print("Same same")
		else:
			print("Different")
			with open(key + '.json', 'w') as outfile:
				json.dump(data, outfile)
				trigger()

def trigger():		
	if key == "1q5gdePANXci8enuiS4oHUJxcxC13d6bjMRSicakychE":
		# print ("run processData.py")
		# import processData
		import charts
		sendEmail("The Australian coronavirus tracking googledoc has been updated and new feeds and charts have been created", "Australian coronavirus tracking", ["andy.ball@theguardian.com","nick.evershed@theguardian.com","david.constable@theguardian.com"])

if args.key == "1q5gdePANXci8enuiS4oHUJxcxC13d6bjMRSicakychE":
	key = args.key
	print(args.key)
	data = requests.get('https://interactive.guim.co.uk/docsdata/' + key + '.json').json()['sheets']
	local = pathlib.Path(key + '.json')
	if local.exists ():
	    exist()
	else:
	    load()
else:
	print("Nothing to see here")
