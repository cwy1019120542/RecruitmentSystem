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

def md5_passwd(phone_number,passwd):
	deal_text=phone_number[:5]+passwd+phone_number[6:]
	m=hashlib.md5()
	m.update(deal_text.encode('utf8'))
	return m.hexdigest()

def login(request):
	return render(request,'SuperY/login.html')
	
def login_ajax(request):
	print(request.POST)
	number=request.POST['number']
	passwd=request.POST['passwd']
	identity=request.POST['identity']
	same_user=eval(f'models.{identity.capitalize()}.objects.filter(Q(phone_number=number)|Q(mail=number))')
	if not same_user:
		return HttpResponse(demjson.encode({'number_error':'该账号不存在'}))
	if '@' in number:
		phone_number=eval(f'models.{identity.capitalize()}.objects.get(mail=number)')
	else:
		phone_number=number
	passwd=md5_passwd(phone_number,passwd)
	if passwd != same_user[0].passwd:
		return HttpResponse(demjson.encode({'passwd_error':'密码不正确'}))
	same_user=same_user[0]
	same_user.login_random=str(random.random())
	same_user.save()
	request.session[phone_number]=identity+'-'+same_user.login_random
	return HttpResponse(demjson.encode({'url':reverse(f'SuperY:{identity}_index',kwargs={'phone_number':phone_number})}))

def register(request):
	return render(request,'SuperY/register.html')

def register_ajax(request):
	print(request.POST)
	data=request.POST.copy()
	phone_number=data['phone_number']
	data['passwd']=md5_passwd(phone_number,data['passwd'])
	identity=data.pop('identity')[0]
	same_phone=eval(f'models.{identity.capitalize()}.objects.filter(phone_number=phone_number)')
	if same_phone:
		return HttpResponse(demjson.encode({'phone_number_error':'该手机号已被注册'}))
	else:
		data=data.dict()
		eval(f'models.{identity.capitalize()}.objects.create(**data)')
		url=reverse('SuperY:login')
		return HttpResponse(demjson.encode({'url':url}))

def is_login(request,identity,phone_number):
	user=eval(f'models.{identity.capitalize()}.objects.get(phone_number=phone_number)')
	if phone_number not in request.session:
		return redirect(reverse('SuperY:login'))
	else:
		if request.session[phone_number] != identity+'-'+user.login_random:
			return redirect(reverse('SuperY:login'))


def logout(request,identity,phone_number):
	is_login(request,identity,phone_number)
	request.session.pop(phone_number)
	return redirect(reverse('SuperY:login'))

def applicant_index(request,phone_number):
	is_login(request,'applicant',phone_number)
	applicant=models.Applicant.objects.get(phone_number=phone_number)
	applicant_search_list=models.ApplicantSearch.objects.filter(applicant=applicant)
	if not applicant_search_list:
		post_list=models.Post.objects.all()[:9]
	else:
		search_word=applicant_search_list[0].search_word
		post_list=models.Post.objects.filter(Q(company__company_name__icontains=search_word)|Q(post_name__icontains=search_word)|Q(work_place__icontains=search_word))[:9]
	if len(post_list) < 9:
		supply_number=9-len(post_list)
		post_list=chain(post_list,models.Post.objects.all()[:supply_number])
	resume=models.Resume.objects.filter(applicant=applicant)
	if not resume:
		company_look=0
		deliver_post=0
	else:
		company_look=resume[0].company_look.count()
		deliver_post=resume[0].post_set.all().count()
	context_dict={'user':applicant,'post_list':post_list,'company_look':company_look,'deliver_post':deliver_post}
	return render(request,'SuperY/applicant_index.html',context_dict)

def applicant_search_ajax(request):
	data=request.POST.copy()
	search_word=data['search_word']
	phone_number=data['phone_number']
	url=reverse('SuperY:applicant_search',kwargs={'phone_number':phone_number,'search_word':search_word,'page':1})
	return HttpResponse(demjson.encode({'url':url}))

def my_paginator(data_all,page_data_number,aim_page):
	paginator=Paginator(data_all,page_data_number)
	data_list=paginator.page(aim_page)
	return paginator.count,paginator.num_pages,data_list


