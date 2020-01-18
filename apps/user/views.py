from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
import re
from user.models import User
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from django.http import HttpResponse
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
        user.is_active = 0
        user.save()

        #发送激活右键,生成激活链接 http://127.0.0.1:8000/user/active/1
        #激活链接需要包含用户身份信息
        #加密用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm':user.id}
        token = serializer.dump(info)
        #给用户发验证邮件
        # 返回应答,跳转到首页
        return redirect(reverse('goods:index'))

class ActiveView(View):
    '''用户激活'''
    def get(self, request, token):
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.load(token)
            user_id = info['confirm']
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            #
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            return HttpResponse('激活链接过期!')


class LoginView(View):
    def get(self,request):
        return render(request, 'login.html')

