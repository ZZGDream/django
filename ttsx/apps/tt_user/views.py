import re
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.contrib.auth import authenticate, login, logout
from ttsx import settings
from .models import User, Address, AreaInfo
from django.http import HttpResponse
from django_redis import get_redis_connection
from tt_goods.models import GoodsSKU
from celery_tasks.tasks import send_user_active
from utils.views import LoginRequiredViewMixin


# Create your views here.
# def register(request):
#     return render(request, 'register.html')
class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html', {'title': '注册'})

    def post(self, request):
        uname = request.POST.get('user_name')
        pwd = request.POST.get('pwd')
        cpwd = request.POST.get('cpwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        context = {
            'uname': uname,
            'pwd': pwd,
            'cpwd': cpwd,
            'emali': email,
            'err_msg': '',
        }
        # 判断是否接受协议
        if allow is None:
            context['err_msg'] = '请接收协议'
            return render(request, 'register.html', context)

        if not all([uname, pwd, cpwd, email]):
            context['err_msg'] = '请填写完整信息'
            return render(request, 'register.html', context)

        if pwd != cpwd:
            context['err_msg'] = '前后密码不一致'
            return render(request, 'register.html', context)

        if User.objects.filter(username=uname).count() > 0:
            context['err_msg'] = '用户名已经存在'
            return render(request, 'register.html', context)

        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            context['err_msg'] = '邮箱格式不正确'
            return render(request, 'register.html', context)

        # if User.objects.filter(email=email).count() > 0:
        #     context['err_msg'] = '邮箱已经注册'
        #     return render(request, 'register.html', context)

        user = User.objects.create_user(uname, email, pwd)  # 生成一条用户记录
        user.is_active = False
        user.save()
        send_user_active.delay(user.id, email)

        # # 加密用户编号
        # serializer = Serializer(settings.SECRET_KEY, 60 * 60 * 24 * 7)
        # # 加密后为二进制类型应该进行解码成字符串
        # value = serializer.dumps({'id': user.id}).decode()
        # msg = "<a href='http://127.0.0.1:8000/user/active/%s'>点击激活</a>" % value
        # send_mail('天天生鲜-账户激活', '', settings.EMAIL_FROM, [email], html_message=msg)
        return HttpResponse('注册成功，请稍后激活')


def active(request, value):
    try:
        serializer = Serializer(settings.SECRET_KEY)
        dict = serializer.loads(value)
    except Exception as e:
        return HttpResponse('链接已经过期，请重新发送邮件')
    uid = dict.get('id')
    user = User.objects.get(pk=uid)
    user.is_active = True
    user.save()

    return redirect('/user/login')


def exists(request):
    uname = request.GET.get('uname')
    if uname is not None:
        result = User.objects.filter(username=uname).count()
    return JsonResponse({'result': result})


class LoginView(View):
    def get(self, request):
        uname = request.COOKIES.get('uname', '')
        context = {
            'title': '登录',
            'uname': uname
        }
        return render(request, 'login.html', context)

    def post(self, request):
        # 接收数据
        dict = request.POST
        uname = dict.get('username')
        upwd = dict.get('pwd')
        remember = dict.get('remember')

        # 构造返回结果
        context = {
            'uname': uname,
            'upwd': upwd,
            'err_msg': '',
            'title': '登录处理',
        }

        # 判断数据是否填写
        if not all([uname, upwd]):
            context['err_msg'] = '请填写完整信息'
            return render(request, 'login.html', context)

        # 判断用户名、密码是否正确
        user = authenticate(username=uname, password=upwd)

        if user is None:
            context['err_msg'] = '用户名或密码错误'
            return render(request, 'login.html', context)

        # 如果未激活也不允许登录
        if not user.is_active:
            context['err_msg'] = '请先到邮箱中激活'
            return render(request, 'login.html', context)

        # 状态保持
        login(request, user)

        response = redirect('/user/info')

        # 记住用户名
        if remember is None:
            response.delete_cookie('uname')
        else:
            response.set_cookie('uname', uname, expires=60 * 60 * 24 * 7)

        # 如果登录成功则转到用户中心页面
        return redirect('/user/info')


def logout_user(request):
    logout(request)
    return redirect('/user/login')


@login_required  # 检查用户是否登陆,封装了is_authenticated()方法
def info(request):
    # 查询用户是否有默认收货地址
    address = request.user.address_set.filter(isDefault=True)
    if address:
        address = address[0]
    else:
        address = None

    redis_client = get_redis_connection()
    gid_list = redis_client.lrange('history%d' % request.user.id, 0, -1)
    goods_list = []
    for gid in gid_list:
        goods_list.append(GoodsSKU.objects.get(pk=gid))
    context = {
        'title': '个人信息',
        'address': address,
        'goods_list': goods_list
    }
    return render(request, 'user_center_info.html', context)


@login_required
def order(request):
    context = {}
    return render(request, 'user_center_order.html', context)


class SiteView(LoginRequiredViewMixin, View):
    def get(self, request):
        addr_list = Address.objects.filter(user=request.user)
        context = {
            'title': "收货地址",
            'addr_list': addr_list,
        }
        return render(request, 'user_center_site.html', context)

    def post(self, request):
        dict = request.POST
        receiver = dict.get('receiver')
        provice = dict.get('provice')  # 选中的option的value值
        city = dict.get('city')
        district = dict.get('district')
        addr = dict.get('addr')
        code = dict.get('email')
        phone = dict.get('phone')
        default = dict.get('default')

        # 验证有效性
        if not all([receiver, provice, city, district, addr, code, phone]):
            return render(request, 'user_center_site.html', {'err_msg': '信息填写不完整'})
        address = Address()
        address.receiver = receiver
        address.province_id = provice
        address.city_id = city
        address.district_id =district
        address.addr = addr
        address.code = code
        address.phone_number = phone
        if default:
            address.isDefault = True
        address.user = request.user
        address.save()

        return redirect('/user/site')


def area(request):
    pid = request.GET.get('pid')
    if pid is None:
        slist = AreaInfo.objects.filter(aparent_id__isnull=True)
    else:
        slist = AreaInfo.objects.filter(aparent_id=pid)


    slist2 = []
    for s in slist:
        slist2.append({'id':s.id,'title':s.title})
    return JsonResponse({'slist2':slist2})