def applicant_search(request,phone_number,search_word,page):
	is_login(request,'applicant',phone_number)
	applicant=models.Applicant.objects.get(phone_number=phone_number)
	post_all=models.Post.objects.filter(Q(company__company_name__icontains=search_word)|Q(post_name__icontains=search_word)|Q(work_place__icontains=search_word))
	if post_all:
		models.ApplicantSearch.objects.create(applicant=applicant,search_word=search_word)
	post_number,page_all,post_list=my_paginator(post_all,5,page)
	context_dict={'applicant':applicant,'post_number':post_number,'page_all':page_all,'post_list':post_list}
	return render(request,'SuperY/applicant_search.html',context_dict)

def applicant_post_detail(request,phone_number,post_id):
	is_login(request,'applicant',phone_number)
	applicant=models.Applicant.objects.get(phone_number=phone_number)
	post=models.Post.objects.get(id=post_id)
	context_dict={'applicant':applicant,'post':post}
	return render(request,'SuperY/post_detail',context_dict)

def company_index(request,phone_number):
	is_login(request,'company',phone_number)
	company=models.Company.objects.get(phone_number=phone_number)
	if not company.is_check:
		return redirect(reverse('SuperY:company_check',kwargs={'phone_number':phone_number}))
	company_look=models.Resume.objects.filter(company_look=company).count()
	post_list=models.Post.objects.filter(company=company)
	receive_resume=0
	for post in post_list:
		receive_resume+=post.resume.count()
	context_dict={'user':company,'company_look':company_look,'receive_resume':receive_resume}
	return render(request,'SuperY/company_index.html',context_dict)

def company_check(request,phone_number):
	is_login(request,'company',phone_number)
	company=models.Company.objects.get(phone_number=phone_number)
	if company.is_check:
		return redirect(reverse('SuperY:company_index',kwargs={'phone_number':phone_number}))
	return render(request,'SuperY/company_check.html')

def company_check_ajax(request):
	data=request.POST.copy()
	company_name=data['company_name']
	company_same=models.Company.objects.filter(company_name=company_name)
	if company_same:
		return HttpResponse(demjson.encode({'error':'该公司已被注册'}))
	business_licence=request.FILES['business_licence']
	phone_number=data.pop('phone_number')[0]
	models.Company.objects.filter(phone_number=phone_number).update(**data,is_check=True,business_licence=business_licence)
	pic_path=settings.MEDIA_ROOT+r'\company\business_licence'+'\\'+company_name
	if not os.path.exists(pic_path):
		os.mkdir(pic_path)
	pic=pic_path+'\\'+business_licence.name
	with open(pic,'wb') as f:
		for chunk in business_licence.chunks():
			f.write(chunk)
	return HttpResponse(demjson.encode({'url':reverse('SuperY:company_index',kwargs={'phone_number':phone_number})}))

def applicant_resume_detail(request,phone_number):
	is_login(request,'applicant',phone_number)
	applicant=models.Applicant.objects.get(phone_number=phone_number)
	resume=applicant.resume
	context_dict={'user':applicant,'resume':resume}
	return render(request,'SuperY/resume_index.html',context_dict)

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

def company_post_list(request,phone_number):
	is_login(request,'company',phone_number)
	company=models.Company.objects.get(phone_number=phone_number)
	post_list=models.Post.objects.filter(company=company)
	context_dict={'user':company,'post_list':post_list}
	return render(request,'SuperY/company_post_list.html',context_dict)

def company_post_detail(request,phone_number,post_id):
	is_login(request,'company',phone_number)
	company=models.Company.objects.get(phone_number=phone_number)
	post=models.Post.objects.get(id=post_id)
	context_dict={'user':company,'post':post_id}
	return render(request,'SuperY/company_post_detail.html',context_dict)

# def company_post_detail_ajax(request):
# 	data=request.POST().copy()
# 	phone_number=data.pop('phone_number')
# 	is_login(request,'company',phone_number)
# 	post_tag_list=data
