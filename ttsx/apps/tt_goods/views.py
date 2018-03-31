from django.http import Http404
from django.shortcuts import render
from django_redis import get_redis_connection
from django.core.paginator import Page, Paginator
from .models import GoodsCategory, IndexGoodsBanner, IndexPromotionBanner, IndexCategoryGoodsBanner, GoodsSKU
from utils.page_list import get_page_list
from haystack.generic_views import SearchView


# from haystack.generic_views import SearchView
# Create your views here.
def fdfs_test(request):
    category = GoodsCategory.objects.get(pk=2)
    context = {'category': category}
    return render(request, 'fdfs_test.html', context)


def index(request):
    # 查询分类信息
    category_list = GoodsCategory.objects.all()
    # 查询轮播图片,通过ALL方法获取的是一个字典型的列表
    banner_list = IndexGoodsBanner.objects.all().order_by('index')
    # 查询广告
    adv_list = IndexPromotionBanner.objects.all().order_by('index')
    # 查询每个分类的推荐商品
    for category in category_list:
        # 查询推荐的标题商品
        category.title_list = IndexCategoryGoodsBanner.objects.filter(display_type=0, category=category).order_by(
            'index')[0:3]
        # 查询推荐的图片商品
        category.image_list = IndexCategoryGoodsBanner.objects.filter(display_type=1, category=category).order_by(
            'index')[0:4]
    context = {
        'title': '首页',
        'category_list': category_list,
        'banner_list': banner_list,
        'adv_list': adv_list
    }
    return render(request, 'index.html', context)
    # html = response.content.decode()
    # with open(,'w') as f:
    #     f.write(html)
    #


def detail(request, sku_id):
    try:
        sku = GoodsSKU.objects.get(pk=sku_id)
    except:
        raise Http404()
    category_list = GoodsCategory.objects.all()
    new_list = sku.category.goodssku_set.all().order_by('-id')[0:2]
    other_list = sku.goods.goodssku_set.all()
    # 验证用户是否登陆
    if request.user.is_authenticated():
        # 和redis建立连接
        redis_client = get_redis_connection()
        key = 'history%d' % request.user.id
        # 防止重复浏览的商品信息
        redis_client.lrem(key, 0, sku.id)
        # 将用户浏览商品信息写入REDIS
        redis_client.lpush(key, sku.id)
        if redis_client.llen(key) > 5:
            redis_client.lpop(key)

    context = {
        'title': '商品详情页',
        'sku': sku,
        'category_list': category_list,
        'new_list': new_list,
        'other_list': other_list
    }
    return render(request, 'detail.html', context)


def list_sku(request, category_id):
    try:
        category_now = GoodsCategory.objects.get(pk=category_id)
    except:
        raise Http404()
    # 获取键值对参数，get方法获取的是字符串
    order = int(request.GET.get('order', 1))
    if order == 1:
        order_by = '-id'
    elif order == 2:
        order_by = '-price'
    elif order == 3:
        order_by = 'price'
    elif order == 4:
        order_by = '-sales'
    else:
        order_by = '-id'
    sku_list = GoodsSKU.objects.filter(category_id=category_id).order_by(order_by)
    new_list = category_now.goodssku_set.all().order_by('-id')[0:2]
    category_list = GoodsCategory.objects.all()
    # 将列表进行分页，后一个参数为每页显示的数据
    paginator = Paginator(sku_list, 1)
    pindex = int(request.GET.get('pindex', 1))
    total_page = paginator.num_pages
    # 判断数据有效性
    if pindex < 1:
        pindex = 1
    if pindex > total_page:
        pindex = total_page
    page = paginator.page(pindex)
    context = {
        'title': '商品列表',
        'sku_list': sku_list,
        'category_now': category_now,
        'new_list': new_list,
        'page': page,
        'category_list': category_list,
        'order': order,
        # 页数的列表
        'page_list': get_page_list(total_page, pindex)
    }
    return render(request, 'list.html', context)


# 自定义上下文
class MySearchView(SearchView):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        category_list = GoodsCategory.objects.all()
        total_page = context['paginator'].num_pages
        pindex = context['page_obj'].number
        # do something
        context['title'] = '搜索结果'
        context['category_list'] = category_list
        context['page_list']=get_page_list(total_page,pindex)
        return context
