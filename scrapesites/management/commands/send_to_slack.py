from django.core.management.base import BaseCommand, CommandError
from urllib import request, parse
import os
import json

class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Sending message to slack")
        send_message_to_slack = 'Dude, this Slack message is coming from my Python program!'

        post = {"text": "{0}".format(send_message_to_slack)}
        slack_url = str(os.environ.get('WEBOPS_SLACK_URL'))
        try:
            json_data = json.dumps(post)
            req = request.Request(slack_url,
                                  data=json_data.encode('ascii'),
                                  headers={'Content-Type': 'application/json'})
            request.urlopen(req)
        except Exception as em:
            print("EXCEPTION: " + str(em))
