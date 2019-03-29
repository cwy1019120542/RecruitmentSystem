from django.shortcuts import render,redirect,reverse,HttpResponse,get_object_or_404
from . import models
from django.db.models import Q
import hashlib
import demjson
import random
from itertools import chain
from django.core.paginator import Paginator
from django.conf import settings
import os
import random
from functools import wraps

def md5_passwd(deal_text):
	m=hashlib.md5()
	m.update(deal_text.encode('utf8'))
	return m.hexdigest()

def login(request):
	return render(request,'SuperY/login.html')
	
def login_ajax(request):
	print(request.POST)
	phone_number=request.POST['phone_number']
	passwd=request.POST['passwd']
	identity=request.POST['identity']
	same_user=eval(f'models.{identity.capitalize()}.objects.filter(phone_number=phone_number)')
	if not same_user:
		return HttpResponse(demjson.encode({'phone_number_error':'该账号不存在'}))
	deal_text=phone_number[:5]+passwd+phone_number[6:]
	passwd=md5_passwd(deal_text)
	if passwd != same_user[0].passwd:
		return HttpResponse(demjson.encode({'passwd_error':'密码不正确'}))
	same_user=same_user[0]
	same_user.login_random=str(random.random())
	same_user.save()
	key=identity+'-'+str(same_user.id)
	request.session[key]=same_user.login_random			#session中存储的值更加合理化
	user_id=same_user.id
	return HttpResponse(demjson.encode({'url':reverse(f'SuperY:{identity}_index',kwargs={'user_id':user_id})}))

def register(request):
	return render(request,'SuperY/register.html')

def register_ajax(request):
	print(request.POST)
	data=request.POST.copy()
	phone_number=data['phone_number']
	deal_text=phone_number[:5]+data['passwd']+phone_number[6:]
	data['passwd']=md5_passwd(deal_text)
	identity=data.pop('identity')[0]
	same_phone=eval(f'models.{identity.capitalize()}.objects.filter(phone_number=phone_number)')
	if same_phone:
		return HttpResponse(demjson.encode({'phone_number_error':'该手机号已被注册'}))
	else:
		data=data.dict()
		eval(f'models.{identity.capitalize()}.objects.create(**data)')
		if identity == 'applicant':
			applicant=models.Applicant.objects.get(phone_number=phone_number)
			models.Resume.objects.create(applicant=applicant)
		url=reverse('SuperY:login')
		return HttpResponse(demjson.encode({'url':url}))

def is_login(identity):
	def login_judge(func):
		@wraps(func)
		def wrapper(request,user_id,*args,**kwargs):
			user=eval(f'models.{identity.capitalize()}.objects.filter(id=user_id)')
			key=identity+'-'+str(user_id)
			if key not in request.session:				#判断登录状态更严谨
				print('fail1')
				return redirect(reverse('SuperY:login'))
			elif not user:
				print('fail2')
				return redirect(reverse('SuperY:login'))
			elif request.session[key] != user[0].login_random:
				print('fail3')
				return redirect(reverse('SuperY:login'))
			print('success')
			return func(request,user_id,*args,**kwargs)
		return wrapper
	return login_judge

@is_login('applicant')
def applicant_index(request,user_id):
	applicant=models.Applicant.objects.get(id=user_id)
	applicant_search_list=models.ApplicantSearch.objects.filter(applicant=applicant)
	if not applicant_search_list:
		post_list=models.Post.objects.all()[:9]
	else:
		search_word=applicant_search_list[0].search_word
		post_list=models.Post.objects.filter(Q(company__company_name__icontains=search_word)|Q(post_name__icontains=search_word)|Q(work_place__icontains=search_word))[:9]
	if len(post_list) < 9:
		supply_number=9-len(post_list)
		post_list=chain(post_list,models.Post.objects.all()[:supply_number])
	resume=models.Resume.objects.get(applicant=applicant)
	context_dict={'user':applicant,'post_list':post_list,'resume':resume}
	return render(request,'SuperY/applicant_index.html',context_dict)

