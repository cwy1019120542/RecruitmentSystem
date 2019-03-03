from django.db import models

class Applicant(models.Model):
	phone_number=models.CharField(max_length=255,help_text='手机号码')
	mail=models.CharField(max_length=255,help_text='电子邮箱',null=True)
	person_name=models.CharField(max_length=255,help_text='姓名')
	passwd=models.CharField(max_length=255,help_text='密码')
	register_datetime=models.DateTimeField(auto_now_add=True,help_text='注册时间')
	class Meta:
		db_table='applicant'
		ordering=['register_datetime']
	def __str__(self):
		return self.phone_number+'['+self.person_name+']'

class Company(models.Model):
	phone_number=models.CharField(max_length=255)
	mail=models.CharField(max_length=255)
	person_name=models.CharField(max_length=255)
	passwd=models.CharField(max_length=255)
	company_name=models.CharField(max_length=255)
	register_datetime=models.DateTimeField(auto_now_add=True)
	class Meta:
		db_table='company'
		ordering=['register_datetime']
	def __str__(self):
		return self.company_name

class 