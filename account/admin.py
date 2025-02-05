from django.contrib import admin
from account.models import Account, UserProfile
# Register your models here.
class AccountAdmin(admin.ModelAdmin):
    list_display = ('email','username','first_name','last_name','phone_number')

admin.site.register(Account,AccountAdmin)
admin.site.register(UserProfile)