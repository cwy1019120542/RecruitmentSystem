from django.conf.urls import url,include
from . import views
app_name='SuperY'
urlpatterns=[
url(r'^login/$',views.login,name='login'),
url(r'^login_ajax/$',views.login_ajax,name='login_ajax'),
url(r'^register/$',views.register,name='register'),
url(r'^register_ajax/$',views.register_ajax,name='register_ajax'),
]