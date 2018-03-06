import threading
import subprocess
import os
import time
import json


class run_check(object):

    def __init__(self):
            # Create an initial OK XML so an alert is not raised on start-up.
            with open('app/templates/check.xml', 'w') as out:
                xml_out_1 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                xml_out_2 = "<pingdom_http_custom_check>"
                xml_out_3 = "<status>OK</status>"
                xml_out_4 = "<response_time>0.00</response_time>"
                xml_out_5 = "</pingdom_http_custom_check>"
                out.write('{}\n{}\n{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, xml_out_3, xml_out_4, xml_out_5))
            # Set how long to sleep before re-running check.
            self.interval = int(os.environ.get('CHECK_INTERVAL'))
            print('This check will run every ' + str(self.interval) + 's')
            thread = threading.Thread(target=self.run, args=())
            thread.daemon = True
            thread.start()

    def run(self):
        # Method that runs forever.
        # Open file that contains the URLs to check.
        with open('url_list.json') as json_file:
                all_urls = json.load(json_file)
        # Initialize a url list with all green OK status.
        my_list = {}
        for key in all_urls.items():
            for url_name in key[1]:
                my_list[url_name] = 'OK'
        while True:
            # Pingdom checks for XML in a set format.
            xml_out_1 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
            xml_out_2 = "<pingdom_http_custom_check>"
            xml_out_3 = ""
            xml_out_5 = "</pingdom_http_custom_check>"
            dead_link_found = False
            t0 = time.time()
            # Create logs.html for storing link check results.
            with open('app/templates/logs.html', 'w') as out:
                out.write('{}\n{}\n{}\n{}\n'.format('<html>', '<body>', '<h1>Link check - logs</h1>', '<p>'))
            # For all URLs check for 404 dead links.
            for current_url, status in my_list.items():
                count_404 = 0
                current_item_pos = 0
                print(current_url)
                # Update log file with url name.
                with open('app/templates/logs.html', 'a') as out:
                    out.write('{}'.format(current_url))
                # Use wgets spider to check all links -t (3s) time to wait if link doesnt respond,
                # remove check for robots.txt, -r recurse website & output results to a list.
                output_results = subprocess.run(['wget', '--spider', '-t', '3', '-e', 'robots=off', '-r', '-p', current_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                list_of_results = (output_results.stderr.decode('utf-8')).split('\n')
                dead_link = []
                for item in list_of_results:
                    # Check list for 404, this is found at end of string.
                    # If found store bad link in array which is 3 positions before the 404 is found.
                    current_item_pos += 1
                    if item.endswith('404 Not Found'):
                        count_404 += 1
                        print(list_of_results[current_item_pos - 3])
                        print(item)
                        dead_link.append(list_of_results[current_item_pos - 3])
                        # Store bad link in log file and record that a dead link was found.
                        with open('app/templates/logs.html', 'a') as out:
                            out.write('{}{}\n{}{}{}\n'.format(' - FAILED', '<br/>', '404 - ', list_of_results[current_item_pos - 3], '<br/>'))
                        dead_link_found = True
                # If a 404 is found and this is the first time this loop has run
                # then record the dead link.  This is so that this doesn't
                # get overwritten if this dead link was found during the previous run
                # and we keep a record of the time that the link was originally found.
                if count_404 > 0 and status == 'OK':
                    my_list[current_url] = dead_link
                if count_404 == 0:
                    my_list[current_url] = "OK"
                print('Number of Dead Links: ' + str(count_404))
                # If no 404s found then mark url as good.
                with open('app/templates/logs.html', 'a') as out:
                    if count_404 == 0:
                        out.write('{}{}\n'.format(' - GOOD', '<br/>'))
            # Checks done close logs.
            with open('app/templates/logs.html', 'a') as out:
                out.write('{}\n{}\n{}\n{}\n'.format('--  All Sites Checked --', '</p>', '</body>', '</html>'))
            # Record time it took to run checks so that it can be displayed in
            # pingdoms response time.
            t1 = time.time()
            total_time = (t1 - t0) * 1000
            # Ouput urls link status to pingdoms check XML,
            # this is what pingdom points to.
            if dead_link_found:
                with open('app/templates/check.xml', 'w') as out:
                    out.write('{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, "<status>"))
                    for key, value in my_list.items():
                        print(key)
                        print(value)
                        if value != 'OK':
                            out.write('{}\n{}{}{}\n'.format("The following URL has dead link:", "<", key[7:].replace('/', '-'), ">"))
                            for x in value:
                                out.write('{}\n'.format(x))
                            out.write('{}{}{}\n'.format("</", key[7:].replace('/', '-'), ">"))
                    out.write('{}\n'.format("</status>"))
                    xml_out_4 = "<response_time>%.2f</response_time>" % total_time
                    out.write('{}\n{}\n'.format(xml_out_4, xml_out_5))
            if not dead_link_found:
                with open('app/templates/check.xml', 'w') as out:
                    xml_out_3 = "<status>OK</status>"
                    xml_out_4 = "<response_time>%.2f</response_time>" % total_time
                    out.write('{}\n{}\n{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, xml_out_3, xml_out_4, xml_out_5))                                                                                                               # Sleep for duration of check interval.
            time.sleep(self.interval)
