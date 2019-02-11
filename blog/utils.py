import sys
import os
import urllib
import threading
from queue import Queue
import uuid

class DownloadThread(threading.Thread):
	def __init__(self, queue, destfolder):
		super(DownloadThread, self).__init__()
		self.queue = queue
		self.destfolder = 'blog/'+destfolder
		self.daemon = True
	
	def run(self):
		while True:
			url = self.queue.get()
			try:
				self.download_url(url[0],url[1])
			except Exception as ex:
				print("   Error in Downloading!!!")
				print(ex)
			self.queue.task_done()

	def download_url(self, url,static_name):
		# change it to a different way if you require
		if not os.path.exists(self.destfolder):
			os.makedirs(self.destfolder)
		dest = os.path.join(self.destfolder, static_name)
		urllib.request.urlretrieve(url, dest)


def download_image(urls, destfolder):
	queue = Queue()
	static_urls = []
	for url in urls:
		if url == '':
			static_urls.append(url)
		else:
			static_name = str(uuid.uuid1())
			suffix = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('wx_fmt',[''])[0]
			static_name = static_name+'.'+suffix
			queue.put([url,static_name])
			static_urls.append(destfolder+static_name)
	
	t = DownloadThread(queue, destfolder)
	t.start()	
	queue.join()
	return static_urls
