from category.models import Category,SubCategory


def menu_link(request):
    link = Category.objects.all()
    return dict({'links':link})


def menu_link(request):
    link = SubCategory.objects.all()
    return dict({'links':link})