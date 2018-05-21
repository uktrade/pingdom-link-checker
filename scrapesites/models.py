from django.db import models
from pylinkvalidator.api import crawl_with_options

import psycopg2
import threading
import subprocess
import os
import time
import json

# Create your models here.
class run_check(models.Model):

    xml_out_1 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    xml_out_2 = "<pingdom_http_custom_check>"
    xml_out_3 = ""
    xml_out_5 = "</pingdom_http_custom_check>"
    connection = psycopg2.connect("dbname='url_results' user='checker' host='localhost' password='checker'")
    # Method that runs forever.
    # Check if url check table has any errors
    query = "SELECT CASE WHEN EXISTS (SELECT * FROM url_status LIMIT 1) THEN 1 ELSE 0 END"
    check_empty = connection.cursor()
    check_empty.execute(query)
    #import pdb; pdb.set_trace()
    if check_empty.fetchone() == 0:
        with open('scrapesites/templates/check.xml', 'w') as out:
            xml_out_1 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
            xml_out_2 = "<pingdom_http_custom_check>"
            xml_out_3 = "<status>OK</status>"
            xml_out_4 = "<response_time>0.00</response_time>"
            xml_out_5 = "</pingdom_http_custom_check>"
            out.write('{}\n{}\n{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, xml_out_3, xml_out_4, xml_out_5))
    else:
        with open('scrapesites/templates/check.xml', 'w') as out:
            out.write('{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, "<status>"))
            result = "TABLE url_status"
            mark = connection.cursor()
            mark.execute(result)
            #import pdb; pdb.set_trace()
            while True:
                row = mark.fetchone()
                if row == None:
                    break
                out.write('{}{}{}\n'.format(row[0], row[1], row[2].replace('<', '-').replace('>', '-')))
                print("site: " + row[0] + "\t\tSource url: " + row[1] + "\t\tBroken url: " + row[2])
            out.write('{}\n'.format("</status>"))
            xml_out_4 = "<response_time>0.0</response_time>"
            out.write('{}\n{}\n'.format(xml_out_4, xml_out_5))
    # Open file that contains the URLs to check.
    with open('url_list.json') as json_file:
            all_urls = json.load(json_file)
    # Initialize a url list with all green OK status.
    my_list = {}
    for key in all_urls.items():
        for url_name in key[1]:
            my_list[url_name] = 'OK'
    interval = int(os.environ.get('CHECK_INTERVAL'))

    while True:
        print ('I am running check')
        # Pingdom checks for XML in a set format.

        xml_out_1 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        xml_out_2 = "<pingdom_http_custom_check>"
        xml_out_3 = ""
        xml_out_5 = "</pingdom_http_custom_check>"
        dead_link_found = False
        t0 = time.time()

        # Create logs.html for storing link check results.
        with open('scrapesites/templates/logs.html', 'w') as out:
            out.write('{}\n{}\n{}\n{}\n'.format('<html>', '<body>', '<h1>Link check - logs</h1>', '<p>'))

        # import pdb; pdb.set_trace()
        # For all URLs check for 404 dead links.
        for current_url, status in my_list.items():
            count_404 = 0
            current_item_pos = 0
            print(current_url)
            # Update log file with url name.

            with open('scrapesites/templates/logs.html', 'a') as out:
                out.write('{}{}'.format('<br>', current_url))

            #output_results = subprocess.run(['wget', '--spider', '-t', '3', '-e', 'robots=off', '-r', '-p', current_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #output_results = crawl_with_options(["https://www.createdbypete.com"], {"show-source": True, "output": "/Users/jay/Documents/Work/DIT/Work/WebOps/pingdom-link-checker/"})
            output_results = subprocess.run(['pylinkvalidate.py', '--depth=4', '--show-source', '--output=url.out', current_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            f = open('url.out', 'r')
            lines = f.readlines()
            f.close()
            #print (lines)
            for item in lines:
                current_item_pos += 1
                #import pdb; pdb.set_trace()
                if item.lstrip(' ').startswith('not found (404)'):
                    #import pdb; pdb.set_trace()
                    count_404 += 1
                    dead_link_found = True
                    if count_404 < 2:
                        with open('scrapesites/templates/logs.html', 'a') as out:
                            out.write('{}{}\n'.format(' - FAILED','</br>'))

                    for x in range (current_item_pos,current_item_pos+2):
                        if (lines[x]).lstrip(' ').startswith ('from'):
                            print('Source URL: ' + lines[x].lstrip(' ').rstrip("\n"))
                            source_url = lines[x].lstrip(' ').rstrip("\n")
                        if (lines[x]).lstrip(' ').startswith ('<'):
                            print('Broken Link: ' + lines[x].lstrip(' ').rstrip("\n"))
                            broken_url = lines[x].lstrip(' ').rstrip("\n")
                            statement = "INSERT INTO url_status VALUES ('" + current_url + "', '" + source_url + "', '" + broken_url + "') ON CONFLICT (site, source_url, broken_url) DO NOTHING"
                            mark = connection.cursor()
                            mark.execute(statement)
                            connection.commit()
                            with open('scrapesites/templates/logs.html', 'a') as out:
                                out.write('{}{}{}\n'.format('<br>404 Source: ', source_url, '<br/>'))
                                out.write('{}{}{}\n'.format('<br>Broken link: ', broken_url, '</br>'))

            #Clear table if no more 404's found.
            if count_404 == 0:
                #import pdb; pdb.set_trace()
                statement = "DELETE FROM url_status WHERE site = '" + current_url + "'"
                mark = connection.cursor()
                mark.execute(statement)
                connection.commit()
                with open('scrapesites/templates/logs.html', 'a') as out:
                    out.write('{}{}\n'.format(' - GOOD', '</br>'))

            #list_of_results = (output_results.stderr.decode('utf-8')).split('\n')

        # Checks done close logs.
        with open('scrapesites/templates/logs.html', 'a') as out:
            out.write('{}\n{}\n{}\n{}\n'.format('--  All Sites Checked --', '</p>', '</body>', '</html>'))
        # Record time it took to run checks so that it can be displayed in
        # pingdoms response time.

        t1 = time.time()
        total_time = (t1 - t0) * 1000
        #import pdb; pdb.set_trace()
        # Ouput urls link status to pingdoms check XML,
        # this is what pingdom points to.
        if dead_link_found:
            with open('scrapesites/templates/check.xml', 'w') as out:
                out.write('{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, "<status>"))
                result = "TABLE url_status"
                mark = connection.cursor()
                mark.execute(result)
                #import pdb; pdb.set_trace()
                while True:
                    row = mark.fetchone()

                    if row == None:
                        break
                    out.write('{}{}{}\n'.format(row[0], row[1], row[2].replace('<', '-').replace('>', '-')))
                    print("site: " + row[0] + "\t\tSource url: " + row[1] + "\t\tBroken url: " + row[2])
                #out.write('{}{}{}\n'.format("</", key[8:].replace('/', '_'), ">"))
                out.write('{}\n'.format("</status>"))
                xml_out_4 = "<response_time>%.2f</response_time>" % total_time
                out.write('{}\n{}\n'.format(xml_out_4, xml_out_5))
        if not dead_link_found:
            with open('scrapesites/templates/check.xml', 'w') as out:
                xml_out_3 = "<status>OK</status>"
                xml_out_4 = "<response_time>%.2f</response_time>" % total_time
                out.write('{}\n{}\n{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, xml_out_3, xml_out_4, xml_out_5))                                                                                                               # Sleep for duration of check interval.

        time.sleep(interval)


def publish(self):
        # Create an initial OK XML so an alert is not raised on start-up.
        print('This check will run every ')
        self.save()
