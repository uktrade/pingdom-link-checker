# pingdom-link-checker

About:
This is a python script that will recursively check all link on a website and reports a failure in an XML file for Pingdom to read.  A list of websites to check are in a file that can be updated as required.  This app uses the flask framework to display the results as an xml file and will also log the site status on a page.

How to use:
Run with
		python run.py

This is deployed onto Heroku with the following parameters:
		web: python run.py
In Heroku you must configure a variable for how often you wish to run the script (in seconds). The recommended value is - CHECK_INTERVAL = 300

Site list:
A list of URLs are in the file "url_list"
You can hash/comment out any url you wish to temporarily remove.

Script output:
		<?xml version="1.0" encoding="UTF-8"?>
		<pingdom_http_custom_check>
		<status>OK</status>
		<response_time>3959.50</response_time>
		</pingdom_http_custom_check>

If Pingodm recives a status of OK the it will report site is up.  Anything else will mean site down.  The script will update status to the location of the log file to investigate which site has a problem.

Logs:
Browsing to /logs.html will show you the the status of each individual site, this can be used to determine which site failed and what link is failing. eg. 
		https://pingdom-link-checker.ukti.io/logs.html

To Do -
Refresh:
The script is scheduled to run at a set interval, however you can manually refresh the app.  this can be useful if you had an alert for a failure and what to check the status immediately.  This is done by adding a /refresh to the end of the url. eg. 
		https://pingdom-link-checker.ukti.io/refresh
