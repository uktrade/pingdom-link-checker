# pingdom-link-checker

About:
This is a python script that will recursively check all link on a website and reports a failure in an XML file for Pingdom to read.  A list of websites to check are in a file that can be updated as required.  This app uses the django framework to display the results as an xml file and will also log the site status on a page.

How to use:
Run with
		python manage.py runserver

This is deployed onto UK Gov PaaS.

Site list:
A list of URLs are stored in a PostgresDB Table, you can access the table from the Django admin.
You can diable any url you wish to temporarily remove.

Script output:
		<?xml version="1.0" encoding="UTF-8"?>
		<pingdom_http_custom_check>
		<status>OK</status>
		<response_time>3959.50</response_time>
		</pingdom_http_custom_check>

If Pingdom recives a status of OK the it will report site is up.  Anything else will mean site down.  The script will update status to the location of the log file to investigate which site has a problem.

Logs:
Browsing to /logs.html will show you the the status of each individual site, this can be used to determine which site failed and what link is failing. eg.
		https://pingdom-link-checker.london.cloudapps.digital/logs.html

Geckoboard Pull request endpoints:
All Sites
https://pingdom-link-checker.london.cloudapps.digital/gecko/

TeamSpecific(provided team exists in site DB)
https://pingdom-link-checker.london.cloudapps.digital/gecko?team=directory
