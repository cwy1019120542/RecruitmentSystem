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
url(r'^applicant/(?P<phone_number>\w+)/post/(?P<post_id>)\d+/$',views.applicant_post_detail,name='applicant_post_detail'),
url(r'^company/(?P<phone_number>\w+)/$',views.company_index,name='company_index'),
url(r'^company/(?P<phone_number>\w+)/company_check/$',views.company_check,name='company_check'),
url(r'^company_check_ajax/$',views.company_check_ajax,name='company_check_ajax'),
url(r'^(?P<identity>\w+)/(?P<phone_number>\w+)/logout/$',views.logout,name='logout'),
url(r'^applicant/(?P<phone_number>\w+)/resume/$',views.applicant_resume_detail,name='applicant_resume_detail'),
url(r'^applicant_resume_ajax/$',views.applicant_resume_ajax,name='applicant_resume_ajax'),
url(r'^work_experience_ajax/$',views.work_experience_ajax,name='work_experience_ajax'),
url(r'^project_experience_ajax/$',views.project_experience_ajax,name='project_experience_ajax'),
url(r'^educate_experience_ajax/$',views.educate_experience_ajax,name='educate_experience_ajax'),
url(r'^skill_ajax/$',views.skill_ajax,name='skill_ajax'),
url(r'^(?P<identity>\w+)/(?P<phone_number>\d+)/passwd_change/$',views.passwd_change,name='passwd_change'),
url(r'^passwd_change_ajax/$',views.passwd_change_ajax,name='passwd_change_ajax'),
url(r'^company/(?P<phone_number>\w+)/post/$',views.company_post_list,name='company_post_list'),
url(r'^company/(?P<phone_number>\w+)/post/(?P<post_id>)/$',views.company_post_detail,name='company_post_detail'),
# url(r'^company_post_detail_ajax/$',views.company_post_detail_ajax,name='company_post_detail_ajax'),

]