from django.core.management.base import BaseCommand, CommandError
from pylinkvalidator.api import crawl_with_options

import psycopg2
import subprocess
import os
import time
import json

from scrapesites.models import Urllist, Url_status

class Command(BaseCommand):
    def handle(self, *args, **options):
        connection = psycopg2.connect("dbname='url_results' user='checker' host='localhost' password='checker'")

        xml_out_1, xml_out_2, xml_out_5 = initialize_check_xml_format()
        on_start_get_status(connection)
        # import pdb; pdb.set_trace()
        # Open file that contains the URLs to check.
        # with open('url_list.json') as json_file:
        #        all_urls = json.load(json_file)

        # interval = int(os.environ.get('CHECK_INTERVAL'))

        print('I am running check')

        dead_link_found = False
        t0 = time.time()

        # Create logs.html for storing link check results.
        with open('scrapesites/templates/logs.html', 'w') as out:
            out.write('{}\n{}\n{}\n{}\n'.format('<html>', '<body>', '<h1>Link check - logs</h1>', '<p>'))

        # import pdb; pdb.set_trace()
        # For all URLs check for 404 dead links.

        # url = Url_status()
        # url.site = "www.whatevers.com"
        # ...
        # url.save()

        # obj, created = Url_status.objects.get_or_create(site=, x,y)

        # if created:
        # we have a new o bject

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
                    # import pdb; pdb.set_trace()
                    count_404 += 1
                    dead_link_found = True
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

                            # statement = "INSERT INTO url_status VALUES ('" + current_url + "', '" + source_url + "', '" + broken_url + "') ON CONFLICT (site, source_url, broken_url) DO NOTHING"
                            # mark = connection.cursor()
                            # mark.execute(statement)
                            # connection.commit()
                            # import pdb; pdb.set_trace()
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
                # statement = "DELETE FROM url_status WHERE site = '" + url_list.url + "'"
                # mark = connection.cursor()
                # mark.execute(statement)
                # connection.commit()

                with open('scrapesites/templates/logs.html', 'a') as out:
                    out.write('{}{}\n'.format(' - GOOD', '</br>'))

        # Checks done close logs.
        with open('scrapesites/templates/logs.html', 'a') as out:
            out.write('{}\n{}\n{}\n{}\n'.format('--  All Sites Checked --', '</p>', '</body>', '</html>'))
        # Record time it took to run checks so that it can be displayed in
        # pingdoms response time.

        t1 = time.time()
        total_time = (t1 - t0) * 1000
        # import pdb; pdb.set_trace()
        # Ouput urls link status to pingdoms check XML,
        # this is what pingdom points to.
        if dead_link_found:
            load_broken_links_from_db(connection, xml_out_1, xml_out_2, xml_out_5)
        else:
            with open('scrapesites/templates/check.xml', 'w') as out:
                xml_out_3 = "<status>OK</status>"
                xml_out_4 = "<response_time>%.2f</response_time>" % total_time
                out.write('{}\n{}\n{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, xml_out_3, xml_out_4, xml_out_5))


def on_start_get_status(connection):
    # Check if url check table is empty
    xml_out_1, xml_out_2, xml_out_5 = initialize_check_xml_format()
    # query = "SELECT CASE WHEN EXISTS (SELECT * FROM url_status LIMIT 1) THEN 1 ELSE 0 END"
    # check_empty = connection.cursor()
    # check_empty.execute(query)
    # import pdb; pdb.set_trace()
    # if check_empty.fetchone() == 0:
    if not Url_status.objects.exists():
        with open('scrapesites/templates/check.xml', 'w') as out:
            xml_out_3 = "<status>OK</status>"
            xml_out_4 = "<response_time>0.00</response_time>"
            out.write('{}\n{}\n{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, xml_out_3, xml_out_4, xml_out_5))
    else:
        load_broken_links_from_db(connection, xml_out_1, xml_out_2, xml_out_5)


def load_broken_links_from_db(connection, xml_out_1, xml_out_2, xml_out_5):
    with open('scrapesites/templates/check.xml', 'w') as out:
            out.write('{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, "<status>"))
            for row in Url_status.objects.all().values():
                # import pdb; pdb.set_trace()
                out.write('{}{}{}\n'.format('Website: ', row['site'], '<br/>'))
                out.write('{}{}{}'.format('Source Page: ', row['source_url'], '<br/>'))
                out.write('{}{}{}\n'.format('Bad Link: ', row['broken_url'].replace('<', '&lt;').replace('>', '&gt;'), '<br/>'))
                print(row)

            out.write('{}\n'.format("</status>"))
            xml_out_4 = "<response_time>0.0</response_time>"
            out.write('{}\n{}\n'.format(xml_out_4, xml_out_5))


def initialize_check_xml_format():
    xml_out_1 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    xml_out_2 = "<pingdom_http_custom_check>"
    xml_out_5 = "</pingdom_http_custom_check>"
    return xml_out_1, xml_out_2, xml_out_5
