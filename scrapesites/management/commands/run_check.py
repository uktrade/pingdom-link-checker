from django.core.management.base import BaseCommand, CommandError
from pylinkvalidator.api import crawl_with_options
from scrapesites.send_to_slack import send_message

import subprocess
import time


from scrapesites.models import Brokenlink, Urllist, Responsetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        xml_out_1, xml_out_2, xml_out_5 = initialize_check_xml_format()

        # If URL is no longer in check list, then delete failed links from table.
        on_start_clear_db()

        # Read previous status of links from table.
        # on_start_get_status()
        # import pdb; pdb.set_trace()

        print('Link check now running ...')

        dead_link_found = False
        t0 = time.time()

        # Create logs.html for storing link check results.
        # with open('scrapesites/templates/logs.html', 'w') as out:
        #     out.write('{}\n{}\n{}\n'.format('{% load staticfiles %}', '<html>', '<head>'))
        #     out.write('{}\n'.format('<link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">'))
        #     out.write('{}\n'.format('<link rel="stylesheet" href="{% static "css/scrapesites.css" %}">'))
        #     out.write('{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n'.format('<title>Link check - logs</title>', '</head>', '<body>', '<div class ="page-header">', '<h1>Link check - logs</h1>', '</div>', '<div class ="page-body">', '<p>'))

        # Loop through URL list and run link check.
        for current_url in Urllist.objects.filter(enable=True):
            print(current_url.site_url, " - Supported by: ", current_url.team)
            # import pdb; pdb.set_trace()
            count_404 = 0
            current_item_pos = 0

            with open('scrapesites/templates/logs.html', 'a') as out:
                out.write('{}{}{}{}'.format('<h2>', current_url.site_url, " - Supported by: ", current_url.team))
            # import pdb; pdb.set_trace()
            # output_results = crawl_with_options(["https://www.createdbypete.com"], {"show-source": True, "workers": "10"})
            # ignore_prefix = '--ignore=' + (os.environ.get('IGNORE_PREFIXES'))
            ignore_prefix = '--ignore=' + current_url.ignore_prefix
            scan_results = subprocess.run(['pylinkvalidate.py', \
                            '--depth=4', \
                            '--workers=10', \
                            '--show-source', \
                            '--console', \
                            #'--types=a', \
                            '--test-outside', \
                            '--parser=lxml', \
                            '--header=\'Connection: keep-alive\'', \
                            '--header=\'Pragma: no-cache\'', \
                            '--header=\'Cache-Control: no-cache\'', \
                            '--header=\'Upgrade-Insecure-Requests: 1\'', \
                            '--header=\'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8\'', \
                            '--header=\'DNT: 1\'', \
                            '--header=\'Accept-Encoding: gzip, deflate\'', \
                            '--header=\'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36\'', \
                            ignore_prefix, \
                            #'--ignore="https://www.createdbypete.com/articles/simple-way-to-find-broken-links-with-wget"', \
                            current_url.site_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            scan_result_list = scan_results.stdout.decode('utf-8').split('\n')

            # Check the scan results for broken links, 404s
            for item in scan_result_list:
                current_item_pos += 1
                # import pdb; pdb.set_trace()
                if item.lstrip(' ').startswith('not found (404)'):
                    #import pdb; pdb.set_trace()
                    count_404 += 1
                    dead_link_found = True
                    Urllist.objects.filter(site_url=current_url.site_url).update(broken_link_found=True)

                    # Record that a bad link is found, but this only needs to run once.
                    # if count_404 < 2:
                    #     with open('scrapesites/templates/logs.html', 'a') as out:
                    #         out.write('{}\n'.format(' - <span class="failed">FAILED</span></h2>'))

                    # Record all the source and broken links and write to table and log file if unique.
                    for x in range(current_item_pos, current_item_pos + 2):
                        if (scan_result_list[x]).lstrip(' ').startswith('from'):
                            print('Source URL: ' + scan_result_list[x].lstrip(' ').rstrip("\n"))
                            source_url = scan_result_list[x].lstrip(' ').rstrip("\n")
                        if (scan_result_list[x]).lstrip(' ').startswith('<'):
                            print('Broken Link: ' + scan_result_list[x].lstrip(' ').rstrip("\n"))
                            broken_link = scan_result_list[x].lstrip(' ').rstrip("\n")
                            try:
                                Brokenlink.objects.get_or_create(
                                    site_url=current_url.site_url,
                                    source_url=source_url,
                                    broken_link=broken_link,
                                    temp_url=urrent_url.site_url)
                            except:
                                print("entry exists")
                            # with open('scrapesites/templates/logs.html', 'a') as out:
                            #     out.write('{}{}{}\n'.format('<h3>404 Source: ', source_url, '</h3>'))
                            #     out.write('{}{}{}\n'.format('<h4>Broken link: ', broken_link.replace('<', '&lt;').replace('>', '&gt;'), '</h4>'))

            # Clear checked url from table if no 404's found.
            if count_404 == 0:
                # import pdb; pdb.set_trace()
                Brokenlink.objects.filter(site_url=current_url.site_url).delete()
                Urllist.objects.filter(site_url=current_url.site_url).update(broken_link_found=False, slack_sent=False)
                # maybe send all clear slack?
                # with open('scrapesites/templates/logs.html', 'a') as out:
                #     out.write('{}\n'.format(' - <span class="good">GOOD</span></h2>'))

        # Checks done close logs.
        # with open('scrapesites/templates/logs.html', 'a') as out:
        #     out.write('{}\n{}\n{}\n{}\n{}\n{}\n{}\n'.format('--  All Sites Checked --', '</div>', '</p>', '<div class ="page-footer">', '<h5><a href="/admin">WebOps ___ </a></h5>', '</body>', '</html>'))

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

            # Create an XML output for all the broken links found.
            # load_broken_links_from_db(xml_out_1, xml_out_2, xml_out_5, total_time)
        else:
            defaults = {'response_time': total_time, 'previous_check_state': True}
            Responsetime.objects.update_or_create(id=1, defaults=defaults)
            # with open('scrapesites/templates/check.xml', 'w') as out:
            #     xml_out_3 = "<status>OK</status>"
            #     xml_out_4 = "<response_time>%.2f</response_time>" % total_time
            #     out.write('{}\n{}\n{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, xml_out_3, xml_out_4, xml_out_5))

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


# def on_start_get_status():
#     # Check if url check table is empty
#     xml_out_1, xml_out_2, xml_out_5 = initialize_check_xml_format()
#     response_time = Responsetime.objects.get(id=1).response_time
#     # import pdb; pdb.set_trace()
#     if Responsetime.objects.get(id=1).previous_check_state or not Brokenlink.objects.exists():
#         xml_out_3 = "<status>OK</status>"
#         xml_out_4 = "<response_time>%.2f</response_time>" % response_time
#         with open('scrapesites/templates/check.xml', 'w') as out:
#             out.write('{}\n{}\n{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, xml_out_3, xml_out_4, xml_out_5))
#     else:
#         load_broken_links_from_db(xml_out_1, xml_out_2, xml_out_5, response_time)


# def load_broken_links_from_db(xml_out_1, xml_out_2, xml_out_5, response_time):
#     with open('scrapesites/templates/check.xml', 'w') as out:
#         out.write('{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, "<status>"))
#         website_list = []
#         count = 0
#         for current_row in Brokenlink.objects.all().values():
#             # import pdb; pdb.set_trace()
#
#             website_list.append(current_row['site_url'])
#             if count == 0:
#                 out.write('{}{}{}\n'.format('<b><u>Website: ', current_row['site_url'], '</u></b><br/>'))
#             elif website_list[count - 1] != current_row['site_url']:
#                 out.write('{}{}{}{}\n'.format('</br>', '<b><u>Website: ', current_row['site_url'], '</u></b><br/>'))
#             count += 1
#             out.write('{}{}{}\n'.format('Source Page: <font color="#000099">', current_row['source_url'], '</font><br/>'))
#             out.write('{}{}{}\n\n'.format('Bad Link: <font color="#990000">', current_row['broken_link'].replace('<', '&lt;').replace('>', '&gt;'), '</font><br/><br/>'))
#             # print(current_row)
#
#         out.write('{}{}\n'.format('</status>', '<br/>'))
#         xml_out_4 = "<response_time>%.2f</response_time>" % response_time
#         out.write('{}\n{}\n'.format(xml_out_4, xml_out_5))


def initialize_check_xml_format():
    xml_out_1 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    xml_out_2 = "<pingdom_http_custom_check>"
    xml_out_5 = "</pingdom_http_custom_check>"
    return xml_out_1, xml_out_2, xml_out_5
