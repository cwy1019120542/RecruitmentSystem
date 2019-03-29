from django.conf.urls import url,include
from . import views
app_name='SuperY'
urlpatterns=[
url(r'^login/$',views.login,name='login'),
url(r'^login_ajax/$',views.login_ajax,name='login_ajax'),
url(r'^register/$',views.register,name='register'),
url(r'^register_ajax/$',views.register_ajax,name='register_ajax'),
url(r'^deliver_post_ajax/$',views.deliver_post_ajax,name='deliver_post_ajax'),
url(r'^applicant_search_ajax/$',views.applicant_search_ajax,name='applicant_search_ajax'),
url(r'^applicant_resume_ajax/$',views.applicant_resume_ajax,name='applicant_resume_ajax'),
url(r'^work_experience_ajax/$',views.work_experience_ajax,name='work_experience_ajax'),
url(r'^project_experience_ajax/$',views.project_experience_ajax,name='project_experience_ajax'),
url(r'^educate_experience_ajax/$',views.educate_experience_ajax,name='educate_experience_ajax'),
url(r'^company_check_ajax/$',views.company_check_ajax,name='company_check_ajax'),
url(r'^skill_ajax/$',views.skill_ajax,name='skill_ajax'),
url(r'^passwd_change_ajax/$',views.passwd_change_ajax,name='passwd_change_ajax'),
url(r'^applicant_(?P<user_id>\d+)/$',views.applicant_index,name='applicant_index'),
url(r'^applicant_(?P<user_id>\w+)/post_(?P<post_id>\w+)/$',views.applicant_post_detail,name='applicant_post_detail'),
url(r'^applicant_(?P<user_id>\w+)/company_look/page_(?P<page>\d+)/$',views.applicant_company_look,name='applicant_company_look'),
url(r'^applicant_(?P<user_id>\w+)/search_(?P<search_word>\w+)/page_(?P<page>\d+)/$',views.applicant_search_post,name='applicant_search_post'),
url(r'^applicant_(?P<user_id>\w+)/company_(?P<company_id>\w+)/page_(?P<page>\d+)/$',views.applicant_company_post,name='applicant_company_post'),
url(r'^company_(?P<user_id>\w+)/$',views.company_index,name='company_index'),
url(r'^company_(?P<user_id>\w+)/company_check/$',views.company_check,name='company_check'),
url(r'^applicant_(?P<user_id>\w+)/logout/$',views.applicant_logout,name='applicant_logout'),
url(r'^company_(?P<user_id>\w+)/logout/$',views.company_logout,name='company_logout'),
url(r'^applicant_(?P<user_id>\w+)/resume/$',views.applicant_resume,name='applicant_resume'),
url(r'^(?P<identity>\w+)/(?P<user_id>\d+)/passwd_change/$',views.passwd_change,name='passwd_change'),
url(r'^company/(?P<user_id>\w+)/post/$',views.company_post_list,name='company_post_list'),
url(r'^company/(?P<user_id>\w+)/post/(?P<post_id>)/$',views.company_post_detail,name='company_post_detail'),
# url(r'^company_post_detail_ajax/$',views.company_post_detail_ajax,name='company_post_detail_ajax'),

]