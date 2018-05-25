from django.core.management.base import BaseCommand, CommandError
from scrapesites.send_to_slack import send_message


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Sending message to slack")
        send_message()
