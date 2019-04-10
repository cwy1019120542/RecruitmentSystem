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
from datetime import datetime

def md5_passwd(deal_text):
	m=hashlib.md5()
	m.update(str(deal_text).encode('utf8'))
	return m.hexdigest()

def login(request):
	return render(request,'SuperY/login.html')
	
def login_ajax(request):
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
	login_random=md5_passwd(random.random())
	key=identity+'-'+str(same_user.id)
	request.session[key]=login_random			#session中存储的值更加合理化
	user_id=same_user.id
	response=HttpResponse(demjson.encode({'url':reverse(f'SuperY:{identity}_index',kwargs={'user_id':user_id})}))
	response.set_cookie(key,login_random)
	return response

def register(request):
	return render(request,'SuperY/register.html')

def register_ajax(request):
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

def is_login(func):
	@wraps(func)
	def wrapper(request,identity,user_id,*args,**kwargs):
		key=identity+'-'+str(user_id)
		if key not in request.session or key not in request.COOKIES:				#判断登录状态更严谨
			print('fail1')
			return redirect(reverse('SuperY:login'))
		elif request.session[key] != request.COOKIES[key]:
			print('fail2')
			return redirect(reverse('SuperY:login'))
		return func(request,identity,user_id,*args,**kwargs)
	return wrapper

@is_login
def applicant_index(request,identity,user_id):
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

@is_login
def search_ajax(request,identity,user_id):
	data=request.POST.copy().dict()
	search_word=data['search_word']
	user=eval(f'models.{identity.capitalize()}.objects.get(id=user_id)')
	eval(f'models.{identity.capitalize()}Search.objects.create({identity}=user,search_word=search_word)')		#搜索关键词保存应该放在这里，这样就只会搜索的时候保存一次
	url=reverse(f'SuperY:{identity}_search',kwargs={'user_id':user_id,'search_word':search_word,'page':1})
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

@is_login
def applicant_search(request,identity,user_id,search_word,page):
	applicant=models.Applicant.objects.get(id=user_id)
	post_all=models.Post.objects.filter(Q(company__company_name__icontains=search_word)|Q(post_name__icontains=search_word)|Q(work_place__icontains=search_word))
	post_number,page_all,post_list=my_paginator(post_all,5,page)
	context_dict={'user':applicant,'post_number':post_number,'page_all':page_all,'post_list':post_list}
	return render(request,'SuperY/applicant_post.html',context_dict)

@is_login
def applicant_post_detail(request,identity,user_id,post_id):
	applicant=models.Applicant.objects.get(id=user_id)
	post=models.Post.objects.filter(id=post_id)
	if not post:
		return redirect(reverse('SuperY:applicant_index',kwargs={'user_id':user_id}))
	context_dict={'user':applicant,'post':post[0]}
	return render(request,'SuperY/applicant_post_detail.html',context_dict)

@is_login
def deliver_post_ajax(request,identity,user_id):
	post_id=request.POST['post_id']
	applicant=models.Applicant.objects.get(id=user_id)
	resume=models.Resume.objects.get(applicant=applicant)
	post_list=models.Post.objects.filter(resume=resume)
	post=models.Post.objects.get(id=post_id)
	if post in post_list:
		return HttpResponse(demjson.encode({'message':'fail'}))
	else: 
		post.resume.add(resume)
		return HttpResponse(demjson.encode({'message':'success'})) 

@is_login
def applicant_company_look(request,identity,user_id,page):
	applicant=models.Applicant.objects.get(id=user_id)
	resume=models.Resume.objects.get(applicant=applicant)
	company_all=resume.company_look.all()
	company_number,page_all,company_list=my_paginator(company_all,5,page)
	context_dict={'user':applicant,'company_list':company_list,'company_number':company_number,'page_all':page_all}
	return render(request,'SuperY/applicant_company_look.html',context_dict)

