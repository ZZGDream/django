from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tt_goods.models import GoodsSKU
from django_redis import get_redis_connection


# Create your views here.
@login_required()
def index(request):
    # 接受商品编号
    dict = request.GET
    sku_ids = dict.getlist('sku_id')
    # 查收货地址
    addr_list = request.user.address_set.all()
    # 查询商品信息
    sku_list = []
    redis_client = get_redis_connection()
    key = 'cart%d' % request.user.id
    for sku_id in sku_ids:
        sku = GoodsSKU.objects.get(pk=sku_id)
        # 通过redis获取的值为二进制类型
        sku.cart_count = int(redis_client.hget(key, sku_id))
        sku_list.append(sku)
    context = {
        'title': '我的订单',
        'addr_list': addr_list,
        'sku_list': sku_list
    }
    return render(request, 'place_order.html', context)


@login_required()
def handle(request):
    # if request.method != 'POST':
    #     return Http404()
    # dict = request.POST
    # addr_id = dict.get('addr_id')
    # pay_sytle = dict.get('pay_style')
    # sku_ids = dict.get('sku_ids')
    # # 验证数据的有效性
    # if not all([addr_id, pay_sytle, sku_ids]):
    #     return JsonResponse({'status': 2})

    return JsonResponse({'status': 1})
