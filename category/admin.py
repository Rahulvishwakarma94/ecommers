from django.contrib import admin
from category.models import  Category,SubCategory
# Register your models here.

class AdminCategory(admin.ModelAdmin):
    list_display = ['category_name']
    prepopulated_fields = {'slug':('category_name',)}


class AdminSubCategory(admin.ModelAdmin):
    list_display = ['Sub_category_name']
    prepopulated_fields = {'slug':('Sub_category_name',)}

admin.site.register(Category,AdminCategory)
admin.site.register(SubCategory,AdminSubCategory)    