@is_login
def applicant_company_post(request,identity,user_id,company_id,page):
	applicant=models.Applicant.objects.get(id=user_id)
	company=models.Company.objects.get(id=company_id)
	post_all=models.Post.objects.filter(company=company)
	post_number,page_all,post_list=my_paginator(post_all,5,page)
	context_dict={'user':applicant,'post_list':post_list,'post_number':post_number,'page_all':page_all}
	return render(request,'SuperY/applicant_post.html',context_dict)

@is_login
def applicant_deliver_post(request,identity,user_id,page):
	applicant=models.Applicant.objects.get(id=user_id)
	resume=models.Resume.objects.get(applicant=applicant)
	post_all=models.Post.objects.filter(resume=resume)
	post_number,page_all,post_list=my_paginator(post_all,5,page)
	context_dict={'user':applicant,'post_list':post_list,'post_number':post_number,'page_all':page_all}
	return render(request,'SuperY/applicant_post.html',context_dict)

@is_login
def applicant_resume(request,identity,user_id):
	applicant=models.Applicant.objects.get(id=user_id)
	resume=models.Resume.objects.get(applicant=applicant)
	context_dict={'user':applicant,'resume':resume}
	return render(request,'SuperY/applicant_resume.html',context_dict)

@is_login
def resume_info_modify(request,identity,user_id):
	applicant=models.Applicant.objects.get(id=user_id)
	resume=models.Resume.objects.get(applicant=applicant)
	context_dict={'user':applicant,'resume':resume}
	return render(request,'SuperY/resume_info_modify.html',context_dict)

@is_login
def resume_hope_modify(request,identity,user_id):
	applicant=models.Applicant.objects.get(id=user_id)
	resume=models.Resume.objects.select_related('applicant').get(applicant=applicant)
	context_dict={'user':applicant,'resume':resume}
	return render(request,'SuperY/resume_hope_modify.html',context_dict)

@is_login
def resume_info_modify_ajax(request,identity,user_id):
	data=request.POST.copy()
	applicant=models.Applicant.objects.get(id=user_id)
	resume=models.Resume.objects.filter(applicant=applicant)
	data=data.dict()	
	head_pic=request.FILES.get('head_pic','fail')
	if head_pic == 'fail':
		data.pop('head_pic')
		resume.update(**data,update_datetime=datetime.now())
	else:
		head_pic.name=str(resume[0].id)+'.'+head_pic.name.split('.')[1]
		resume.update(**data,head_pic=head_pic,update_datetime=datetime.now())
		pic_path=settings.MEDIA_ROOT+r'\resume\head_pic'
		if not os.path.exists(pic_path):
			os.mkdir(pic_path)
		pic=pic_path+'\\'+head_pic.name
		with open(pic,'wb') as f:
			for chunk in head_pic.chunks():
				f.write(chunk)
	resume=resume[0]
	resume.is_useful=True
	resume.save()
	return HttpResponse()

@is_login
def resume_hope_modify_ajax(request,identity,user_id):
	data=request.POST.copy()
	applicant=models.Applicant.objects.get(id=user_id)
	data=data.dict()
	models.Resume.objects.filter(applicant=applicant).update(**data)
	return HttpResponse()

@is_login
def experience(request,identity,user_id,experience_name,experience_id=None):
	applicant=models.Applicant.objects.get(id=user_id)
	resume=models.Resume.objects.get(applicant=applicant)
	if experience_id:
		experience_name_class=experience_name.title().replace('_','')
		experience=eval(f'models.{experience_name_class}.objects.get(id=experience_id)')
		context_dict={'user':applicant,'experience':experience}
	else:
		context_dict={'user':applicant}
	return render(request,f'SuperY/{experience_name}.html',context_dict)

