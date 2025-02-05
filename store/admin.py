from django.contrib import admin
from store.models import Product,Variation

# Register your models here.

class AdminProduct(admin.ModelAdmin):
    list_display = ['product_name']
    prepopulated_fields = {'slug':('product_name',)}

class AdminVariation(admin.ModelAdmin):
    list_display = ('product','variation_category','variation_value','is_active')
    list_editable = ['is_active']

admin.site.register(Variation,AdminVariation)
admin.site.register(Product,AdminProduct)