def applicant_search_ajax(request):
	data=request.POST.copy()
	search_word=data['search_word']
	user_id=data['user_id']
	applicant=models.Applicant.objects.get(id=user_id)
	models.ApplicantSearch.objects.create(applicant=applicant,search_word=search_word)		#搜索关键词保存应该放在这里，这样就只会搜索的时候保存一次
	url=reverse('SuperY:applicant_search_post',kwargs={'user_id':user_id,'search_word':search_word,'page':1})
	return HttpResponse(demjson.encode({'url':url}))

def my_paginator(data_all,page_data_number,aim_page):
	paginator=Paginator(data_all,page_data_number)
	all_page_number=paginator.num_pages
	if int(aim_page)<1:
		aim_page=1
	elif int(aim_page)>all_page_number:
		aim_page=all_page_number
	data_list=paginator.page(aim_page)
	return paginator.count,paginator.num_pages,data_list

@is_login('applicant')
def applicant_search_post(request,user_id,search_word,page):
	applicant=models.Applicant.objects.get(id=user_id)
	post_all=models.Post.objects.filter(Q(company__company_name__icontains=search_word)|Q(post_name__icontains=search_word)|Q(work_place__icontains=search_word))
	post_number,page_all,post_list=my_paginator(post_all,5,page)
	context_dict={'user':applicant,'post_number':post_number,'page_all':page_all,'post_list':post_list}
	return render(request,'SuperY/applicant_post.html',context_dict)

@is_login('applicant')
def applicant_post_detail(request,user_id,post_id):
	applicant=models.Applicant.objects.get(id=user_id)
	post=models.Post.objects.filter(id=post_id)
	if not post:
		return redirect(reverse('SuperY:applicant_index',kwargs={'user_id':user_id}))
	context_dict={'user':applicant,'post':post[0]}
	return render(request,'SuperY/applicant_post_detail.html',context_dict)

def deliver_post_ajax(request):
	post_id=request.POST['post_id']
	user_id=request.POST['user_id']
	applicant=models.Applicant.objects.get(id=user_id)
	resume=models.Resume.objects.get(applicant=applicant)
	post_list=models.Post.objects.filter(resume=resume)
	post=models.Post.objects.get(id=post_id)
	if post in post_list:
		return HttpResponse(demjson.encode({'message':'fail'}))
	else: 
		post.resume.add(resume)
		return HttpResponse(demjson.encode({'message':'success'})) 

@is_login('applicant')
def applicant_company_look(request,user_id,page):
	applicant=models.Applicant.objects.get(id=user_id)
	resume=models.Resume.objects.get(applicant=applicant)
	company_all=resume.company_look.all()
	company_number,page_all,company_list=my_paginator(company_all,5,page)
	context_dict={'user':applicant,'company_list':company_list,'company_number':company_number,'page_all':page_all}
	return render(request,'SuperY/applicant_company_look.html',context_dict)

@is_login('applicant')
def applicant_company_post(request,user_id,company_id,page):
	applicant=models.Applicant.objects.get(id=user_id)
	company=models.Company.objects.get(id=company_id)
	post_all=models.Post.objects.filter(company=company)
	post_number,page_all,post_list=my_paginator(post_all,5,page)
	context_dict={'user':applicant,'post_list':post_list,'post_number':post_number,'page_all':page_all}
	return render(request,'SuperY/applicant_post.html',context_dict)

@is_login('applicant')
def applicant_deliver_post(request,phone_number):
	applicant=models.Applicant.objects.get(phone_number=phone_number)
	resume=models.Resume.objects.get(applicant=applicant)
	post_all=models.Post.objects.filter(resume=resume)
	post_list=my_paginator(post_all,5,page)
	context_dict={'user':applicant,'post_list':post_list}
	return render(request,'Super/applicant_company_post.html',context_dict)

@is_login('applicant')
def applicant_logout(request,user_id):
	applicant=models.Applicant.objects.get(id=user_id)
	key='applicant'+'-'+str(user_id)
	request.session.pop(key)
	return redirect(reverse('SuperY:login'))

@is_login('applicant')
def applicant_resume(request,user_id):
	applicant=models.Applicant.objects.get(id=user_id)
	resume=models.Resume.objects.get(applicant=applicant)
	context_dict={'user':applicant,'resume':resume}
	return render(request,'SuperY/applicant_resume.html',context_dict)