@is_login
def experience_ajax(request,identity,user_id):
	data=request.POST.copy()
	applicant=models.Applicant.objects.get(id=user_id)
	resume=models.Resume.objects.get(applicant=applicant)
	experience_id=data.pop('experience_id')[0]
	experience_name=data.pop('experience_name')[0]
	data=data.dict()
	if not experience_id:
		eval(f'models.{experience_name}.objects.create(resume=resume,**data)')
	else:		
		eval(f'models.{experience_name}.objects.filter(id=experience_id).update(**data)')
	resume.update_datetime=datetime.now()
	resume.save()
	return HttpResponse()

@is_login
def company_index(request,identity,user_id):
	company=models.Company.objects.get(id=user_id)
	if not company.is_check:
		return redirect(reverse('SuperY:company_check',kwargs={'user_id':user_id}))
	resume_number=models.Resume.objects.filter(company_look=company).count()
	post_list=models.Post.objects.filter(company=company)
	receive_resume=0
	for post in post_list:
		receive_resume+=post.resume.count()
	company_search_list=models.CompanySearch.objects.filter(company=company)
	if not company_search_list:
		resume_list=models.Resume.objects.filter(is_useful=True)[:9]
	else:
		search_word=company_search_list[0]
		resume_list=models.Resume.objects.filter(Q(work_place__icontains=search_word)|Q(post_name__icontains=search_word)|Q(profession__icontains=search_word),is_useful=True)
	context_dict={'user':company,'resume_number':resume_number,'receive_resume':receive_resume,'resume_list':resume_list}
	return render(request,'SuperY/company_index.html',context_dict)

@is_login
def company_check(request,identity,user_id):
	company=models.Company.objects.get(id=user_id)
	if company.is_check:
		return redirect(reverse('SuperY:company_index',kwargs={'user_id':user_id}))
	context_dict={'user':company}
	return render(request,'SuperY/company_check.html',context_dict)

@is_login
def company_check_ajax(request,identity,user_id):
	data=request.POST.copy()
	company_name=data['company_name']
	company_same=models.Company.objects.filter(company_name=company_name)
	if company_same:
		return HttpResponse(demjson.encode({'company_name_error':'该公司已被注册'}))
	business_licence=request.FILES['business_licence']
	data=data.dict()
	company_same.update(**data,is_check=True,business_licence=business_licence)
	pic_path=settings.MEDIA_ROOT+r'\company\business_licence'
	if not os.path.exists(pic_path):
		os.mkdir(pic_path)
	pic=pic_path+'\\'+str(user_id)+'.'+business_licence.name.split('.')[1]
	with open(pic,'wb') as f:
		for chunk in business_licence.chunks():
			f.write(chunk)
	return HttpResponse()

@is_login
def company_info_ajax(request,identity,user_id):
	data=request.POST.copy()
	company=models.Company.objects.filter(id=user_id)
	company_name=data['company_name']
	company_same=models.Company.objects.filter(company_name=company_name)
	if company[0] != company_same[0]:
		return HttpResponse(demjson.encode({'company_name_error':'该公司已被注册'}))
	business_licence=request.FILES.get('business_licence','fail')
	data=data.dict()
	if business_licence == 'fail':
		data.pop('business_licence')
		company_same.update(**data)
		return HttpResponse()
	business_licence.name=str(user_id)+'.'+business_licence.name.split('.')[1]
	company_same.update(**data,business_licence=business_licence)
	pic_path=settings.MEDIA_ROOT+r'\company\business_licence'
	if not os.path.exists(pic_path):
		os.mkdir(pic_path)
	pic=pic_path+'\\'+business_licence.name
	with open(pic,'wb') as f:
		for chunk in business_licence.chunks():
			f.write(chunk)
	return HttpResponse()

@is_login
def company_search(request,identity,user_id,search_word,page):
	company=models.Company.objects.get(id=user_id)
	resume_all=models.Resume.objects.filter(Q(post_name__icontains=search_word)|Q(work_place__icontains=search_word)|Q(profession__icontains=search_word),is_useful=True)
	resume_number,page_all,resume_list=my_paginator(resume_all,5,page)
	context_dict={'user':company,'resume_number':resume_number,'page_all':page_all,'resume_list':resume_list}
	return render(request,'SuperY/company_resume.html',context_dict)

