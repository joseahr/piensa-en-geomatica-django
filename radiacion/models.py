from django.db import models
from datetime import datetime
# Create your models here.

class Document(models.Model):
	docfile = models.FileField(upload_to='radiaciones')
	shp = models.TextField()
	nombre_original = models.TextField()
	fecha = models.DateTimeField(default=datetime.now, blank=True)