from django.core.management.base import BaseCommand, CommandError
from pylinkvalidator.api import crawl_with_options
from scrapesites.send_to_slack import send_message

import subprocess
import time


from scrapesites.models import Brokenlink, Urllist, Responsetime

class Command(BaseCommand):
    def handle(self, *args, **options):

        # If URL is no longer in check list, then delete failed links from table.
        on_start_clear_db()
        # import pdb; pdb.set_trace()

        print('Link check now running ...')

        dead_link_found = False
        t0 = time.time()

        # Loop through URL list and run link check.
        for current_url in Urllist.objects.filter(enable=True):
            print(current_url.site_url, " - Supported by: ", current_url.team)
            # import pdb; pdb.set_trace()
            count_404 = 0
            current_item_pos = 0

            ignore_prefix = '--ignore=' + current_url.ignore_prefix
            scan_results = subprocess.run(['pylinkvalidate.py', \
                            '--depth=4', \
                            '--workers=2', \
                            '--show-source', \
                            '--console', \
                            #'--types=a', \
                            '--test-outside', \
                            '--parser=lxml', \
                            '--header=Connection: keep-alive', \
                            '--header=Pragma: no-cache', \
                            '--header=Cache-Control: no-cache', \
                            '--header=Upgrade-Insecure-Requests: 1', \
                            '--header=Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', \
                            '--header=DNT: 1', \
                            '--header=Accept-Encoding: gzip, deflate', \
                            '--header=User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36 link-checker-ops', \
                            ignore_prefix, \
                            current_url.site_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            scan_result_list = scan_results.stdout.decode('utf-8').split('\n')

            # Check the scan results for broken links, 404s
            for item in scan_result_list:
                current_item_pos += 1
                # import pdb; pdb.set_trace()
                if item.lstrip(' ').startswith('not found (404)'):
                    # import pdb; pdb.set_trace()
                    count_404 += 1
                    dead_link_found = True
                    Urllist.objects.filter(site_url=current_url.site_url).update(broken_link_found=True)

                    # Record all the source and broken links and write to table and log file if unique.
                    for x in range(current_item_pos, current_item_pos + 2):
                        if (scan_result_list[x]).lstrip(' ').startswith('from'):
                            print('Source URL: ' + scan_result_list[x].lstrip(' ').rstrip("\n"))
                            source_url = scan_result_list[x].lstrip(' ').rstrip("\n")
                        if (scan_result_list[x]).lstrip(' ').startswith('<'):
                            print('Broken Link: ' + scan_result_list[x].lstrip(' ').rstrip("\n"))
                            broken_link = scan_result_list[x].lstrip(' ').rstrip("\n")
                            try:
                                # import pdb; pdb.set_trace()
                                Brokenlink.objects.get_or_create(
                                    site_url=current_url.site_url,
                                    source_url=source_url,
                                    broken_link=broken_link,
                                    temp_url=current_url,)
                            except:
                                print("entry exists")
                            
            # Clear checked url from table if no 404's found.
            if count_404 == 0:
                # import pdb; pdb.set_trace()
                Brokenlink.objects.filter(site_url=current_url.site_url).delete()
                Urllist.objects.filter(site_url=current_url.site_url).update(broken_link_found=False, slack_sent=False)
                # maybe send all clear slack?
               
        
        # Record time it took to run checks so that it can be displayed in
        # pingdoms response time.
        t1 = time.time()
        total_time = (t1 - t0) * 1000

        # import pdb; pdb.set_trace()
        # Ouput urls link status to pingdoms check XML,
        # this is what pingdom points to.
        if dead_link_found:
            defaults = {'response_time': total_time, 'previous_check_state': False}
            Responsetime.objects.update_or_create(id=1, defaults=defaults)


        else:
            defaults = {'response_time': total_time, 'previous_check_state': True}
            Responsetime.objects.update_or_create(id=1, defaults=defaults)


        # Send slack message to the team of failed check.
        for urllist in Urllist.objects.filter(broken_link_found=True, slack_sent=False):
            # import pdb; pdb.set_trace()
            if send_message(urllist.team):
                Urllist.objects.filter(site_url=urllist.site_url).update(slack_sent=True)
            else:
                print("Could not send slack message")


def on_start_clear_db():
    # import pdb; pdb.set_trace()
    for current_row in Brokenlink.objects.all().values():
        if current_row['site_url'] not in Urllist.objects.values_list('site_url', flat=True):
            Brokenlink.objects.filter(site_url=current_row['site_url']).delete()

