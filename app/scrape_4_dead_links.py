import threading, subprocess, os, time
from subprocess import call

# def run_link_check():

# 	xml_out_1 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
# 	xml_out_2 = "<pingdom_http_custom_check>"
# 	#xml_out_4 = "<response_time>2.22</response_time>"
# 	xml_out_5 = "</pingdom_http_custom_check>"


# 	url_contents = [url_content.rstrip('\n') for url_content in open ('url_list')]

# 	dead_link_found = False
# 	t0 = time.time()

# 	for current_url in url_contents:
# 		FourOFour = 0
# 		print "%s" % current_url
# 		subprocess.call (["wget", "--spider", "-o", "dead_link.log", "-e", "robots=off", "-w", "1", "-r", "-p", current_url ])
# 		with open('dead_link.log') as inFile:
# 			for line in inFile:
# 				if '404' in line:
# 					FourOFour += 1
# 					dead_link_found = True

# 		print "Number of Dead Links: %d" %FourOFour

# 	t1 = time.time()
# 	total_time = (t1-t0)*1000

# 	if ( dead_link_found == True ):
# 		with open('app/templates/check.xml','w') as out:
# 			xml_out_3 = "<status>Dead Links Found</status>"
# 			xml_out_4 = "<response_time>%.2f</response_time>" % total_time
# 			out.write('{}\n{}\n{}\n{}\n'.format(xml_out_1,xml_out_2,xml_out_3,xml_out_4,xml_out_5))

# 	if ( dead_link_found == False ):
# 		with open('app/templates/check.xml','w') as out:
# 			xml_out_3 = "<status>ok</status>"
# 			xml_out_4 = "<response_time>%.2f</response_time>" % total_time
# 			out.write('{}\n{}\n{}\n{}\n{}\n'.format(xml_out_1,xml_out_2,xml_out_3,xml_out_4,xml_out_5))


class run_check(object):

	def __init__(self, interval=15):
		self.interval = interval

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

			for current_url in url_contents:
				FourOFour = 0
				print "%s" % current_url
				subprocess.call (["wget", "--spider", "-o", "dead_link.log", "-e", "robots=off", "-w", "1", "-r", "-p", current_url ])
				with open('dead_link.log') as inFile:
					for line in inFile:
						if '404' in line:
							FourOFour += 1
							dead_link_found = True

				print "Number of Dead Links: %d" %FourOFour

			t1 = time.time()
			total_time = (t1-t0)*1000

			if ( dead_link_found == True ):
				with open('app/templates/check.xml','w') as out:
					xml_out_3 = "<status>Dead Links Found</status>"
					xml_out_4 = "<response_time>%.2f</response_time>" % total_time
					out.write('{}\n{}\n{}\n{}\n'.format(xml_out_1,xml_out_2,xml_out_3,xml_out_4,xml_out_5))

			if ( dead_link_found == False ):
				with open('app/templates/check.xml','w') as out:
					xml_out_3 = "<status>ok</status>"
					xml_out_4 = "<response_time>%.2f</response_time>" % total_time
					out.write('{}\n{}\n{}\n{}\n{}\n'.format(xml_out_1,xml_out_2,xml_out_3,xml_out_4,xml_out_5))
			time.sleep(self.interval)