@is_login
def company_info(request,identity,user_id):
	company=models.Company.objects.get(id=user_id)
	context_dict={'user':company}
	return render(request,'SuperY/company_info.html',context_dict)

@is_login
def company_resume_detail(request,identity,user_id,resume_id):
	company=models.Company.objects.get(id=user_id)
	resume=models.Resume.objects.get(id=resume_id)
	resume.company_look.add(company)
	context_dict={'user':company,'resume':resume}
	return render(request,'SuperY/company_resume_detail.html',context_dict)

@is_login
def company_post(request,identity,user_id,page):
	company=models.Company.objects.get(id=user_id)
	post_all=models.Post.objects.filter(company=company)
	post_number,page_all,post_list=my_paginator(post_all,5,page)
	context_dict={'user':company,'post_list':post_list,'post_number':post_number,'page_all':page_all}
	return render(request,'SuperY/company_post.html',context_dict)

@is_login
def company_post_detail(request,identity,user_id,post_id):
	company=models.Company.objects.get(id=user_id)
	post=models.Post.objects.get(id=post_id)
	context_dict={'user':company,'post':post_id}
	return render(request,'SuperY/company_post_detail.html',context_dict)

@is_login
def company_post_modify(request,identity,user_id,post_id=None):
	company=models.Company.objects.get(id=user_id)
	tag_list=models.Tag.objects.all()
	if post_id:
		post=models.Post.objects.get(id=post_id)
		context_dict={'user':company,'tag_list':tag_list,'post':post}
	else:
		context_dict={'user':company,'tag_list':tag_list}
	return render(request,'SuperY/company_post_modify.html',context_dict)

@is_login
def company_post_modify_ajax(request,identity,user_id):
	data=request.POST.copy().dict()
	company=models.Company.objects.get(id=user_id)
	post_id=data.pop('post_id')
	tag_id_list=data.pop('tag_id_list')
	if post_id:
		post=models.Post.objects.filter(id=post_id)
		post.update(**data,company=company,update_datetime=datetime.now())
		post=post[0]
	else:
		post=models.Post.objects.create(**data,company=company,update_datetime=datetime.now())
	tag_id_list=tag_id_list.split(',')
	if tag_id_list[0]:
		tag_list=(models.Tag.objects.get(id=int(tag_id)) for tag_id in tag_id_list)
		post.tag.clear()
		post.tag.add(*tag_list)
	return HttpResponse()

@is_login
def company_company_look(request,identity,user_id,page):
	company=models.Company.objects.get(id=user_id)
	resume_all=models.Resume.objects.filter(company_look=company)
	resume_number,page_all,resume_list=my_paginator(resume_all,5,page)
	context_dict={'user':company,'resume_number':resume_number,'page_all':page_all,'resume_list':resume_list}
	return render(request,'SuperY/company_resume.html',context_dict)

@is_login
def company_receive_resume(request,identity,user_id,page):
	company=models.Company.objects.get(id=user_id)
	post_list=models.Post.objects.filter(company=company)
	resume_all=[]
	for post in post_list:
		for resume in post.resume.all():
			resume_all.append((post,resume))
	resume_number,page_all,resume_list=my_paginator(resume_all,5,page)
	print(resume_list)
	context_dict={'user':company,'resume_number':resume_number,'page_all':page_all,'resume_list':resume_list,'receive':True}
	return render(request,'SuperY/company_resume.html',context_dict)

@is_login
def person_info(request,identity,user_id):
	user=eval(f'models.{identity.capitalize()}.objects.get(id=user_id)')
	context_dict={'user':user}
	return render(request,f'SuperY/{identity}_person_info.html',context_dict)

