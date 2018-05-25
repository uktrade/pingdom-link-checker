from django.core.management.base import BaseCommand, CommandError
from pylinkvalidator.api import crawl_with_options
from scrapesites.send_to_slack import send_message

#import psycopg2
import subprocess
import os
import time
import json

from scrapesites.models import Urllist, Url_status, Responsetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        #connection = psycopg2.connect("dbname='url_results' user='checker' host='localhost' password='checker'")

        xml_out_1, xml_out_2, xml_out_5 = initialize_check_xml_format()
        # On start also clear table for ol urls that no longr exists
        on_start_get_status()
        # import pdb; pdb.set_trace()
        # interval = int(os.environ.get('CHECK_INTERVAL'))

        print('I am running check')

        dead_link_found = False
        t0 = time.time()

        # Create logs.html for storing link check results.
        with open('scrapesites/templates/logs.html', 'w') as out:
            out.write('{}\n{}\n{}\n{}\n'.format('<html>', '<body>', '<h1>Link check - logs</h1>', '<p>'))

        for url_list in Urllist.objects.filter(enable=True):
            print(url_list.url, " ", url_list.team)
            # import pdb; pdb.set_trace()
            count_404 = 0
            current_item_pos = 0
            # Update log file with url name.

            with open('scrapesites/templates/logs.html', 'a') as out:
                out.write('{}{}'.format('<br>', url_list.url))
            # import pdb; pdb.set_trace()
            # output_results = crawl_with_options(["https://www.createdbypete.com"], {"show-source": True, "output": "/Users/jay/Documents/Work/DIT/Work/WebOps/pingdom-link-checker/"})
            subprocess.run(['pylinkvalidate.py', '--depth=4', '--show-source', '--output=url.out', url_list.url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            f = open('url.out', 'r')
            lines = f.readlines()
            f.close()
            # print (lines)
            for item in lines:
                current_item_pos += 1
                # import pdb; pdb.set_trace()
                if item.lstrip(' ').startswith('not found (404)'):
                    #import pdb; pdb.set_trace()
                    count_404 += 1
                    dead_link_found = True
                    Urllist.objects.filter(url=url_list.url).update(bad_link=True)
                    if count_404 < 2:
                        with open('scrapesites/templates/logs.html', 'a') as out:
                            out.write('{}{}\n'.format(' - FAILED', '</br>'))

                    for x in range(current_item_pos, current_item_pos + 2):
                        if (lines[x]).lstrip(' ').startswith('from'):
                            print('Source URL: ' + lines[x].lstrip(' ').rstrip("\n"))
                            source_url = lines[x].lstrip(' ').rstrip("\n")
                        if (lines[x]).lstrip(' ').startswith('<'):
                            print('Broken Link: ' + lines[x].lstrip(' ').rstrip("\n"))
                            broken_url = lines[x].lstrip(' ').rstrip("\n")
                            try:
                                Url_status.objects.get_or_create(
                                    site=url_list.url,
                                    source_url=source_url,
                                    broken_url=broken_url,)
                            except:
                                print("entry exists")
                            with open('scrapesites/templates/logs.html', 'a') as out:
                                out.write('{}{}{}\n'.format('<br>404 Source: ', source_url, '<br/>'))
                                out.write('{}{}{}\n'.format('<br>Broken link: ', broken_url, '</br>'))

            # Clear table if no more 404's found.
            if count_404 == 0:
                # import pdb; pdb.set_trace()

                Url_status.objects.filter(site=url_list.url).delete()
                Urllist.objects.filter(url=url_list.url).update(bad_link=False, slack_sent=False)
                # maybe send all clear slack.
                with open('scrapesites/templates/logs.html', 'a') as out:
                    out.write('{}{}\n'.format(' - GOOD', '</br>'))

        # Checks done close logs.
        with open('scrapesites/templates/logs.html', 'a') as out:
            out.write('{}\n{}\n{}\n{}\n'.format('--  All Sites Checked --', '</p>', '</body>', '</html>'))
        # Record time it took to run checks so that it can be displayed in
        # pingdoms response time.

        t1 = time.time()
        total_time = (t1 - t0) * 1000
        # Responsetime.objects.filter(id=1).update(response_time=total_time)
        defaults = {'response_time': total_time}
        Responsetime.objects.update_or_create(id=1, defaults=defaults)
        # import pdb; pdb.set_trace()
        # Ouput urls link status to pingdoms check XML,
        # this is what pingdom points to.
        if dead_link_found:
            load_broken_links_from_db(xml_out_1, xml_out_2, xml_out_5, total_time)
        else:
            with open('scrapesites/templates/check.xml', 'w') as out:
                xml_out_3 = "<status>OK</status>"
                xml_out_4 = "<response_time>%.2f</response_time>" % total_time
                out.write('{}\n{}\n{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, xml_out_3, xml_out_4, xml_out_5))

        # Send slack
        for urllist in Urllist.objects.filter(bad_link=True,slack_sent=False):
            # import pdb; pdb.set_trace()
            if send_message(urllist.team):
                Urllist.objects.filter(url=urllist.url).update(slack_sent=True)
            else:
                print("Could not send slack message")


def on_start_get_status():
    # Check if url check table is empty
    xml_out_1, xml_out_2, xml_out_5 = initialize_check_xml_format()
    # import pdb; pdb.set_trace()
    if not Url_status.objects.exists():
        if not Responsetime.objects.exists():
            xml_out_4 = "<response_time>0.00</response_time>"
        else:
            xml_out_4 = "<response_time>%.2f</response_time>" % Responsetime.objects.get(id=1).response_time
        with open('scrapesites/templates/check.xml', 'w') as out:
            xml_out_3 = "<status>OK</status>"
            out.write('{}\n{}\n{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, xml_out_3, xml_out_4, xml_out_5))
    else:
        response_time = Responsetime.objects.get(id=1).response_time
        load_broken_links_from_db(xml_out_1, xml_out_2, xml_out_5, response_time)


def load_broken_links_from_db(xml_out_1, xml_out_2, xml_out_5, response_time):
    with open('scrapesites/templates/check.xml', 'w') as out:
        out.write('{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, "<status>"))
        website_list = []
        count = 0
        for row in Url_status.objects.all().values():
            # import pdb; pdb.set_trace()

            website_list.append(row['site'])
            if count == 0:
                out.write('{}{}{}\n'.format('<b><u>Website: ', row['site'], '</u></b><br/>'))
            elif website_list[count - 1] != row['site']:
                out.write('{}{}{}{}\n'.format('</br>', '<b><u>Website: ', row['site'], '</u></b><br/>'))
            count += 1
            out.write('{}{}{}\n'.format('Source Page: <font color="#000099">', row['source_url'], '</font><br/>'))
            out.write('{}{}{}\n\n'.format('Bad Link: <font color="#990000">', row['broken_url'].replace('<', '&lt;').replace('>', '&gt;'), '</font><br/><br/>'))
            print(row)

        out.write('{}{}\n'.format('</status>','<br/>'))
        xml_out_4 = "<response_time>%.2f</response_time>" % response_time
        out.write('{}\n{}\n'.format(xml_out_4, xml_out_5))


def initialize_check_xml_format():
    xml_out_1 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    xml_out_2 = "<pingdom_http_custom_check>"
    xml_out_5 = "</pingdom_http_custom_check>"
    return xml_out_1, xml_out_2, xml_out_5
