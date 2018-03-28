from django.shortcuts import render
from .models import GoodsCategory


# Create your views here.
def fdfs_test(request):
    category = GoodsCategory.objects.get(pk=2)
    context = {'category': category}
    return render(request, 'fdfs_test.html', context)