@is_login
def person_info_ajax(request,identity,user_id):
	data=request.POST.copy().dict()
	phone_number=data.pop('phone_number')
	head_pic=request.FILES.get('head_pic','fail')
	user=eval(f'models.{identity.capitalize()}.objects.filter(id=user_id)')
	same_user=eval(f'models.{identity.capitalize()}.objects.filter(phone_number=phone_number)')
	passwd=data['passwd']
	passwd=user[0].phone_number[:5]+passwd+user[0].phone_number[6:]
	passwd=md5_passwd(passwd)
	if user[0].passwd != passwd:
		return HttpResponse(demjson.encode({'passwd_error':'密码不正确'}))
	if not same_user or same_user[0] == user[0]:
		if not same_user:
			passwd=phone_number[:5]+data['passwd']+phone_number[6:]
			passwd=md5_passwd(passwd)
			data['passwd']=passwd
			data['phone_number']=phone_number
		else:
			data.pop('passwd')
		if head_pic == 'fail':
			data.pop('head_pic')
			user.update(**data)
		else:
			head_pic.name=str(user_id)+'.'+head_pic.name.split('.')[-1]
			pic=settings.MEDIA_ROOT+'//'+identity+r'\head_pic'+'\\'+head_pic.name
			with open(pic,'wb') as f:
				for chunk in head_pic.chunks():
					f.write(chunk)
			user.update(**data,head_pic=head_pic)
		return HttpResponse()
	else:
		return HttpResponse(demjson.encode({'phone_number_error':'该手机号已被注册'}))

@is_login
def passwd_change(request,identity,user_id):
	user=eval(f'models.{identity.capitalize()}.objects.get(id=user_id)')
	context_dict={'user':user}
	return render(request,f'SuperY/{identity}_passwd_change.html',context_dict)

@is_login
def passwd_change_ajax(request,identity,user_id):
	data=request.POST.copy().dict()
	old_passwd=data.pop('old_passwd')
	user=eval(f'models.{identity.capitalize()}.objects.get(id=user_id)')
	phone_number=user.phone_number
	deal_text=phone_number[:5]+old_passwd+phone_number[6:]
	old_passwd=md5_passwd(deal_text)
	if old_passwd != user.passwd:
		return HttpResponse(demjson.encode({'old_passwd_error':'原密码错误'}))
	new_passwd=data.pop('new_passwd')
	deal_text=phone_number[:5]+new_passwd+phone_number[6:]
	new_passwd=md5_passwd(deal_text)
	user.passwd=new_passwd
	user.save()
	return HttpResponse()

@is_login
def logout(request,identity,user_id):
	user=eval(f'models.{identity.capitalize()}.objects.get(id=user_id)')
	key=identity+'-'+str(user_id)
	request.session.pop(key)
	return redirect(reverse('SuperY:login'))

def forget_passwd(request):
	return render(request,'SuperY/forget_passwd.html')

def forget_passwd_ajax(request):
	data=request.POST.copy().dict()
	user_id=data['user_id']
	identity=data['identity']
	person_name=data['person_name']
	phone_number=data['phone_number']
	register_datetime=data['register_datetime']
	user=eval(f'models.{identity.capitalize()}.objects.filter(person_name=person_name,id=user_id,phone_number=phone_number)')
	if not user:
		return HttpResponse(demjson.encode({'phone_number_error':'该用户不存在'}))
	else:
		print()
		if str(user[0].register_datetime).split('+')[0] != register_datetime:
			return HttpResponse(demjson.encode({'phone_number_error':'该用户不存在'}))
		passwd=data['passwd']
		deal_text=phone_number[:5]+passwd+phone_number[6:]
		user[0].passwd=md5_passwd(deal_text)
		user[0].save()
		return HttpResponse()

def page_not_found(request,**kwargs):
	return render(request,'SuperY/404.html')
