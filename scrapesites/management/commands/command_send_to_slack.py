from django.core.management.base import BaseCommand, CommandError
from scrapesites.send_to_slack import send_message


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_message('TEAM_DIRECTORY')
