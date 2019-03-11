from django.conf.urls import url,include
from . import views
app_name='SuperY'
urlpatterns=[
url(r'^login/$',views.login,name='login'),
url(r'^login_ajax/$',views.login_ajax,name='login_ajax'),
url(r'^register/$',views.register,name='register'),
url(r'^register_ajax/$',views.register_ajax,name='register_ajax'),
url(r'^applicant/(?P<phone_number>\w+)/$',views.applicant_index,name='applicant_index'),
url(r'^applicant_search_ajax/$',views.applicant_search_ajax,name='applicant_search_ajax'),
url(r'^applicant/(?P<phone_number>\w+)/(?P<search_word>\w+)/(?P<page>\d+)/$',views.applicant_search,name='applicant_search'),
url(r'^applicant/(?P<phone_number>\w+)/(?P<post_id>)\d+/$',views.post_detail,name='post_detail'),
url(r'^company/(?P<phone_number>\w+)/$',views.company_index,name='company_index'),
url(r'^company/(?P<phone_number>\w+)/company_check/$',views.company_check,name='company_check'),
url(r'^company_check_ajax/$',views.company_check_ajax,name='company_check_ajax'),
url(r'^(?P<identity>\w+)/(?P<phone_number>\w+)/logout/$',views.logout,name='logout'),
]