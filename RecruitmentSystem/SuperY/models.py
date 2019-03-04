from django.db import models

class Applicant(models.Model):
	phone_number=models.CharField(max_length=255,help_text='手机号码')
	mail=models.CharField(max_length=255,help_text='电子邮箱',null=True)
	person_name=models.CharField(max_length=255,help_text='注册人姓名')
	passwd=models.CharField(max_length=255,help_text='密码')
	register_datetime=models.DateTimeField(auto_now_add=True,help_text='注册时间')
	class Meta:
		db_table='applicant'
		ordering=['register_datetime']
	def __str__(self):
		return self.phone_number+'['+self.person_name+']'

class Company(models.Model):
	phone_number=models.CharField(max_length=255,help_text='手机号码')
	mail=models.CharField(max_length=255,help_text='电子邮箱')
	person_name=models.CharField(max_length=255,help_text='注册人姓名')
	passwd=models.CharField(max_length=255,help_text='密码')
	company_name=models.CharField(max_length=255,help_text='公司名称',null=True)
	register_datetime=models.DateTimeField(auto_now_add=True,help_text='注册时间')
	company_info=models.TextField(null=True)
	class Meta:
		db_table='company'
		ordering=['register_datetime']
	def __str__(self):
		return self.company_name

class ApplicantSearch(models.Model):
	applicant=models.ForeignKey(Applicant,on_delete=models.CASCADE,help_text='搜索人')
	search_word=models.CharField(max_length=255,help_text='搜索关键词')
	search_datetime=models.DateTimeField(auto_now_add=True,help_text='搜索时间')
	class Meta:
		db_table='applicant_search'
		ordering=['search_datetime']
	def __str__(self):
		return self.search_word

class Post(models.Model):
	company=models.ForeignKey(Company, on_delete=models.CASCADE,help_text='所属公司')
	post_name=models.CharField(max_length=255,help_text='职位名称')
	salary=models.CharField(max_length=255,help_text='薪资')
	work_place=models.CharField(max_length=255,help_text='工作地点')
	experience_require=models.CharField(max_length=255,help_text='工作经验要求')
	graduate_require=models.CharField(max_length=255,help_text='毕业院校要求')
	recruit_number=models.CharField(max_length=255,help_text='招聘人数')
	post_info=models.TextField(help_text='岗位介绍')
	publish_datetime=models.DateTimeField(auto_now=True,help_text='发布时间')
	class Meta:
		db_table='post'
		ordering=['publish_datetime']
	def __str__(self):
		return self.post_name

class PostTag(models.Model):
	post=models.ForeignKey(Post, on_delete=models.CASCADE,help_text='所属岗位')
	tag_name=models.CharField(max_length=255,help_text='标签名称')
	class Meta:
		db_table='post_tag'
	def __str__(self):
		return self.tag_name