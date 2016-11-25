import threading, subprocess, os, time
from subprocess import call

class run_check(object):

	def __init__(self):

		self.interval = int(os.environ.get('CHECK_INTERVAL'))
		
		print "This check will run every %ds"  % self.interval
		
		thread = threading.Thread(target=self.run, args=())
		thread.daemon = True                            # Daemonize thread
		thread.start()                  

	def run(self):
		""" Method that runs forever """
		while True:
		
			#print('Doing something imporant in the background')

			xml_out_1 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
			xml_out_2 = "<pingdom_http_custom_check>"
			xml_out_5 = "</pingdom_http_custom_check>"


			url_contents = [url_content.rstrip('\n') for url_content in open ('url_list')]

			dead_link_found = False
			t0 = time.time()

			with open('app/templates/deadlinks.html','w') as out:
				out.write ('{}\n{}\n{}\n{}\n'.format('<html>','<body>','<h1>Link check - logs</h1>','<p>'))


			for current_url in url_contents:
				if not current_url.startswith("#"):
					
					FourOFour = 0
					print "%s" % current_url
					with open('app/templates/deadlinks.html','a') as out:
						out.write ('{}'.format(current_url))
					subprocess.call (["wget", "--spider", "-o", "dead_link.log", "-e", "robots=off", "-w", "1", "-r", "-p", current_url ])
					
					with open('dead_link.log') as inFile:
						for line in inFile:
							if '--20' in line:
								url_checked = line

							if '404' in line:
								FourOFour += 1
								print line
								print url_checked
								with open('app/templates/deadlinks.html','a') as out:
									out.write ('{}{}\n{}{}{}\n'.format(' - FAILED','<br/>','404 - ',url_checked,'<br/>'))

								dead_link_found = True

					print "Number of Dead Links: %d" %FourOFour
					with open('app/templates/deadlinks.html','a') as out:
						if (FourOFour == 0 ):
							out.write ('{}{}\n'.format(' - GOOD', '<br/>'))


			with open('app/templates/deadlinks.html','a') as out:
				out.write ('{}\n{}\n{}\n{}\n'.format('--  All Sites Checked --','</p>','</body>','</html>'))


			t1 = time.time()
			total_time = (t1-t0)*1000

			if ( dead_link_found == True ):
				with open('app/templates/check.xml','w') as out:
					xml_out_3 = "<status>Dead Links Found</status>"
					xml_out_4 = "<response_time>%.2f</response_time>" % total_time
					out.write('{}\n{}\n{}\n{}\n{}\n'.format(xml_out_1,xml_out_2,xml_out_3,xml_out_4,xml_out_5))

			if ( dead_link_found == False ):
				with open('app/templates/check.xml','w') as out:
					xml_out_3 = "<status>OK</status>"
					xml_out_4 = "<response_time>%.2f</response_time>" % total_time
					out.write('{}\n{}\n{}\n{}\n{}\n'.format(xml_out_1,xml_out_2,xml_out_3,xml_out_4,xml_out_5))
			time.sleep(self.interval)

