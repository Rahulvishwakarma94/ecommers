from django.db import models
from django.urls import reverse
# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=200,unique=True)
    slug = models.SlugField(max_length=200,unique=True)
    
    def __str__(self):
        return self.category_name
    
    def get_url(self):
        return reverse('SubCategory_by_category',args=[self.slug])

class SubCategory(models.Model):
    category = models.ForeignKey(Category,null=True,blank=True,on_delete=models.CASCADE)
    Sub_category_name = models.CharField(max_length=200,unique=True)
    slug = models.SlugField(max_length=200,unique=True)

    
    def __str__(self):
        return self.Sub_category_name   
    
    def get_url(self):
        return reverse('product_by_category',args=[self.slug])