def applicant_resume_ajax(request):
	data=request.POST.copy()
	phone_number=data.pop('phone_number')[0]
	is_login(request,'applicant',phone_number)
	head_pic=request.FILES['head_pic']
	update_type=data.pop('update_type')[0]
	if update_type == 'add':
		applicant=models.Applicant.objects.get(phone_number=phone_number)
		models.Resume.objects.create(applicant=applicant,head_pic=head_pic,**data)
	else:
		resume_id=data.pop('resume_id')[0]
		models.Resume.objects.filter(id=resume_id).update(head_pic=head_pic,**data)
	return HttpResponse()

def work_experience_ajax(request):
	data=request.POST.copy()
	phone_number=data.pop('phone_number')[0]
	is_login(request,'applicant',phone_number)
	update_type=data.pop('update_type')[0]
	if update_type == 'add':
		resume_id=data.pop('resume_id')[0]
		resume=models.Resume.objects.get(id=resume_id)
		models.WorkExperience.objects.create(resume=resume,**data)
	else:		
		work_experience_id=data.pop('work_experience_id')[0]
		models.WorkExperience.objects.filter(id=work_experience_id).update(**data)
	return HttpResponse()

def project_experience_ajax(request):
	data=request.POST.copy()
	phone_number=data.pop('phone_number')[0]
	is_login(request,'applicant',phone_number)
	update_type=data.pop('update_type')[0]
	if update_type == 'add':
		resume_id=data.pop('resume_id')[0]
		resume=models.Resume.objects.get(id=resume_id)
		models.ProjectExperience.objects.create(resume=resume,**data)
	else:		
		project_experience_id=data.pop('project_experience_id')[0]
		models.ProjectExperience.objects.filter(id=project_experience_id).update(**data)
	return HttpResponse()

def educate_experience_ajax(request):
	data=request.POST.copy()
	phone_number=data.pop('phone_number')[0]
	is_login(request,'applicant',phone_number)
	update_type=data.pop('update_type')[0]
	if update_type == 'add':
		resume_id=data.pop('resume_id')[0]
		resume=models.Resume.objects.get(id=resume_id)
		models.EducateExperience.objects.create(resume=resume,**data)
	else:		
		educate_experience_id=data.pop('educate_experience_id')[0]
		models.EducateExperience.objects.filter(id=educate_experience_id).update(**data)
	return HttpResponse()

def skill_ajax(request):
	data=request.POST.copy()
	phone_number=data.pop('phone_number')[0]
	is_login(request,'applicant',phone_number)
	update_type=data.pop('update_type')[0]
	if update_type == 'add':
		resume_id=data.pop('resume_id')[0]
		resume=models.Resume.objects.get(id=resume_id)
		models.Skill.objects.create(resume=resume,**data)
	else:		
		skill_id=data.pop('skill_id')[0]
		models.Skill.objects.filter(id=skill_id).update(**data)
	return HttpResponse()



@is_login('company')
def company_index(request,user_id):
	company=models.Company.objects.get(id=user_id)
	if not company.is_check:
		return redirect(reverse('SuperY:company_check',kwargs={'user_id':user_id}))
	resume_number=models.Resume.objects.filter(company_look=company).count()
	post_list=models.Post.objects.filter(company=company)
	receive_resume=0
	for post in post_list:
		receive_resume+=post.resume.count()
	context_dict={'user':company,'resume_number':resume_number,'receive_resume':receive_resume}
	return render(request,'SuperY/company_index.html',context_dict)

@is_login('company')
def company_check(request,user_id):
	company=models.Company.objects.get(id=user_id)
	if company.is_check:
		return redirect(reverse('SuperY:company_index',kwargs={'user_id':user_id}))
	context_dict={'user':company}
	return render(request,'SuperY/company_check.html',context_dict)

