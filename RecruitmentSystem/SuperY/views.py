from django.shortcuts import render,redirect,reverse,HttpResponse
from . import models
from django.db.models import Q
import hashlib

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
		return HttpResponse('该账号不存在')
	if '@' in number:
		phone_number=eval(f'models.{identity.capitalize()}.objects.get(mail=number)')
	else:
		phone_number=number
	passwd=md5_passwd(phone_number,passwd)
	if passwd != same_user[0].passwd:
		return HttpResponse('密码不正确')
	return HttpResponse()

def register(request):
	return render(request,'SuperY/register.html')

def register_ajax(request):
	print(request.POST)
	person_name=request.POST['person_name']
	phone_number=request.POST['phone_number']
	mail=request.POST['mail']
	passwd=request.POST['passwd']
	passwd=md5_passwd(phone_number,passwd)
	print(passwd)
	identity=request.POST['identity']
	same_phone=eval(f'models.{identity.capitalize()}.objects.filter(phone_number=phone_number)')
	if same_phone:
		return HttpResponse('该手机号已被注册')
	if mail:
		same_mail=eval(f'models.{identity.capitalize()}.objects.filter(mail=mail)')
		if same_mail:
			return HttpResponse('该邮箱已被注册')
	eval(f'models.{identity.capitalize()}.objects.create(person_name=person_name,phone_number=phone_number,mail=mail,passwd=passwd)')
	return HttpResponse()