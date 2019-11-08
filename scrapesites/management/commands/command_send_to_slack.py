from django.core.management.base import BaseCommand, CommandError
from scrapesites.helper.send_to_slack import send_message


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_message('DIRECTORY')
