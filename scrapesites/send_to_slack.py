import os
import json
from urllib import request

def send_message(team):
    # Read team from shell
    team_slack_url = (os.environ.get(team))
    # import pdb; pdb.set_trace()
    if team_slack_url:
        print(team + ': Broken links have been found on your site please investigate')
        print('URL: ' + team_slack_url)
        # post = {"text": "{0}".format(send_message_to_slack)}
        # slack_url = str(os.environ.get('WEBOPS_SLACK_URL'))
        # try:
        #     json_data = json.dumps(post)
        #     req = request.Request(slack_url,
        #                           data=json_data.encode('ascii'),
        #                           headers={'Content-Type': 'application/json'})
        #     request.urlopen(req)
        # except Exception as em:
        #     print("EXCEPTION: " + str(em))
        return True
    else:
        print("Env var for " + team + " doesn't exist")
        return False
