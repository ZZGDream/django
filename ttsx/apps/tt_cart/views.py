from django.shortcuts import render
from django.http import JsonResponse, Http404, HttpResponse
from tt_goods.models import GoodsSKU
import json
from django_redis import get_redis_connection


# Create your views here.
def add(request):
    # 判断请求方式
    if request.method != 'POST':
        return Http404()
    dict = request.POST
    sku_id = dict.get('sku_id')
    # 进行判断防止伪造请求
    if GoodsSKU.objects.filter(pk=sku_id).count() <= 0:
        return JsonResponse({'status': 2})
    count = int(dict.get('count', 0))
    if count <= 0:
        return JsonResponse({'status': 3})
    if count > 5:
        count = 5
    # 判断用户是否登陆
    if request.user.is_authenticated():
        redis_client = get_redis_connection()
        key = 'cart%d' % request.user.id
        if redis_client.hexists(key, sku_id):
            # 通过redis获取的数据为字符串类型
            count1 = int(redis_client.hget(key, sku_id))
            count2 = count + count1
            if count2 > 5:
                count2 = 5

            redis_client.hset(key, sku_id, count2)

        else:
            redis_client.hset(key, sku_id, count)
        total_count = 0
        for v in redis_client.hvals(key):
            total_count += int(v)
        response = JsonResponse({'status': 1, 'total_count': total_count})
    else:
        # cart_str为字符串类型
        cart_dict = {}
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_dict = json.loads(cart_str)
        # cart_dict = {sku_id:count}
        if sku_id in cart_dict:
            count1 = cart_dict[sku_id]
            count2 = count + count1
            if count2 > 5:
                count2 = 5
            cart_dict[sku_id] = count2
        else:
            cart_dict[sku_id] = count
        total_count = 0
        for k, v in cart_dict.items():
            total_count += v
        response = JsonResponse({'status': 1, 'total_count': total_count})
        # 将字典转换为字符串
        cart_str = json.dumps(cart_dict)
        # 不设置过期时间默认关闭浏览器自动过期
        response.set_cookie('cart', cart_str, expires=60 * 60)
        # 计算商品总数量

    return response


def index(request):
    # 判断用户是否登陆
    sku_list = []
    if request.user.is_authenticated():
        redis_client = get_redis_connection()
        key = 'cart%d' % request.user.id
        id_list = redis_client.hkeys(key)
        for id1 in id_list:
            sku = GoodsSKU.objects.get(pk=id1)
            sku.cart_count = int(redis_client.hget(key, id1))
            sku_list.append(sku)
    else:
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_dic = json.loads(cart_str)
            for k, v in cart_dic.items():
                # 根据商品编号获取商品对象
                sku = GoodsSKU.objects.get(pk=k)
                sku.cart_count = v
                sku_list.append(sku)

    context = {
        'title': '购物车',
        'sku_list': sku_list
    }
    return render(request, 'cart.html', context)


def edit(request):
    if request.method != 'POST':
        return Http404()
    dict = request.POST
    sku_id = dict.get('sku_id', 0)
    count = dict.get('count', 0)
    if GoodsSKU.objects.filter(pk=sku_id).count() <= 0:
        return JsonResponse({'status': 2})
    try:
        count = int(count)
    except:
        return JsonResponse({'status': 3})
    if count <= 0:
        count = 0
    elif count >= 5:
        count = 5
    response = JsonResponse({'ststus': 1})
    if request.user.is_authenticated():
        redis_client = get_redis_connection()
        redis_client.hset('cart%d' % request.user.id, sku_id, count)
    else:
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_dict = json.loads(cart_str)
            cart_dict[sku_id] = count
            cart_str = json.dumps(cart_dict)
            response.set_cookie('cart', cart_str, expires=60 * 60 * 24)

        pass

    return response


def delete(request):
    if request.method != 'POST':
        return Http404()

    dict = request.POST
    sku_id = dict.get('sku_id')
    response = JsonResponse({"status": 1})
    if request.user.is_authenticated():
        redis_client = get_redis_connection()
        redis_client.hdel('cart%d'%request.user.id,sku_id)

    else:
        cart_str = request.COOKIES.get('cart')
        cart_dict = json.loads(cart_str)
        cart_dict.pop(sku_id)
        #"cart_str"为字典型的字符串
        cart_str = json.dumps(cart_dict)
        response.set_cookie('cart', cart_str, expires=60 * 60 * 24)
    return response
