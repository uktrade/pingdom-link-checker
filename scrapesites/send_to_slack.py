import os
import json
from urllib import request
from scrapesites.models import Urllist

def send_message(team):
    # Read slack url from table
    # import pdb; pdb.set_trace()
    team_slack_url = Urllist.objects.get(team=team).slack_url
    slack_message = team + ': Broken links have been found on your site please investigate'
    if team_slack_url:
        print(slack_message)
        # print('URL: ' + team_slack_url)
        post = {"text": "{0}".format(slack_message)}
        try:
            json_data = json.dumps(post)
            req = request.Request(team_slack_url,
                                  data=json_data.encode('ascii'),
                                  headers={'Content-Type': 'application/json'})
            request.urlopen(req)
        except Exception as em:
            print("EXCEPTION: " + str(em))
        return True
    else:
        print("Env var for " + team + " doesn't exist")
        return False
