from django.core.management.base import BaseCommand, CommandError
import time
from scrapesites.helper.crawler import Scanner
from scrapesites.helper.DB import RecordManager as dbManager
from scrapesites.send_to_slack import send_message


class Command(BaseCommand):

    def __init__(self):
        self.scanner = Scanner()
        self.dbManager = dbManager()

    def handle(self, *args, **options):
        activeSites = set(self.dbManager.getActiveSites().values_list(
            'site_url', 'ignore_prefix', 'team'))
        t = time.perf_counter()
        for site, ignore_prefix, team in activeSites:
            errors = self.scanner.run(
                site=site, ignore_prefix=ignore_prefix, team=team)

            # Error arry is populated if an only if dead link (404) is found!
            if errors:
                # Update broken link found to True
                self.dbManager.updateBrokenLinkState(site=site, status=True)
                # ToDo:  Update Broken Links
                self.dbManager.updateBrokenLinks(site=site, errors=errors)
            else:
                # Update Broken link found to False
                self.dbManager.updateBrokenLinkState(site=site, status=False)
                # Delete all records related to current site from Brokeb link table
                self.dbManager.deleteSiteRecordsFromBrokenLinks(site=site)

        run_time = time.perf_counter() - t

        if self.dbManager.has_deadlinks():
            # if dead links found Update response_time and ,previous_check_state to False
            self.dbManager.updateResponseRecord(
                response_time=run_time, previous_check_state=False)
        else:
            # if no dead links Update response_time and ,previous_check_state to True
            self.dbManager.updateResponseRecord(
                response_time=run_time, previous_check_state=True)

        # Send Slack Update if it is Set to true

        # Send slack message to the team of failed check.
        for urllist in self.dbManager.getBrokenLinksWithPendingSlackSent():
            # import pdb; pdb.set_trace()
            if send_message(urllist.team):
                self.dbManager.updateSlackSentState(
                    site=urllist.site, slack_sent=True)
            else:
                print("Could not send slack message\nsite: {},team: {}".format(
                    urllist.site_url, urllist.team))
