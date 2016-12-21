import threading, subprocess, os, time, json
from subprocess import call
from collections import namedtuple, defaultdict

class run_check(object):

	def __init__(self):

			self.interval = int(os.environ.get('CHECK_INTERVAL'))

			print "This check will run every %ds"  % self.interval
			self.create_url_status()

			thread = threading.Thread(target=self.run, args=())
			thread.daemon = True                            # Daemonize thread
			thread.start()

	def create_url_status(self):
		#copy url list to json format list

		first = True
		with open('url_status.json','w') as out:
			out.write ('{}'.format("{"))
			url_contents = [url_content.rstrip('\n') for url_content in open ('url_list')]
			for current_url in url_contents:
				if not current_url.startswith("#"):
					if first:
						#out.write ('{}{}{}'.format("\"", current_url, "\":[\"OK\",\"0\"]"))
						out.write ('{}{}{}'.format("\"", current_url, "\":\"OK\""))
						first = False
					else:
						#out.write ('{}{}{}'.format(",\"", current_url, "\":[\"OK\",\"0\"]"))
						out.write ('{}{}{}'.format(",\"", current_url, "\":\"OK\""))
			out.write ('{}'.format("}"))
		#Create a blank OK XML
		with open('app/templates/check.xml','w') as out:
			out.write('{}\n'.format("<?xml version=\"1.0\" encoding=\"UTF-8\"?><pingdom_http_custom_check><status>OK</status><response_time>0</response_time></pingdom_http_custom_check>"))


	def run(self):
		""" Method that runs forever """
		check_log_url = "https://pingdom-link-checker.ukti.io/logs.html"



		while True:

			#print('Doing something imporant in the background')
			xml_list = defaultdict(list)

			with open('url_status.json') as json_file:
				d = json.load(json_file)
				# for key, value in d.iteritems():
			 # 		print key, value

			xml_out_1 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
			xml_out_2 = "<pingdom_http_custom_check>"
			xml_out_3 = ""
			xml_out_5 = "</pingdom_http_custom_check>"


			#url_contents = [url_content.rstrip('\n') for url_content in open ('url_list')]

			dead_link_found = 0
			t0 = time.time()

			with open('app/templates/logs.html','w') as out:
				out.write ('{}\n{}\n{}\n{}\n'.format('<html>','<body>','<h1>Link check - logs</h1>','<p>'))

			for current_url, status in d.iteritems():

				FourOFour = 0
				print "%s" % current_url
				with open('app/templates/logs.html','a') as out:
					out.write ('{}'.format(current_url))
				subprocess.call (["wget", "--spider", "-o", "dead_link.log", "-e", "robots=off", "-w", "1", "-r", "-p", current_url ])

				with open('dead_link.log') as inFile:
					dead_link_array = []
					for line in inFile:
						if '--20' in line:
							url_checked = line

						if "404 Not Found" in line:
							FourOFour = 1
							print line
							dead_link_array.append(url_checked)

							with open('app/templates/logs.html','a') as out:
								out.write ('{}{}\n{}{}{}\n'.format(' - FAILED','<br/>','404 - ',url_checked,'<br/>'))

							dead_link_found = 1


				if ( (FourOFour == 1) and (status == 'OK')):
					d[current_url] = dead_link_array

				if (FourOFour == 0):
					d[current_url] = "OK"


				print "Number of Dead Links: %d" %FourOFour
				with open('app/templates/logs.html','a') as out:
					if (FourOFour == 0 ):
						out.write ('{}{}\n'.format(' - GOOD', '<br/>'))
						#with open('url_status','r') as status:

			with open('url_status.json', 'w') as json_file:
				json.dump(d, json_file)

			#print "json file dumped"
			#print d
			with open('app/templates/logs.html','a') as out:
				out.write ('{}\n{}\n{}\n{}\n'.format('--  All Sites Checked --','</p>','</body>','</html>'))


			t1 = time.time()
			total_time = (t1-t0)*1000


			#print "dead link found = ", dead_link_found
			if ( dead_link_found == 1 ):
				with open('app/templates/check.xml','w') as out:
					out.write('{}\n{}\n{}\n'.format(xml_out_1,xml_out_2,"<status>"))
					with open('url_status.json') as json_file:
						d = json.load(json_file)
						#for key, value in xml_list.items():
						for key, value in d.iteritems():
							print (key)
							print (value)

							if ( value != 'OK') :
								out.write('{}\n{}{}{}\n'.format("The following URL has dead link:","<",key[7:],">"))
								for x in value:
									out.write('{}\n'.format(x))
								out.write('{}{}{}\n'.format("</",key[7:],">"))


					out.write('{}\n'.format("</status>"))
					xml_out_4 = "<response_time>%.2f</response_time>" % total_time
					out.write('{}\n{}\n'.format(xml_out_4,xml_out_5))

			if ( dead_link_found == 0 ):
				with open('app/templates/check.xml','w') as out:
					xml_out_3 = "<status>OK</status>"
					xml_out_4 = "<response_time>%.2f</response_time>" % total_time
					out.write('{}\n{}\n{}\n{}\n{}\n'.format(xml_out_1,xml_out_2,xml_out_3,xml_out_4,xml_out_5))
			time.sleep(self.interval)

