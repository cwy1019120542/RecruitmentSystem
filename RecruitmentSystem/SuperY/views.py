from django.shortcuts import render,redirect,reverse,HttpResponse,get_object_or_404
from . import models
from django.db.models import Q
import hashlib
import demjson
import random
from itertools import chain
from django.core.paginator import Paginator

def md5_passwd(phone_number,passwd):
	deal_text=phone_number[:5]+passwd+phone_number[6:]
	m=hashlib.md5()
	m.update(deal_text.encode('utf8'))
	return m.hexdigest()

def login(request):
	return render(request,'SuperY/login.html')
	
def login_ajax(request):
	number=request.POST['number']
	passwd=request.POST['passwd']
	identity=request.POST['identity']
	same_user=eval(f'models.{identity.capitalize()}.objects.filter(Q(phone_number=number)|Q(mail=number))')
	if not same_user:
		return HttpResponse(demjson.encode({'error':'该账号不存在'}))
	if '@' in number:
		phone_number=eval(f'models.{identity.capitalize()}.objects.get(mail=number)')
	else:
		phone_number=number
	passwd=md5_passwd(phone_number,passwd)
	if passwd != same_user[0].passwd:
		return HttpResponse(demjson.encode({'error':'密码不正确'}))
	request.session['identity']=identity
	request.session['phone_number']=phone_number
	return HttpResponse(demjson.encode({'url':reverse(f'SuperY:{identity}_index',kwargs={'phone_number':phone_number})}))

def register(request):
	return render(request,'SuperY/register.html')

def register_ajax(request):
	person_name=request.POST['person_name']
	phone_number=request.POST['phone_number']
	passwd=request.POST['passwd']
	passwd=md5_passwd(phone_number,passwd)
	identity=request.POST['identity']
	same_phone=eval(f'models.{identity.capitalize()}.objects.filter(phone_number=phone_number)')
	if same_phone:
		return HttpResponse(demjson.encode({'error':'该手机号已被注册'}))
	eval(f'models.{identity.capitalize()}.objects.create(person_name=person_name,phone_number=phone_number,passwd=passwd)')
	return HttpResponse()

def is_login(request,identity,phone_number):
	identity_judge=request.session.get('identity','')
	phone_number_judge=request.session.get('phone_number','')
	if identity_judge != identity or phone_number_judge != phone_number: 
		return redirect(reverse('SuperY:login'))

def logout(request,identity,phone_number):
	is_login(request,identity,phone_number)
	session['identity']=''
	session['phone_number']=''
	return redirect(reverse('SuperY:login'))

def applicant_index(request,phone_number):
	is_login(request,'applicant',phone_number)
	applicant=models.Applicant.objects.get(phone_number=phone_number)
	if request.method == 'POST':
		search_word=request.POST['search_word']
		if not search_word:
			post_list=models.Post.objects.all()
		else:
			models.ApplicantSearch.objects.create(applicant=applicant,search_word=search_word)
			post_list=models.Post.objects.filter(Q(company__company_name__icontains=search_word)|Q(post_name__icontains=search_word)|Q(work_place__icontains=search_word))
		context_dict={'applicant':applicant,'post_list':post_list}
		return render(request,'SuperY/applicant_search.html',context_dict)
	applicant_search_list=models.ApplicantSearch.objects.filter(applicant=applicant)
	if not applicant_search_list:
		post_list=models.Post.objects.all()[:9]
	else:
		search_word=applicant_search_list[0].search_word
		post_list=models.Post.objects.filter(Q(company__company_name__icontains=search_word)|Q(post_name__icontains=search_word)|Q(work_place__icontains=search_word))
	if len(post_list) < 9:
		supply_number=9-len(post_list)
		post_list=chain(post_list,models.Post.objects.all()[:supply_number])
	context_dict={'applicant':applicant,'post_list':post_list}
	return render(request,'SuperY/applicant_index.html',context_dict)

def applicant_search_ajax(request):
	search_word=request.POST['search_word']
	url=reverse('SuperY:applicant_search',kwargs={'phone_number':request.session['phone_number'],'search_word':search_word,'page':1})
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

def post_detail(request,phone_number,post_id):
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
	return render(request,'SuperY/company_index.html')

def company_check(request,phone_number):
	is_login(request,'company',phone_number)
	return render(request,'SuperY/company_check.html')

def company_check_ajax(request):
	company_name=request.POST['company_name']
	company_type=request.POST['company_type']
	main_product=request.POST['main_product']
	staff_number=request.POST['staff_number']
	address=request.POST['address']
	phone_number=request.POST['phone_number']
	company_same=models.Company.objects.filter(company_name=company_name)
	if company_same:
		return HttpResponse(demjson.encode({'error':'该公司已被注册'}))
	models.Company.objects.get(phone_number=phone_number).update(company_name=company_name,company_type=company_type,main_product=main_product,staff_number=staff_number,address=address,is_check=True)