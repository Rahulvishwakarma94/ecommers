from django.shortcuts import render
from store.models import Product

def index(request):

    pro = Product.objects.all()

    context = {
        'product':pro,
    }
    return render(request,'index.html',context)