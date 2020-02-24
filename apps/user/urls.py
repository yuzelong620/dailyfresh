from django.conf.urls import url
#from user import views
from django.contrib.auth.decorators import login_required
from user.views import RegisterView,ActiveView,LoginView,UserInfoView,UserOrderView,AddressView

urlpatterns = [
    #url(r'^register$', views.register, name='register'),    #注册跳转
    #url(r'^register_handle$', views.register_handle, name='register_handle')    #注册处理
    url(r'^register$', RegisterView.as_view(),name='register'),
    url(r'^register_handle$', RegisterView.as_view(), name='register_handle'),
    url(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),
    url(r'^login$', LoginView.as_view(), name='login'),

    url(r'^$', login_required(UserInfoView.as_view()), name='user'),
    url(r'^order$', login_required(UserOrderView.as_view()), name='order'),
    url(r'^address$', login_required(AddressView.as_view()), name='address')
]
