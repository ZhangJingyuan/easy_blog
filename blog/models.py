from django.db import models

# Create your models here.
class Blog(models.Model):
	title = models.CharField(max_length=100, unique=True)
	origin_name = models.CharField(max_length=100,null=True)
	origin_account = models.CharField(max_length=100,null=True)
	origin_url = models.CharField(max_length=255,null=True)
	body = models.TextField(null = True)
	posted = models.DateField(db_index=True, auto_now_add=True)
	if_post = models.BooleanField(default=False)

	def __str__(self):
		return self.title
	
	def __unicode__(self):
		return '%s' % self.title