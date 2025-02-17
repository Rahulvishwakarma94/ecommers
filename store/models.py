from django.db import models
from category.models import SubCategory
from django.urls import reverse
# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200,unique=True)
    SubCategory = models.ForeignKey(SubCategory,on_delete=models.CASCADE)
    product_image = models.ImageField(upload_to='product_image/')
    product_price = models.IntegerField()
    product_stock = models.IntegerField()
    product_discription = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.product_name
    
    def get_url(self):
        return reverse('product_details',args=[self.category.slug,self.slug])
    


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category = 'color',is_active=True)

    def sizes(self):
        return super(VariationManager,self).filter(variation_category = 'size',is_active=True)


variation_category_choice = {
    "color":"color",
    "size":"size",
}

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100,choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value