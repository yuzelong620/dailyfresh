from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
import re
from user.models import User
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from django.http import HttpResponse
from celery_tasks.tasks import send_register_active_email
from django.contrib.auth import authenticate, login
# Create your views here.

def register(request):
    '''显示注册页面'''
    return render(request, 'register.html')


def register_handle(request):
    '''注册处理'''
    #数据接收
    username = request.POST.get('user_name')
    password = request.POST.get('pwd')
    email = request.POST.get('email')
    allow = request.POST.get('allow')
    #数据校验
    if not all([username,password,email]):
        return render(request, 'register.html', {'errmsg':'数据不完整!'})
    #校验邮箱
    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        return render(request, 'register.html', {'errmsg': '邮箱格式错误!'})

    if allow != 'on':
        return render(request, 'register,html', {'errmsg': '请同意协议!'})
    #效验用户名是否存在
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None

    if user:
        return render(request, 'register.html', {'errmsg':'用户名已存在'})
    #业务处理  用户注册
    user = User.objects.create_user(username, email, password)
    user.is_active = 0
    user.save()
    #返回应答,跳转到首页
    return redirect(reverse('goods:index'))

class RegisterView(View):
    '''注册类视图'''
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        '''注册处理'''
        # 数据接收
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 数据校验
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整!'})
        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式错误!'})

        if allow != 'on':
            return render(request, 'register,html', {'errmsg': '请同意协议!'})
        # 效验用户名是否存在
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user:
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        # 业务处理  用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 1
        user.save()

        #发送激活右键,生成激活链接 http://127.0.0.1:8000/user/active/1
        #激活链接需要包含用户身份信息
        #加密用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm':user.id}
        token = serializer.dumps(info)
        token = token.decode()

        #用celery发邮件
        send_register_active_email.delay(email, username, token)
        # 返回应答,跳转到首页
        return redirect(reverse('goods:index'))

class ActiveView(View):
    '''用户激活'''
    def get(self, request, token):
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            user_id = info['confirm']
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            #
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            return HttpResponse('激活链接过期!')

#登录view
class LoginView(View):
    def get(self,request):
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'login.html', {'username':username, 'checked':checked})

    def post(self,request):
        '''登录校验'''
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        #效验完整型
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg':'数据不完整'})

        user = authenticate(username=username,password=password)
        if user is not None:
            if user.is_active:
                #记录登录状态
                login(request,user)
                #获取登录后要跳 转的地址
                next_url = request.GET.get('next', reverse('goods:index'))
                # 跳转首页
                response = redirect(next_url)
                #判断是否需要记住用户名
                remember =request.POST.get('remember')
                if remember == 'on':
                    #记住用户名
                    response.set_cookie('username',username,max_age=7*24*3600)
                else:
                    response.delete_cookie('username')

                return response
            else:
                return render(request, 'login.html',{'errmsg':'账户未激活!'})
        else:
            return render(request, 'login.html', {'errmsg':'用户名或密码错误!'})

class UserInfoView(View):
    '''用户中心页面跳转'''
    def get(self, request):
        return render(request, 'user_center_info.html', {'page':'user'})


class UserOrderView(View):
    '''用户订单页面跳转'''
    def get(self, request):
        return render(request, 'user_center_order.html', {'page':'order'})


class AddressView(View):
    '''用户中心地址页'''
    def get(self,request):
        return render(request, 'user_center_site.html',{'page':'address'})