def company_check_ajax(request):
	data=request.POST.copy()
	company_name=data['company_name']
	company_same=models.Company.objects.filter(company_name=company_name)
	if company_same:
		return HttpResponse(demjson.encode({'company_name_error':'该公司已被注册'}))
	business_licence=request.FILES['business_licence']
	user_id=data.pop('user_id')[0]
	data=data.dict()
	models.Company.objects.filter(id=user_id).update(**data,is_check=True,business_licence=business_licence)
	pic_path=settings.MEDIA_ROOT+r'\company\business_licence'+'\\'+company_name
	if not os.path.exists(pic_path):
		os.mkdir(pic_path)
	pic=pic_path+'\\'+business_licence.name
	with open(pic,'wb') as f:
		for chunk in business_licence.chunks():
			f.write(chunk)
	return HttpResponse()

def company_search_ajax(request):
	data=request.POST.copy()
	search_word=data['search_word']
	user_id=data['user_id']
	company=models.Company.objects.get(id=user_id)
	models.CompanySearch.objects.create(company=company,search_word=search_word)		#搜索关键词保存应该放在这里，这样就只会搜索的时候保存一次
	url=reverse('SuperY:company_search_resume',kwargs={'user_id':user_id,'search_word':search_word,'page':1})
	return HttpResponse(demjson.encode({'url':url}))

@is_login('company')
def company_search_resume(request,user_id,search_word,page):
	company=models.Company.objects.get(id=user_id)
	resume_all=models.Resume.objects.filter(Q(post_name__icontains=search_word)|Q(work_place__icontains=search_word)|Q(gradute__icontains=search_word))
	resume_number,page_all,resume_list=my_paginator(resume_all,5,page)
	context_dict={'user':applicant,'resume_number':resume_number,'page_all':page_all,'resume_list':resume_list}
	return render(request,'SuperY/company_resume.html',context_dict)


def passwd_change(request,identity,phone_number):
	user=eval(f'models.{identity.capitalize()}.objects.get(phone_number=phone_number)')
	context_dict={'user':user}
	return render(request,'SuperY/passwd_change.html',context_dict)

def passwd_change_ajax(request):
	data=request.POST.copy()
	identity=data.pop('identity')
	phone_number=data.pop('phone_number')
	is_login(request,identity,phone_number)
	old_passwd=data.pop('old_passwd')
	user=eval(f'models.{identity.capitalize()}.objects.get(phone_number=phone_number)')
	if old_passwd != user.passwd:
		return HttpResponse()
	new_passwd=data.pop('new_passwd')
	user.passwd=new_passwd
	user.save()
	return HttpResponse()

def company_resume_detail(request,phone_number,resume_id):
	is_login(request,'company',phone_number)
	company=models.Company.objects.get(phone_number=phone_number)
	resume=models.Resume.objects.get(id=resume_id)
	context_dict={'user':company,'resume':resume}
	return render(request,'SuperY/company_resume.html',context_dict)

def company_post_list(request,phone_number,page):
	is_login(request,'company',phone_number)
	company=models.Company.objects.get(phone_number=phone_number)
	post_all=models.Post.objects.filter(company=company)
	post_list=my_paginator(post_all,5,page)
	context_dict={'user':company,'post_list':post_list}
	return render(request,'SuperY/company_post_list.html',context_dict)

def company_post_detail(request,phone_number,post_id):
	is_login(request,'company',phone_number)
	company=models.Company.objects.get(phone_number=phone_number)
	post=models.Post.objects.get(id=post_id)
	context_dict={'user':company,'post':post_id}
	return render(request,'SuperY/company_post_detail.html',context_dict)

def company_post_detail_ajax(request):
	data=request.POST().copy()
	phone_number=data.pop('phone_number')[0]
	is_login(request,'company',phone_number)
	post_id=data.pop('post_id')[0]
	post=models.Post.objects.get(id=post_id)
	tag_id_list=data.pop('tag_id_list')
	post.tag.clear()
	for tag_id in tag_id_list:
		tag=models.Tag.objects.get(id=tag_id)
		post.tag.add(tag)


@is_login('company')
def company_logout(request,user_id):
	company=models.Company.objects.get(id=user_id)
	key='company'+'-'+str(user_id)
	request.session.pop(key)
	return redirect(reverse('SuperY:login'))
