from django.db import models
from account.models import Account
from store.models import Product, Variation
# Create your models here.


class Cart(models.Model):
    cart_id = models.CharField(max_length=255, null=True,blank=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE,blank=True,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,blank=True,null=True)
    quantity = models.IntegerField()
    variations = models.ManyToManyField(Variation,blank=True)

    def sub_total(self):
        return self.product.product_price * self.quantity

    def __str__(self):
        return self.product.product_name