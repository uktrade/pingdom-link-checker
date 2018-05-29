import os
import json
from urllib import request

def send_message(team):
    # Read team from shell
    team_slack_url = (os.environ.get('SLACK_' + team))
    slack_message = team + ': Broken links have been found on your site please investigate'
    # import pdb; pdb.set_trace()
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
