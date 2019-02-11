from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Blog
import urllib
from . import utils
import re

from bs4 import BeautifulSoup,Comment,Tag
# Create your views here.

def index_view(request):
	return render(request,'blog/index.html')
	
	
def webpage_handler(request):
	weblink = request.POST['wechat_weblink']
	webcontent = urllib.request.urlopen(weblink).read()
	html_content = webcontent.decode('utf8')
	
	soup = BeautifulSoup(html_content,'html.parser')
	title = soup.find(id='activity-name').string.strip()
	origin_name = soup.find(id='js_author_name').string.strip()
	origin_account = soup.find(id='js_name').string.strip()
	body =soup.find(id='js_content')
	
	b = Blog(title=title,origin_name=origin_name,origin_account=origin_account,origin_url=weblink)
	b.save()
	
	# download images and background url in css
	imgs = body.find_all('img')
	if imgs:
		remote_url = [img.attrs.get('data-src','') for img in imgs]
		local_url = utils.download_image(remote_url,'/media/blog/'+str(b.id)+'/')
		for i in range(0,len(local_url)):
			if local_url[i] != '':
				imgs[i].attrs['src'] = local_url[i]

	backgrounds = body.find_all(style=re.compile('.+background.+url\("([^)]+)"\).+'))
	if backgrounds:
		remote_background_url = []
		for background in backgrounds:
			remote_background_url+=re.findall('background.+url\("([^)]+)"\)',background.attrs['style'])
		local_background_url = utils.download_image(remote_background_url,'/media/blog/'+str(b.id)+'/')
		for i in range(0,len(local_background_url)):
			backgrounds[i].attrs['style'] = re.sub('url\("([^)]+)"\)','url("'+local_background_url[i]+'")',backgrounds[i].attrs['style'])
	
	# add id for each part		
	i = 0
	for child in body.contents:
		if isinstance(child,Tag):
			child.attrs['id'] = 'p'+str(i)
		i+=1
		

	b.body=str(body.prettify())
	b.save()
	
	return redirect('blog_edit',pk=b.id)
	
	
def content_handler(request,blog_id):
	
	blog = Blog.objects.get(pk=blog_id)
	index_list = request.POST.getlist('para_list')
	soup = BeautifulSoup(blog.body,'html.parser')
	content_list =soup.find(id='js_content')
	print(index_list)
	for tag_id in index_list:
		content_list.find(id=tag_id).extract()

	blog.body = str(soup)
	blog.if_post = True
	blog.save()
	
	return redirect('blog_detail',pk=blog.id)
		


class ListView(generic.ListView):
	template_name = 'blog/blog_list.html'
	context_object_name = 'blog_list'
	
	def get_queryset(self):
		return Blog.objects.all()
		
		
		
class DetailView(generic.DetailView):
	model = Blog
	template_name = 'blog/blog_detail.html'
	
class EditView(generic.DetailView):
	model = Blog
	template_name = 'blog/blog_edit.html'
	
	