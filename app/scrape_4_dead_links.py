import threading, subprocess, os, time, json
from subprocess import call
from collections import namedtuple, defaultdict
import datetime
import commands

class run_check(object):

	def __init__(self):

			self.interval = int(os.environ.get('CHECK_INTERVAL'))

			print "This check will run every %ds"  % self.interval

			thread = threading.Thread(target=self.run, args=())
			thread.daemon = True                            # Daemonize thread
			thread.start()
		

	def run(self):
		""" Method that runs forever """
		check_log_url = "https://pingdom-link-checker.ukti.io/logs.html"

		with open('url_list.json') as json_file:
				all_urls = json.load(json_file)

		my_list = {}
		#import pdb; pdb.set_trace()
		for key in all_urls.iteritems():
			for url_found in key[1]:
				my_list[url_found] = 'OK'		

		while True:
			xml_out_1 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
			xml_out_2 = "<pingdom_http_custom_check>"
			xml_out_3 = ""
			xml_out_5 = "</pingdom_http_custom_check>"
			dead_link_found = 0
			t0 = time.time()

			print datetime.datetime.now()

			with open('app/templates/logs.html','w') as out:
				out.write ('{}\n{}\n{}\n{}\n'.format('<html>','<body>','<h1>Link check - logs</h1>','<p>'))

			for current_url, status in my_list.iteritems():

				FourOFour = 0
				count = 0
				print "%s" % current_url
				with open('app/templates/logs.html','a') as out:
					out.write ('{}'.format(current_url))
				o = commands.getoutput('wget --spider -t 3 -e robots=off -r -p ' + current_url)
				listfiles = o.split('\n')
				dead_link_array = []
				for item in listfiles:
					
					count = count + 1
					if item[-13:] == '404 Not Found':
						FourOFour = FourOFour + 1 
						print listfiles[count-3]
						print item
						dead_link_array.append(listfiles[count-3])
						with open('app/templates/logs.html','a') as out:
							out.write ('{}{}\n{}{}{}\n'.format(' - FAILED','<br/>','404 - ',listfiles[count-3],'<br/>'))
						dead_link_found = 1

				if ( (FourOFour > 0) and (status == 'OK')):
					my_list[current_url] = dead_link_array

				if (FourOFour == 0):
					my_list[current_url] = "OK"

				print datetime.datetime.now()
				print "Number of Dead Links: %d" %FourOFour
				with open('app/templates/logs.html','a') as out:
					if (FourOFour == 0 ):
						out.write ('{}{}\n'.format(' - GOOD', '<br/>'))

			with open('app/templates/logs.html','a') as out:
				out.write ('{}\n{}\n{}\n{}\n'.format('--  All Sites Checked --','</p>','</body>','</html>'))


			t1 = time.time()
			total_time = (t1-t0)*1000

			if ( dead_link_found == 1 ):
				with open('app/templates/check.xml','w') as out:
					out.write('{}\n{}\n{}\n'.format(xml_out_1,xml_out_2,"<status>"))
					
					for key, value in my_list.iteritems():
						print (key)
						print (value)

						if ( value != 'OK') :
							out.write('{}\n{}{}{}\n'.format("The following URL has dead link:","<",key[7:].replace('/','-'), ">"))
							for x in value:
								out.write('{}\n'.format(x))
							out.write('{}{}{}\n'.format("</",key[7:].replace('/','-'), ">"))

					out.write('{}\n'.format("</status>"))
					xml_out_4 = "<response_time>%.2f</response_time>" % total_time
					out.write('{}\n{}\n'.format(xml_out_4,xml_out_5))

			if ( dead_link_found == 0 ):
				with open('app/templates/check.xml','w') as out:
					xml_out_3 = "<status>OK</status>"
					xml_out_4 = "<response_time>%.2f</response_time>" % total_time
					out.write('{}\n{}\n{}\n{}\n{}\n'.format(xml_out_1,xml_out_2,xml_out_3,xml_out_4,xml_out_5))
			time.sleep(self.interval)

