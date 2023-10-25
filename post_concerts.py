
from mastodon import Mastodon
from urllib.request import urlopen 
from datetime import datetime

import argparse
import json
import hashlib
import pytz
import sys
import os

argparser=argparse.ArgumentParser()
argparser.add_argument('-c','--config', required=False, type=str, help='Optionally provide a path to a JSON file containing configuration options. If not provided, options must be supplied using command line flags.')
argparser.add_argument('--server', required=False, help="Required: The name of your server (e.g. `mstdn.thms.uk`)")
argparser.add_argument('--access-token', action="append", required=True, help="Required: The access token can be generated at https://<server>/settings/applications, and must have read:search, read:statuses and admin:read:accounts scopes. You can supply this multiple times, if you want tun run it for multiple users.")
argparser.add_argument('--timezone', action="append", required=False, help="Required: The timezone in the target region.")
argparser.add_argument('--apiurl', action="append", required=False, help="Required: The concertcloud API URL from which to fetch concerts.")

arguments = argparser.parse_args()

def log(text):
    print(f"{datetime.now()} {datetime.now().astimezone().tzinfo}: {text}")

if(arguments.config != None):
    if os.path.exists(arguments.config):
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        for key in config:
            setattr(arguments, key.lower().replace('-','_'), config[key])
    else:
        log(f"Config file {arguments.config} doesn't exist")
        sys.exit(1)

url = arguments.apiurl
ltz = pytz.timezone(arguments.timezone)

response = urlopen(url)
data = json.loads(response.read())

mastodon = Mastodon(access_token = arguments.access_token[0], api_base_url = arguments.server)

i = 0
while i < len(data["data"]):
    event = data["data"][i]
    jevent = json.dumps(event, indent=0).encode('utf-8')
    hash = hashlib.sha256(jevent)


    print("\n--------------------------------------------------\n")
    #print("\n\n" + hash.hexdigest())

    d = datetime.fromisoformat(event["date"])
    d = d.astimezone(ltz)

    status = "Toot d'éssai, votre avis s'il vous plait : fréquence, public/unlisted, etc.\n\n"
    status = status + event["title"] + "\n\n"
    status = status + event["location"] + " - " + event["city"] + " - "
    status = status + d.date().isoformat() + " " + d.timetz().strftime("%H:%M") + "\n\n"
    status = status + event["url"] + "\n\n"
    if "comment" in event:
        status = status + event["comment"][0:200] + "...\n\n"
    status = status + "https://www.concertcloud.live/contribute\n\n"
    status = status + "#ConcertCloud" + event["city"].title()
    status = status + " #ConcertCloud" + event["country"].title()
    status = status + " #ConcertCloud" + event["location"].title() + event["city"].title()
    print(status)

    mastodon.status_post(status, visibility = 'public')

    i = i + 1

